from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# Grocery List Schemas
class GroceryListBase(BaseModel):
    """Base schema for grocery list"""
    name: str = Field(..., min_length=1, max_length=200, description="List name")
    description: Optional[str] = Field(None, max_length=1000, description="List description")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()

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
    owner: str
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
