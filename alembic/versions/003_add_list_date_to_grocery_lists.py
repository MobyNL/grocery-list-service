"""Add list_date column to grocery lists

Revision ID: 003_add_list_date
Revises: 002_add_is_closed
Create Date: 2026-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_list_date'
down_revision: Union[str, None] = '002_add_is_closed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add list_date column to grocery_lists table
    op.add_column('grocery_lists', sa.Column('list_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove list_date column from grocery_lists table
    op.drop_column('grocery_lists', 'list_date')
