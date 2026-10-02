"""enforce non negative payment amount

Revision ID: b9a13486c044
Revises: 5324af2867a8
Create Date: 2026-10-02

"""

from typing import Sequence, Union

from alembic import op


revision: str = "b9a13486c044"
down_revision: Union[str, None] = "5324af2867a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_payments_amount_non_negative",
        "payments",
        "amount >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_payments_amount_non_negative",
        "payments",
        type_="check",
    )
