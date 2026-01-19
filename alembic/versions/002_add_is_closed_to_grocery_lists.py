"""Add is_closed column to grocery lists

Revision ID: 002_add_is_closed
Revises: 001_add_store_column
Create Date: 2026-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_is_closed'
down_revision: Union[str, None] = '001_add_store_column'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_closed column to grocery_lists table
    op.add_column('grocery_lists', sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove is_closed column from grocery_lists table
    op.drop_column('grocery_lists', 'is_closed')
