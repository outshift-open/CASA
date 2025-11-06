"""Add source_app_responses table.

Revision ID: 006_source_app_responses
Revises: 005_allow_nullable_llm_refs_in_mcp_tool_calls
Create Date: 2025-10-09 00:10:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "006_source_app_responses"
down_revision = "005_nullable_llm_refs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the source_app_responses table."""
    op.create_table(
        "source_app_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "source_app_call_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_app_calls.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("output", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )

    op.create_index("idx_source_app_responses_token", "source_app_responses", ["token"])
    op.create_index("idx_source_app_responses_source_app_call_id", "source_app_responses", ["source_app_call_id"])
    op.create_index("idx_source_app_responses_created_at", "source_app_responses", ["created_at"])


def downgrade() -> None:
    """Drop the source_app_responses table."""
    op.drop_index("idx_source_app_responses_created_at", table_name="source_app_responses")
    op.drop_index("idx_source_app_responses_source_app_call_id", table_name="source_app_responses")
    op.drop_index("idx_source_app_responses_token", table_name="source_app_responses")
    op.drop_table("source_app_responses")
