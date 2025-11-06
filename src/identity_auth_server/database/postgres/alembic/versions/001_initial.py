"""Initial migration.

Revision ID: 001_initial
Revises:
Create Date: 2025-10-06 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the initial migration."""
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create source_app_calls table
    op.create_table(
        "source_app_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )

    # Create indexes
    op.create_index("idx_source_app_calls_token", "source_app_calls", ["token"])
    op.create_index("idx_source_app_calls_created_at", "source_app_calls", ["created_at"])


def downgrade() -> None:
    """Revert the initial migration."""
    # Drop indexes
    op.drop_index("idx_source_app_calls_created_at")
    op.drop_index("idx_source_app_calls_token")

    # Drop table
    op.drop_table("source_app_calls")

    # Note: We don't drop the UUID extension as it might be used by other things
