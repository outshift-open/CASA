"""Increase remaining token lengths for JWT compatibility.

Revision ID: 014_increase_remaining_token_lengths
Revises: 013_increase_token_length
Create Date: 2025-11-10 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "014_increase_more_token_lengths"
down_revision = "013_increase_token_length"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Increase token column length to accommodate JWTs in all remaining tables."""
    # Increase token length in llm_app_call_sessions from 255 to 2048
    op.alter_column(
        "llm_app_call_sessions",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )

    # Increase token length in mcp_app_call_sessions from 255 to 2048
    op.alter_column(
        "mcp_app_call_sessions",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )

    # Increase token length in source_app_calls from 255 to 2048
    op.alter_column(
        "source_app_calls",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )

    # Increase token length in llm_app_calls from 255 to 2048
    op.alter_column(
        "llm_app_calls",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )

    # Increase token length in llm_app_responses from 255 to 2048
    op.alter_column(
        "llm_app_responses",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )

    # Increase token length in mcp_app_tool_calls from 255 to 2048
    op.alter_column(
        "mcp_app_tool_calls",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )

    # Increase token length in source_app_responses from 255 to 2048
    op.alter_column(
        "source_app_responses",
        "token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Revert token column lengths back to original size."""
    # Revert token length in source_app_responses from 2048 to 255
    op.alter_column(
        "source_app_responses",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    # Revert token length in mcp_app_tool_calls from 2048 to 255
    op.alter_column(
        "mcp_app_tool_calls",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    # Revert token length in llm_app_responses from 2048 to 255
    op.alter_column(
        "llm_app_responses",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    # Revert token length in llm_app_calls from 2048 to 255
    op.alter_column(
        "llm_app_calls",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    # Revert token length in source_app_calls from 2048 to 255
    op.alter_column(
        "source_app_calls",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    # Revert token length in mcp_app_call_sessions from 2048 to 255
    op.alter_column(
        "mcp_app_call_sessions",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    # Revert token length in llm_app_call_sessions from 2048 to 255
    op.alter_column(
        "llm_app_call_sessions",
        "token",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
