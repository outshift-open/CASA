"""Increase token length for JWT compatibility.

Revision ID: 013_increase_token_length
Revises: 012_add_blocked_by_type_enum
Create Date: 2025-11-08 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "013_increase_token_length"
down_revision = "012_add_blocked_by_type_enum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Increase token column length to accommodate JWTs."""
    # Increase token length in source_app_call_sessions from 255 to 2048
    op.alter_column(
        "source_app_call_sessions",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Revert token column length back to original size."""
    op.alter_column(
        "source_app_call_sessions",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
