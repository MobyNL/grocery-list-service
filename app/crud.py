from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .models import GroceryItemORM, GroceryListORM
from .schemas import (
    GroceryItemCreate,
    GroceryItemUpdate,
    GroceryListCreate,
    GroceryListUpdate,
)


# Grocery List CRUD operations
def get_popular_stores(db: Session, limit: int = 5) -> list[str]:
    """Get most commonly used stores from grocery items"""
    results = (
        db.query(GroceryItemORM.store, func.count(GroceryItemORM.store).label('count'))
        .filter(GroceryItemORM.store.isnot(None))
        .filter(GroceryItemORM.store != '')
        .group_by(GroceryItemORM.store)
        .order_by(func.count(GroceryItemORM.store).desc())
        .limit(limit)
        .all()
    )
    return [store for store, count in results]


def get_grocery_list(db: Session, list_id: int) -> Optional[GroceryListORM]:
    """Get a single grocery list by ID"""
    return db.query(GroceryListORM).options(joinedload(GroceryListORM.items)).filter(GroceryListORM.id == list_id).first()


def get_grocery_lists_by_owner(
    db: Session, owner: str, skip: int = 0, limit: int = 100, include_closed: bool = False
) -> list[GroceryListORM]:
    """Get all grocery lists for a specific owner"""
    query = db.query(GroceryListORM).options(joinedload(GroceryListORM.items)).filter(GroceryListORM.owner == owner)

    if not include_closed:
        query = query.filter(GroceryListORM.is_closed == False)

    return (
        query
        .order_by(GroceryListORM.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_grocery_list(
    db: Session, grocery_list: GroceryListCreate, owner: str
) -> GroceryListORM:
    """Create a new grocery list"""
    # Auto-generate name if not provided
    name = grocery_list.name
    if not name:
        parts = []
        if grocery_list.list_date:
            parts.append(grocery_list.list_date.strftime('%Y-%m-%d'))
        if grocery_list.stores:
            parts.append(grocery_list.stores)
        name = ' - '.join(parts) if parts else f"List {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    db_list = GroceryListORM(
        name=name,
        stores=grocery_list.stores,
        description=grocery_list.description,
        owner=owner,
        list_date=grocery_list.list_date,
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


def migrate_items_to_list(
    db: Session, item_ids: list[int], target_list_id: int
) -> list[GroceryItemORM]:
    """Migrate items to a different list"""
    items = db.query(GroceryItemORM).filter(GroceryItemORM.id.in_(item_ids)).all()

    for item in items:
        item.grocery_list_id = target_list_id
        item.purchased = False  # Reset purchased status when moving to new list

    db.commit()

    for item in items:
        db.refresh(item)

    return items


def get_items_by_ids(db: Session, item_ids: list[int]) -> list[GroceryItemORM]:
    """Get multiple items by their IDs"""
    return db.query(GroceryItemORM).filter(GroceryItemORM.id.in_(item_ids)).all()
