from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class GroceryListORM(Base):
    """Grocery list model - users can have multiple lists"""
    __tablename__ = "grocery_lists"
    __table_args__ = {"schema": "grocery_service"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    owner = Column(String(100), nullable=False, index=True)  # Username from user-service
    list_date = Column(DateTime, nullable=True)  # Date for the grocery list (e.g., when shopping is planned)
    is_closed = Column(Boolean, default=False, nullable=False)  # Whether the list is closed/archived
    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)

    # Relationship to items
    items = relationship("GroceryItemORM", back_populates="grocery_list", cascade="all, delete-orphan")


class GroceryItemORM(Base):
    """Individual grocery item within a list"""
    __tablename__ = "grocery_items"
    __table_args__ = {"schema": "grocery_service"}

    id = Column(Integer, primary_key=True, index=True)
    grocery_list_id = Column(Integer, ForeignKey("grocery_service.grocery_lists.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    quantity = Column(Float, default=1.0, nullable=False)
    unit = Column(String(50), nullable=True)  # e.g., "kg", "lbs", "pieces", "bottles"
    category = Column(String(100), nullable=True)  # e.g., "Produce", "Dairy", "Meat"
    store = Column(String(100), nullable=True)  # e.g., "Walmart", "Target", "Whole Foods"
    notes = Column(String(500), nullable=True)
    purchased = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)

    # Relationship to parent list
    grocery_list = relationship("GroceryListORM", back_populates="items")
