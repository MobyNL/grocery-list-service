from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# Grocery List Schemas
class GroceryListBase(BaseModel):
    """Base schema for grocery list"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="List name (optional - auto-generated if not provided)")
    stores: Optional[str] = Field(None, max_length=500, description="Comma-separated list of stores")
    description: Optional[str] = Field(None, max_length=1000, description="List description")
    list_date: Optional[datetime] = Field(None, description="Date for the grocery list")
    is_closed: bool = Field(default=False, description="Whether the list is closed/archived")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty or whitespace only')
            return v.strip()
        return v

    @field_validator('stores')
    @classmethod
    def stores_strip(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip() if v.strip() else None
        return None

    @field_validator('description')
    @classmethod
    def description_strip(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip() if v.strip() else None
        return None


class GroceryListCreate(GroceryListBase):
    """Schema for creating a grocery list"""
    pass


class GroceryListUpdate(BaseModel):
    """Schema for updating a grocery list"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    list_date: Optional[datetime] = Field(None, description="Date for the grocery list")
    is_closed: Optional[bool] = Field(None, description="Whether the list is closed/archived")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty or whitespace only')
            return v.strip()
        return v


class GroceryList(GroceryListBase):
    """Schema for returning a grocery list"""
    id: int
    name: str  # Always present in response (auto-generated if not provided)
    stores: Optional[str]
    owner: str
    list_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Grocery Item Schemas
class GroceryItemBase(BaseModel):
    """Base schema for grocery item"""
    name: str = Field(..., min_length=1, max_length=200, description="Item name")
    quantity: float = Field(default=1.0, gt=0, description="Quantity")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    store: Optional[str] = Field(None, max_length=100, description="Store name")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    purchased: bool = Field(default=False, description="Whether item is purchased")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()

    @field_validator('unit', 'category', 'store', 'notes')
    @classmethod
    def strip_optional_fields(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip() if v.strip() else None
        return None


class GroceryItemCreate(GroceryItemBase):
    """Schema for creating a grocery item"""
    pass


class GroceryItemUpdate(BaseModel):
    """Schema for updating a grocery item"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    store: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    purchased: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty or whitespace only')
            return v.strip()
        return v


class GroceryItem(GroceryItemBase):
    """Schema for returning a grocery item"""
    id: int
    grocery_list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GroceryListWithItems(GroceryList):
    """Schema for returning a grocery list with its items"""
    items: list[GroceryItem] = []

    class Config:
        from_attributes = True


# Item Migration Schemas
class ItemMigrationRequest(BaseModel):
    """Schema for migrating items to another list"""
    item_ids: list[int] = Field(..., description="List of item IDs to migrate")
    target_list_id: Optional[int] = Field(None, description="ID of target list (if migrating to existing list)")
    new_list_name: Optional[str] = Field(None, description="Name for new list (if creating new list)")
    new_list_description: Optional[str] = Field(None, description="Description for new list (if creating new list)")

    @field_validator('item_ids')
    @classmethod
    def validate_item_ids(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError('At least one item ID must be provided')
        return v


class CloseListRequest(BaseModel):
    """Schema for closing a list with optional item migration"""
    migration: Optional[ItemMigrationRequest] = Field(None, description="Optional migration of unpurchased items")
