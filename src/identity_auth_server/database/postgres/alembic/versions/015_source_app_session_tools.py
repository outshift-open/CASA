"""Create source_app_call_session_tools table.

Revision ID: 015_source_app_call_session_tools
Revises: 014_increase_more_token_lengths
Create Date: 2025-11-12 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "015_source_app_session_tools"
down_revision = "014_increase_more_token_lengths"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create source_app_call_session_tools table for tracking approved tools per session."""
    op.create_table(
        "source_app_call_session_tools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_app_call_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool", sa.String(), nullable=False),
        sa.Column("approved", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["source_app_call_session_id"], ["source_app_call_sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("source_app_call_session_id", "tool", name="uq_source_app_call_session_tool"),
    )
    op.create_index(
        "idx_source_app_call_session_tools_session_id",
        "source_app_call_session_tools",
        ["source_app_call_session_id"],
    )
    op.create_index(
        "idx_source_app_call_session_tools_tool",
        "source_app_call_session_tools",
        ["tool"],
    )


def downgrade() -> None:
    """Drop source_app_call_session_tools table and indexes."""
    op.drop_index("idx_source_app_call_session_tools_tool", table_name="source_app_call_session_tools")
    op.drop_index("idx_source_app_call_session_tools_session_id", table_name="source_app_call_session_tools")
    op.drop_table("source_app_call_session_tools")
