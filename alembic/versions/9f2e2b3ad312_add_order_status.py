"""add order status

Revision ID: 9f2e2b3ad312
Revises: d57b351146e9
Create Date: 2026-09-08 16:30:31.002187

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9f2e2b3ad312"
down_revision: Union[str, Sequence[str], None] = "d57b351146e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

status_enum = postgresql.ENUM(
    "PENDING", "PAID", "SHIPPED", "CANCELED", "COMPLETED", name="orderstatus"
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        status_enum.create(bind, checkfirst=True)
    with op.batch_alter_table("orders") as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                status_enum,
                nullable=True,
                server_default="PENDING",
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_column("status")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        status_enum.drop(bind, checkfirst=True)
