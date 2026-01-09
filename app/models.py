from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class GroceryListORM(Base):
    """Grocery list model - users can have multiple lists"""
    __tablename__ = "grocery_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    owner = Column(String(100), nullable=False, index=True)  # Username from user-service
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to items
    items = relationship("GroceryItemORM", back_populates="grocery_list", cascade="all, delete-orphan")


class GroceryItemORM(Base):
    """Individual grocery item within a list"""
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    grocery_list_id = Column(Integer, ForeignKey("grocery_lists.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    quantity = Column(Float, default=1.0, nullable=False)
    unit = Column(String(50), nullable=True)  # e.g., "kg", "lbs", "pieces", "bottles"
    category = Column(String(100), nullable=True)  # e.g., "Produce", "Dairy", "Meat"
    store = Column(String(100), nullable=True)  # e.g., "Walmart", "Target", "Whole Foods"
    notes = Column(String(500), nullable=True)
    purchased = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to parent list
    grocery_list = relationship("GroceryListORM", back_populates="items")
