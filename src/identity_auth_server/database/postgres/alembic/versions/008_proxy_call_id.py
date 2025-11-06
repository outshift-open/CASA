"""Add proxy_call_id columns to LLM app tables.

Revision ID: 008_proxy_call_id
Revises: 007_unique_token_constraint
Create Date: 2025-10-09 12:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "008_proxy_call_id"
down_revision = "007_unique_token_constraint"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add proxy_call_id columns and backfill existing data."""
    op.add_column("llm_app_calls", sa.Column("proxy_call_id", sa.String(length=255), nullable=True))
    op.execute("UPDATE llm_app_calls SET proxy_call_id = id::text")
    op.alter_column(
        "llm_app_calls",
        "proxy_call_id",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.create_unique_constraint("uq_llm_app_calls_proxy_call_id", "llm_app_calls", ["proxy_call_id"])

    op.add_column("llm_app_responses", sa.Column("proxy_call_id", sa.String(length=255), nullable=True))
    op.execute(
        """
        UPDATE llm_app_responses AS r
        SET proxy_call_id = c.proxy_call_id
        FROM llm_app_calls AS c
        WHERE r.llm_app_call_id = c.id
        """
    )
    op.alter_column(
        "llm_app_responses",
        "proxy_call_id",
        existing_type=sa.String(length=255),
        nullable=False,
    )


def downgrade() -> None:
    """Remove proxy_call_id columns and related constraints."""
    op.drop_column("llm_app_responses", "proxy_call_id")
    op.drop_constraint("uq_llm_app_calls_proxy_call_id", "llm_app_calls", type_="unique")
    op.drop_column("llm_app_calls", "proxy_call_id")
