"""Allow nullable LLM references in MCP app tool calls.

Revision ID: 005_nullable_llm_refs
Revises: 004_mcp_app_tool_calls
Create Date: 2025-10-08 00:00:00.000000
"""

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "005_nullable_llm_refs"
down_revision = "004_mcp_app_tool_calls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make LLM foreign keys nullable."""
    op.alter_column(
        "mcp_app_tool_calls",
        "llm_app_call_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
        existing_nullable=False,
    )
    op.alter_column(
        "mcp_app_tool_calls",
        "llm_app_response_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
        existing_nullable=False,
    )


def downgrade() -> None:
    """Revert LLM foreign keys to non-nullable."""
    op.alter_column(
        "mcp_app_tool_calls",
        "llm_app_response_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
        existing_nullable=True,
    )
    op.alter_column(
        "mcp_app_tool_calls",
        "llm_app_call_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
        existing_nullable=True,
    )
