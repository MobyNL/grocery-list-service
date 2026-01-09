from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..crud import (
    create_grocery_item,
    delete_grocery_item,
    get_grocery_item,
    get_grocery_items_by_list,
    get_grocery_list,
    mark_item_purchased,
    update_grocery_item,
)
from ..database import get_db
from ..schemas import GroceryItem, GroceryItemCreate, GroceryItemUpdate

router = APIRouter(prefix="/items", tags=["Grocery Items"])


@router.get("/list/{list_id}", response_model=List[GroceryItem])
def get_items_for_list(
    list_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all items for a specific grocery list"""
    # Verify list exists and user owns it
    grocery_list = get_grocery_list(db, list_id)
    if grocery_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery list not found"
        )

    if grocery_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this list"
        )

    items = get_grocery_items_by_list(db, list_id, skip=skip, limit=limit)
    return items


@router.get("/{item_id}", response_model=GroceryItem)
def get_grocery_item_by_id(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific grocery item"""
    item = get_grocery_item(db, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check ownership through parent list
    grocery_list = get_grocery_list(db, item.grocery_list_id)
    if grocery_list and grocery_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this item"
        )

    return item


@router.post("/list/{list_id}", response_model=GroceryItem, status_code=status.HTTP_201_CREATED)
def create_new_grocery_item(
    list_id: int,
    item: GroceryItemCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new grocery item in a list"""
    # Verify list exists and user owns it
    grocery_list = get_grocery_list(db, list_id)
    if grocery_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grocery list not found"
        )

    if grocery_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add items to this list"
        )

    return create_grocery_item(db, item, list_id)


@router.put("/{item_id}", response_model=GroceryItem)
def update_grocery_item_by_id(
    item_id: int,
    item: GroceryItemUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a grocery item"""
    db_item = get_grocery_item(db, item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check ownership through parent list
    grocery_list = get_grocery_list(db, db_item.grocery_list_id)
    if grocery_list and grocery_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )

    updated_item = update_grocery_item(db, item_id, item)
    return updated_item


@router.patch("/{item_id}/purchased", response_model=GroceryItem)
def mark_item_as_purchased(
    item_id: int,
    purchased: bool,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark an item as purchased or not purchased"""
    db_item = get_grocery_item(db, item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check ownership through parent list
    grocery_list = get_grocery_list(db, db_item.grocery_list_id)
    if grocery_list and grocery_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )

    updated_item = mark_item_purchased(db, item_id, purchased)
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grocery_item_by_id(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a grocery item"""
    db_item = get_grocery_item(db, item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check ownership through parent list
    grocery_list = get_grocery_list(db, db_item.grocery_list_id)
    if grocery_list and grocery_list.owner != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )

    delete_grocery_item(db, item_id)
    return None
