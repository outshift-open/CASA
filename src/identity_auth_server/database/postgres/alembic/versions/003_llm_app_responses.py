"""Add llm_app_responses table.

Revision ID: 003_llm_app_responses
Revises: 002_llm_app_calls
Create Date: 2025-10-07 00:05:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003_llm_app_responses"
down_revision = "002_llm_app_calls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the llm_app_responses table."""
    op.create_table(
        "llm_app_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "llm_app_call_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("llm_app_calls.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("tool_calls", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )

    op.create_index("idx_llm_app_responses_token", "llm_app_responses", ["token"])
    op.create_index("idx_llm_app_responses_llm_app_call_id", "llm_app_responses", ["llm_app_call_id"])
    op.create_index("idx_llm_app_responses_created_at", "llm_app_responses", ["created_at"])


def downgrade() -> None:
    """Drop the llm_app_responses table."""
    op.drop_index("idx_llm_app_responses_created_at", table_name="llm_app_responses")
    op.drop_index("idx_llm_app_responses_llm_app_call_id", table_name="llm_app_responses")
    op.drop_index("idx_llm_app_responses_token", table_name="llm_app_responses")

    op.drop_table("llm_app_responses")
