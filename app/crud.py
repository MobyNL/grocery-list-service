from typing import Optional

from sqlalchemy.orm import Session

from .models import GroceryItemORM, GroceryListORM
from .schemas import (
    GroceryItemCreate,
    GroceryItemUpdate,
    GroceryListCreate,
    GroceryListUpdate,
)


# Grocery List CRUD operations
def get_grocery_list(db: Session, list_id: int) -> Optional[GroceryListORM]:
    """Get a single grocery list by ID"""
    return db.query(GroceryListORM).filter(GroceryListORM.id == list_id).first()


def get_grocery_lists_by_owner(
    db: Session, owner: str, skip: int = 0, limit: int = 100
) -> list[GroceryListORM]:
    """Get all grocery lists for a specific owner"""
    return (
        db.query(GroceryListORM)
        .filter(GroceryListORM.owner == owner)
        .order_by(GroceryListORM.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_grocery_list(
    db: Session, grocery_list: GroceryListCreate, owner: str
) -> GroceryListORM:
    """Create a new grocery list"""
    db_list = GroceryListORM(
        name=grocery_list.name,
        description=grocery_list.description,
        owner=owner,
    )
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


def update_grocery_list(
    db: Session, list_id: int, grocery_list: GroceryListUpdate
) -> Optional[GroceryListORM]:
    """Update an existing grocery list"""
    db_list = get_grocery_list(db, list_id)
    if db_list is None:
        return None

    update_data = grocery_list.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_list, key, value)

    db.commit()
    db.refresh(db_list)
    return db_list


def delete_grocery_list(db: Session, list_id: int) -> bool:
    """Delete a grocery list and all its items"""
    db_list = get_grocery_list(db, list_id)
    if db_list is None:
        return False

    db.delete(db_list)
    db.commit()
    return True


# Grocery Item CRUD operations
def get_grocery_item(db: Session, item_id: int) -> Optional[GroceryItemORM]:
    """Get a single grocery item by ID"""
    return db.query(GroceryItemORM).filter(GroceryItemORM.id == item_id).first()


def get_grocery_items_by_list(
    db: Session, list_id: int, skip: int = 0, limit: int = 100
) -> list[GroceryItemORM]:
    """Get all items for a specific grocery list"""
    return (
        db.query(GroceryItemORM)
        .filter(GroceryItemORM.grocery_list_id == list_id)
        .order_by(GroceryItemORM.purchased, GroceryItemORM.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_grocery_item(
    db: Session, item: GroceryItemCreate, list_id: int
) -> GroceryItemORM:
    """Create a new grocery item"""
    db_item = GroceryItemORM(
        grocery_list_id=list_id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        category=item.category,
        store=item.store,
        notes=item.notes,
        purchased=item.purchased,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_grocery_item(
    db: Session, item_id: int, item: GroceryItemUpdate
) -> Optional[GroceryItemORM]:
    """Update an existing grocery item"""
    db_item = get_grocery_item(db, item_id)
    if db_item is None:
        return None

    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


def delete_grocery_item(db: Session, item_id: int) -> bool:
    """Delete a grocery item"""
    db_item = get_grocery_item(db, item_id)
    if db_item is None:
        return False

    db.delete(db_item)
    db.commit()
    return True


def mark_item_purchased(db: Session, item_id: int, purchased: bool) -> Optional[GroceryItemORM]:
    """Mark an item as purchased or not purchased"""
    db_item = get_grocery_item(db, item_id)
    if db_item is None:
        return None

    db_item.purchased = purchased
    db.commit()
    db.refresh(db_item)
    return db_item
