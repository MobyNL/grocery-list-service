"""Add store column to grocery items

Revision ID: 001_add_store_column
Revises:
Create Date: 2026-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_store_column'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add store column to grocery_items table
    op.add_column('grocery_items', sa.Column('store', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Remove store column from grocery_items table
    op.drop_column('grocery_items', 'store')
