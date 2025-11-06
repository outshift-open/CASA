"""Alembic-based migration runner for managing database schema changes."""

import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def get_alembic_config() -> Config:
    """Get Alembic configuration with database URL set from environment."""
    # Get the path to alembic.ini relative to the project root
    project_root = Path(__file__).parent
    alembic_ini_path = project_root / "alembic" / "alembic.ini"

    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"alembic.ini not found at {alembic_ini_path}")

    # Create Alembic config
    config = Config(str(alembic_ini_path))

    # Set database URL from environment variables
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    database_url = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    config.set_main_option("sqlalchemy.url", database_url)

    return config


def run_alembic_migrations():
    """Run database migrations using Alembic."""
    try:
        logger.info("Starting Alembic database migrations...")

        config = get_alembic_config()

        # Run migrations to head (latest)
        command.upgrade(config, "head")

        logger.info("Alembic database migrations completed successfully")
    except Exception as e:
        logger.error(f"Alembic database migration failed: {e!s}")
        raise


def check_migration_status():
    """Check current migration status."""
    try:
        config = get_alembic_config()

        # Get current revision
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from sqlalchemy import create_engine

        engine = create_engine(config.get_main_option("sqlalchemy.url"))

        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()

            script = ScriptDirectory.from_config(config)
            head_rev = script.get_current_head()

            logger.info(f"Current revision: {current_rev}")
            logger.info(f"Head revision: {head_rev}")

            if current_rev == head_rev:
                logger.info("Database is up to date")
            else:
                logger.warning("Database needs migration")

            return current_rev, head_rev

    except Exception as e:
        logger.error(f"Failed to check migration status: {e!s}")
        raise


if __name__ == "__main__":
    # Allow running this module directly for testing
    run_alembic_migrations()
