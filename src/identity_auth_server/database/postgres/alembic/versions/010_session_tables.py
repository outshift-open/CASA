"""Create session tracking tables.

Revision ID: 010_session_tables
Revises: 009_seed_blocked_by_types
Create Date: 2025-10-15 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "010_session_tables"
down_revision = "009_seed_blocked_by_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables for session token management."""
    op.create_table(
        "source_app_call_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("token", name="uq_source_app_call_sessions_token"),
    )
    op.create_index("idx_source_app_call_sessions_token", "source_app_call_sessions", ["token"])
    op.create_index("idx_source_app_call_sessions_created_at", "source_app_call_sessions", ["created_at"])

    op.create_table(
        "llm_app_call_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_app_call_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["source_app_call_session_id"], ["source_app_call_sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token", name="uq_llm_app_call_sessions_token"),
    )
    op.create_index(
        "idx_llm_app_call_sessions_source_app_call_session_id",
        "llm_app_call_sessions",
        ["source_app_call_session_id"],
    )
    op.create_index("idx_llm_app_call_sessions_token", "llm_app_call_sessions", ["token"])

    op.create_table(
        "mcp_app_call_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_app_call_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("llm_app_call_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["source_app_call_session_id"], ["source_app_call_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["llm_app_call_session_id"], ["llm_app_call_sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token", name="uq_mcp_app_call_sessions_token"),
    )
    op.create_index(
        "idx_mcp_app_call_sessions_source_app_call_session_id",
        "mcp_app_call_sessions",
        ["source_app_call_session_id"],
    )
    op.create_index(
        "idx_mcp_app_call_sessions_llm_app_call_session_id",
        "mcp_app_call_sessions",
        ["llm_app_call_session_id"],
    )
    op.create_index("idx_mcp_app_call_sessions_token", "mcp_app_call_sessions", ["token"])


def downgrade() -> None:
    """Drop session tables and indexes."""
    op.drop_index("idx_mcp_app_call_sessions_token", table_name="mcp_app_call_sessions")
    op.drop_index("idx_mcp_app_call_sessions_llm_app_call_session_id", table_name="mcp_app_call_sessions")
    op.drop_index("idx_mcp_app_call_sessions_source_app_call_session_id", table_name="mcp_app_call_sessions")
    op.drop_table("mcp_app_call_sessions")

    op.drop_index("idx_llm_app_call_sessions_token", table_name="llm_app_call_sessions")
    op.drop_index(
        "idx_llm_app_call_sessions_source_app_call_session_id",
        table_name="llm_app_call_sessions",
    )
    op.drop_table("llm_app_call_sessions")

    op.drop_index("idx_source_app_call_sessions_created_at", table_name="source_app_call_sessions")
    op.drop_index("idx_source_app_call_sessions_token", table_name="source_app_call_sessions")
    op.drop_table("source_app_call_sessions")
