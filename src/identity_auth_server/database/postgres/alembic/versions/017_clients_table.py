"""Add clients table.

Revision ID: 017_clients_table
Revises: 016_approved_to_boolean
Create Date: 2025-11-20 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "017_clients_table"
down_revision = "016_approved_to_boolean"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration to create the clients table."""
    # Create clients table
    op.create_table(
        "clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("client_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("secret", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Create indexes
    op.create_index("idx_clients_client_id", "clients", ["client_id"], unique=True)
    op.create_index("idx_clients_created_at", "clients", ["created_at"])


def downgrade() -> None:
    """Revert the migration by dropping the clients table."""
    # Drop indexes
    op.drop_index("idx_clients_created_at")
    op.drop_index("idx_clients_client_id")

    # Drop table
    op.drop_table("clients")
