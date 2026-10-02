"""change payment amount to decimal

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "74c9c3dbd3d2"
down_revision: Union[str, None] = "cf6b8d296c13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "payments",
        "amount",
        existing_type=sa.Integer(),
        type_=sa.Numeric(18, 2),
        existing_nullable=False,
        postgresql_using="amount::numeric(18,2)",
    )


def downgrade() -> None:
    op.alter_column(
        "payments",
        "amount",
        existing_type=sa.Numeric(18, 2),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="amount::integer",
    )
