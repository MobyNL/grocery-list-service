"""add_stores_to_list_make_name_optional

Revision ID: 37f563616fc7
Revises: 7ddb21fdb6d5
Create Date: 2026-01-21 21:08:31.439011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '37f563616fc7'
down_revision: Union[str, None] = '7ddb21fdb6d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Only modify grocery_lists table in grocery_service schema
    op.add_column('grocery_lists', sa.Column('stores', sa.String(length=500), nullable=True), schema='grocery_service')
    op.alter_column('grocery_lists', 'name',
               existing_type=sa.VARCHAR(length=200),
               nullable=True,
               schema='grocery_service')


def downgrade() -> None:
    # Revert changes to grocery_lists table
    op.alter_column('grocery_lists', 'name',
               existing_type=sa.VARCHAR(length=200),
               nullable=False,
               schema='grocery_service')
    op.drop_column('grocery_lists', 'stores', schema='grocery_service')
