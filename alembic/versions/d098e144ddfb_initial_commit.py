"""Initial commit

Revision ID: d098e144ddfb
Revises: 
Create Date: 2025-01-10 16:44:14.513390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision: str = 'd098e144ddfb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'pokemons',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('xp', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('pokemon_url', sa.String(), nullable=True),
        sa.Column('abilities', JSON(), nullable=True),
        sa.Column('stats', JSON(), nullable=True),
        sa.Column('types', JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')  # Make the name column unique
    )


def downgrade() -> None:
    op.drop_table('pokemons')
