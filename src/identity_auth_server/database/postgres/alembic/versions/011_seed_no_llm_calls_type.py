"""Seed no_tool_calls_made_by_llm blocked_by_type record.

Revision ID: 011_seed_no_tool_calls_type
Revises: 010_session_tables
Create Date: 2025-11-05 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "011_seed_no_llm_calls_type"
down_revision = "010_session_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert blocked_by_type record for no_llm_calls_made_by_app."""
    blocked_by_types_table = sa.table(
        "blocked_by_types",
        sa.column("name", sa.String(length=255)),
        sa.column("description", sa.Text()),
    )

    op.bulk_insert(
        blocked_by_types_table,
        [
            {
                "name": "no_llm_calls_made_by_app",
                "description": "The MCP Server Tool was requested before any LLM calls were made",
            },
        ],
    )


def downgrade() -> None:
    """Remove the seeded no_llm_calls_made_by_app blocked_by_type record."""
    op.execute(
        sa.text("DELETE FROM blocked_by_types WHERE name = :name"),
        {"name": "no_llm_calls_made_by_app"},
    )
