"""add non negative payment amount constraint

Revision ID: 5324af2867a8
Revises: 74c9c3dbd3d2
Create Date: 2026-10-02 11:56:23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5324af2867a8'
down_revision: Union[str, None] = '74c9c3dbd3d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
