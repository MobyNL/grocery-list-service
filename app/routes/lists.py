from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..crud import (
    create_grocery_list,
    delete_grocery_list,
    get_grocery_list,
    get_grocery_lists_by_owner,
    get_items_by_ids,
    migrate_items_to_list,
    update_grocery_list,
)
from ..database import get_db
from ..schemas import (
    CloseListRequest,
    GroceryList,
    GroceryListCreate,
    GroceryListUpdate,
    GroceryListWithItems,
    ItemMigrationRequest,
)

router = APIRouter(prefix="/lists", tags=["Grocery Lists"])


@router.get("/", response_model=List[GroceryList])
def get_my_grocery_lists(
    skip: int = 0,
    limit: int = 100,
    include_closed: bool = False,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all grocery lists for the current user"""
    username = current_user["username"]
    lists = get_grocery_lists_by_owner(db, owner=username, skip=skip, limit=limit, include_closed=include_closed)
    return lists


@router.get("/{list_id}", response_model=GroceryListWithItems)
def get_grocery_list_by_id(
    list_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific grocery list with all its items"""
    grocery_list = get_grocery_list(db, list_id)
    if grocery_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery list not found"
        )

    # Check ownership
    if grocery_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this list"
        )

    return grocery_list


@router.post("/", response_model=GroceryList, status_code=status.HTTP_201_CREATED)
def create_new_grocery_list(
    grocery_list: GroceryListCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new grocery list"""
    username = current_user["username"]
    return create_grocery_list(db, grocery_list, owner=username)


@router.put("/{list_id}", response_model=GroceryList)
def update_grocery_list_by_id(
    list_id: int,
    grocery_list: GroceryListUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a grocery list"""
    db_list = get_grocery_list(db, list_id)
    if db_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery list not found"
        )

    # Check ownership
    if db_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this list"
        )

    updated_list = update_grocery_list(db, list_id, grocery_list)
    return updated_list


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grocery_list_by_id(
    list_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a grocery list and all its items"""
    db_list = get_grocery_list(db, list_id)
    if db_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery list not found"
        )

    # Check ownership
    if db_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this list"
        )

    delete_grocery_list(db, list_id)
    return None


@router.post("/{list_id}/close", response_model=GroceryList)
def close_grocery_list(
    list_id: int,
    close_request: CloseListRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Close a grocery list with optional item migration"""
    db_list = get_grocery_list(db, list_id)
    if db_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery list not found"
        )

    # Check ownership
    if db_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this list"
        )

    # Handle migration if provided
    if close_request.migration:
        migration = close_request.migration

        # Verify all items belong to this list
        items = get_items_by_ids(db, migration.item_ids)
        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid items found to migrate"
            )

        for item in items:
            if item.grocery_list_id != list_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item {item.id} does not belong to this list"
                )

        # Create new list or use existing one
        if migration.new_list_name:
            # Create new list
            new_list = create_grocery_list(
                db,
                GroceryListCreate(
                    name=migration.new_list_name,
                    description=migration.new_list_description
                ),
                owner=current_user["username"]
            )
            target_list_id = new_list.id
        elif migration.target_list_id:
            # Verify target list exists and belongs to user
            target_list = get_grocery_list(db, migration.target_list_id)
            if target_list is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target list not found"
                )
            if target_list.owner != current_user["username"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access target list"
                )
            target_list_id = migration.target_list_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either new_list_name or target_list_id must be provided for migration"
            )

        # Migrate items
        migrate_items_to_list(db, migration.item_ids, target_list_id)

    # Close the list
    updated_list = update_grocery_list(db, list_id, GroceryListUpdate(is_closed=True))
    return updated_list


@router.post("/{list_id}/migrate-items", response_model=GroceryListWithItems)
def migrate_list_items(
    list_id: int,
    migration: ItemMigrationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Migrate items from one list to another (or new) list"""
    # Verify source list exists and belongs to user
    source_list = get_grocery_list(db, list_id)
    if source_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source list not found"
        )

    if source_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access source list"
        )

    # Verify all items belong to source list
    items = get_items_by_ids(db, migration.item_ids)
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid items found to migrate"
        )

    for item in items:
        if item.grocery_list_id != list_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item {item.id} does not belong to source list"
            )

    # Create new list or use existing one
    if migration.new_list_name:
        # Create new list
        target_list = create_grocery_list(
            db,
            GroceryListCreate(
                name=migration.new_list_name,
                description=migration.new_list_description
            ),
            owner=current_user["username"]
        )
        target_list_id = target_list.id
    elif migration.target_list_id:
        # Verify target list exists and belongs to user
        target_list = get_grocery_list(db, migration.target_list_id)
        if target_list is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target list not found"
            )
        if target_list.owner != current_user["username"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access target list"
            )
        target_list_id = migration.target_list_id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either new_list_name or target_list_id must be provided"
        )

    # Migrate items
    migrate_items_to_list(db, migration.item_ids, target_list_id)

    # Return the updated target list with items
    updated_target_list = get_grocery_list(db, target_list_id)
    return updated_target_list
