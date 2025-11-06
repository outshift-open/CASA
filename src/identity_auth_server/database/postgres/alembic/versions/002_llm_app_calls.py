"""Add llm_app_calls table.

Revision ID: 002_llm_app_calls
Revises: 001_initial
Create Date: 2025-10-07 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002_llm_app_calls"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the llm_app_calls table."""
    op.create_table(
        "llm_app_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "source_app_call_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_app_calls.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("messages", sa.Text(), nullable=False),
        sa.Column("tools", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )

    op.create_index("idx_llm_app_calls_token", "llm_app_calls", ["token"])
    op.create_index("idx_llm_app_calls_source_app_call_id", "llm_app_calls", ["source_app_call_id"])
    op.create_index("idx_llm_app_calls_created_at", "llm_app_calls", ["created_at"])


def downgrade() -> None:
    """Drop the llm_app_calls table."""
    op.drop_index("idx_llm_app_calls_created_at", table_name="llm_app_calls")
    op.drop_index("idx_llm_app_calls_source_app_call_id", table_name="llm_app_calls")
    op.drop_index("idx_llm_app_calls_token", table_name="llm_app_calls")

    op.drop_table("llm_app_calls")
