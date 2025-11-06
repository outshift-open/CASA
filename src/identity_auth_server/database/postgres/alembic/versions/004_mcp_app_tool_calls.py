"""Add mcp_app_tool_calls and blocked_by_types tables.

Revision ID: 004_mcp_app_tool_calls
Revises: 003_llm_app_responses
Create Date: 2025-10-07 00:10:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "004_mcp_app_tool_calls"
down_revision = "003_llm_app_responses"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create blocked_by_types and mcp_app_tool_calls tables."""
    op.create_table(
        "blocked_by_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
    )

    op.create_table(
        "mcp_app_tool_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "source_app_call_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_app_calls.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "llm_app_call_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("llm_app_calls.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "llm_app_response_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("llm_app_responses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "blocked_by_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("blocked_by_types.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("tool", sa.Text(), nullable=False),
        sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_index("idx_mcp_app_tool_calls_token", "mcp_app_tool_calls", ["token"])
    op.create_index("idx_mcp_app_tool_calls_source_app_call_id", "mcp_app_tool_calls", ["source_app_call_id"])
    op.create_index("idx_mcp_app_tool_calls_llm_app_call_id", "mcp_app_tool_calls", ["llm_app_call_id"])
    op.create_index("idx_mcp_app_tool_calls_llm_app_response_id", "mcp_app_tool_calls", ["llm_app_response_id"])
    op.create_index("idx_mcp_app_tool_calls_created_at", "mcp_app_tool_calls", ["created_at"])


def downgrade() -> None:
    """Drop mcp_app_tool_calls and blocked_by_types tables."""
    op.drop_index("idx_mcp_app_tool_calls_created_at", table_name="mcp_app_tool_calls")
    op.drop_index("idx_mcp_app_tool_calls_llm_app_response_id", table_name="mcp_app_tool_calls")
    op.drop_index("idx_mcp_app_tool_calls_llm_app_call_id", table_name="mcp_app_tool_calls")
    op.drop_index("idx_mcp_app_tool_calls_source_app_call_id", table_name="mcp_app_tool_calls")
    op.drop_index("idx_mcp_app_tool_calls_token", table_name="mcp_app_tool_calls")

    op.drop_table("mcp_app_tool_calls")
    op.drop_table("blocked_by_types")
