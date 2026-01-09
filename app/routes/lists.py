from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..crud import (
    create_grocery_list,
    delete_grocery_list,
    get_grocery_list,
    get_grocery_lists_by_owner,
    update_grocery_list,
)
from ..database import get_db
from ..schemas import GroceryList, GroceryListCreate, GroceryListUpdate, GroceryListWithItems

router = APIRouter(prefix="/lists", tags=["Grocery Lists"])


@router.get("/", response_model=List[GroceryList])
def get_my_grocery_lists(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all grocery lists for the current user"""
    username = current_user["username"]
    lists = get_grocery_lists_by_owner(db, owner=username, skip=skip, limit=limit)
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
