"""bucket

Revision ID: 5f7cf16a4aae
Revises: efbff32b1201
Create Date: 2025-09-14 11:56:39.096026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f7cf16a4aae'
down_revision: Union[str, None] = 'efbff32b1201'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('games', sa.Column('bucket_header_image', sa.Text(), nullable=True), schema='steam')
    op.add_column('games', sa.Column('bucket_capsule_image', sa.Text(), nullable=True), schema='steam')
    op.add_column('games', sa.Column('bucket_capsule_imagev5', sa.Text(), nullable=True), schema='steam')
    op.add_column('games', sa.Column('bucket_background', sa.Text(), nullable=True), schema='steam')
    op.add_column('games', sa.Column('bucket_background_raw', sa.Text(), nullable=True), schema='steam')

    op.add_column('screenshots', sa.Column('bucket_path_thumbnail', sa.Text(), nullable=True), schema='steam')
    op.add_column('screenshots', sa.Column('bucket_path_full', sa.Text(), nullable=True), schema='steam')



def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('games', 'bucket_header_image', schema='steam')
    op.drop_column('games', 'bucket_capsule_image', schema='steam')
    op.drop_column('games', 'bucket_capsule_imagev5', schema='steam')
    op.drop_column('games', 'bucket_background', schema='steam')
    op.drop_column('games', 'bucket_background_raw', schema='steam')

    op.drop_column('screenshots', 'bucket_path_thumbnail', schema='steam')
    op.drop_column('screenshots', 'bucket_path_full', schema='steam')


