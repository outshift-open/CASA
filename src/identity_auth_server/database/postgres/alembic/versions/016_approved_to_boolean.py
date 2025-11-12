"""Change approved column to boolean in source_app_call_session_tools.

Revision ID: 016_approved_to_boolean
Revises: 015_source_app_call_session_tools
Create Date: 2025-11-12 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "016_approved_to_boolean"
down_revision = "015_source_app_session_tools"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Change approved column from String to Boolean."""
    # First, add a new temporary boolean column
    op.add_column(
        "source_app_call_session_tools",
        sa.Column("approved_bool", sa.Boolean(), nullable=True),
    )

    # Convert existing string values to boolean
    # Assuming 'true', 'True', '1', 'yes', 'Yes' are truthy
    op.execute("""
        UPDATE source_app_call_session_tools
        SET approved_bool = CASE
            WHEN LOWER(approved) IN ('true', '1', 'yes') THEN TRUE
            ELSE FALSE
        END
    """)

    # Make the new column non-nullable
    op.alter_column(
        "source_app_call_session_tools",
        "approved_bool",
        nullable=False,
    )

    # Drop the old column
    op.drop_column("source_app_call_session_tools", "approved")

    # Rename the new column to approved
    op.alter_column(
        "source_app_call_session_tools",
        "approved_bool",
        new_column_name="approved",
    )


def downgrade() -> None:
    """Revert approved column from Boolean back to String."""
    # Add a temporary string column
    op.add_column(
        "source_app_call_session_tools",
        sa.Column("approved_str", sa.String(), nullable=True),
    )

    # Convert boolean values to string
    op.execute("""
        UPDATE source_app_call_session_tools
        SET approved_str = CASE
            WHEN approved = TRUE THEN 'true'
            ELSE 'false'
        END
    """)

    # Make the new column non-nullable
    op.alter_column(
        "source_app_call_session_tools",
        "approved_str",
        nullable=False,
    )

    # Drop the boolean column
    op.drop_column("source_app_call_session_tools", "approved")

    # Rename the string column to approved
    op.alter_column(
        "source_app_call_session_tools",
        "approved_str",
        new_column_name="approved",
    )
