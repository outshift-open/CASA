"""Seed additional blocked_by_types records for MCP app tool calls.

Revision ID: 009_seed_blocked_by_types
Revises: 008_proxy_call_id
Create Date: 2025-10-10 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "009_seed_blocked_by_types"
down_revision = "008_proxy_call_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert blocked_by_types records covering new MCP tool guardrails."""
    blocked_by_types_table = sa.table(
        "blocked_by_types",
        sa.column("name", sa.String(length=255)),
        sa.column("description", sa.Text()),
    )

    op.bulk_insert(
        blocked_by_types_table,
        [
            {
                "name": "modified_mcp_tool_defs",
                "description": "The LLM received modified MCP Server Tool Definitions",
            },
            {
                "name": "tool_not_selected_by_llm",
                "description": "Requested MCP Server Tool was not selected by the LLM",
            },
            {
                "name": "tool_parameters_mismatch",
                "description": "Requested MCP Server Tool Parameters are different from those selected by the LLM",
            },
            {
                "name": "tool_intent_mismatch",
                "description": "MCP Server Tool choice doesn't match the intention of original input",
            },
        ],
    )


def downgrade() -> None:
    """Remove the seeded blocked_by_types records."""
    names = [
        "modified_mcp_tool_defs",
        "tool_not_selected_by_llm",
        "tool_parameters_mismatch",
        "tool_intent_mismatch",
    ]

    for name in names:
        op.execute(sa.text("DELETE FROM blocked_by_types WHERE name = :name"), {"name": name})
