"""Add type column to blocked_by_types table.

Revision ID: 012_add_blocked_by_type_enum
Revises: 011_seed_no_llm_calls_type
Create Date: 2025-11-06 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "012_add_blocked_by_type_enum"
down_revision = "011_seed_no_llm_calls_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add type column to blocked_by_types and populate existing records."""
    # Add the type column (nullable initially)
    op.add_column(
        "blocked_by_types",
        sa.Column("type", sa.String(length=50), nullable=True),
    )

    # Update existing records with their types
    op.execute(sa.text("UPDATE blocked_by_types SET type = 'DETERMINISTIC' WHERE name = 'modified_mcp_tool_defs'"))
    op.execute(sa.text("UPDATE blocked_by_types SET type = 'DETERMINISTIC' WHERE name = 'tool_not_selected_by_llm'"))
    op.execute(sa.text("UPDATE blocked_by_types SET type = 'DETERMINISTIC' WHERE name = 'tool_parameters_mismatch'"))
    op.execute(sa.text("UPDATE blocked_by_types SET type = 'AI-POWERED' WHERE name = 'tool_intent_mismatch'"))
    op.execute(sa.text("UPDATE blocked_by_types SET type = 'DETERMINISTIC' WHERE name = 'no_llm_calls_made_by_app'"))

    # Make the column non-nullable now that all existing records have values
    op.alter_column("blocked_by_types", "type", nullable=False)


def downgrade() -> None:
    """Remove the type column from blocked_by_types."""
    op.drop_column("blocked_by_types", "type")
