"""Add unique constraint to source_app_calls token.

Revision ID: 007_unique_token_constraint
Revises: 006_source_app_responses
Create Date: 2025-10-09 00:15:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "007_unique_token_constraint"
down_revision = "006_source_app_responses"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add unique constraint to token column in source_app_calls table."""
    op.create_unique_constraint("uq_source_app_calls_token", "source_app_calls", ["token"])


def downgrade() -> None:
    """Remove unique constraint from token column in source_app_calls table."""
    op.drop_constraint("uq_source_app_calls_token", "source_app_calls", type_="unique")
