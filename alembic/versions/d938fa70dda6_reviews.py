"""reviews

Revision ID: d938fa70dda6
Revises: 5f7cf16a4aae
Create Date: 2025-09-14 12:34:29.712548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd938fa70dda6'
down_revision: Union[str, None] = '5f7cf16a4aae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('games', sa.Column('total_reviews', sa.Integer()), schema='steam')
    op.add_column('games', sa.Column('total_reviews_positive', sa.Integer()), schema='steam')
    op.add_column('games', sa.Column('total_reviews_negative', sa.Integer()), schema='steam')
    op.add_column('games', sa.Column('reviews_score', sa.Integer()), schema='steam')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('games', 'total_reviews', schema='steam')
    op.drop_column('games', 'total_reviews_positive', schema='steam')
    op.drop_column('games', 'total_reviews_negative', schema='steam')
    op.drop_column('games', 'reviews_score', schema='steam')

