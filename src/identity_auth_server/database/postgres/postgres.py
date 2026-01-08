"""PostgreSQL database connection setup using SQLAlchemy."""

import logging
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

from identity_auth_server.database.database import Database
from identity_auth_server.database.postgres.alembic_runner import run_alembic_migrations

load_dotenv()

logger = logging.getLogger(__name__)


class PostgresDB(Database):
    """PostgreSQL database connection setup using SQLAlchemy."""

    def __init__(self):
        """Initialize the database connection."""
        # Database configuration from environment variables
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_username = os.getenv("DB_USERNAME")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")

        # Construct the database URL
        self.database_url = (
            f"postgresql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        logger.info(f"Database URL: {self.database_url}")

        self.engine = create_engine(self.database_url)
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def run_startup_migrations(self):
        """Run database migrations on application startup using Alembic."""
        try:
            logger.info("Starting Alembic database migrations...")
            run_alembic_migrations()
            logger.info("Alembic database migrations completed successfully")
        except Exception as e:
            logger.error(f"Alembic database migration failed: {e!s}")
            raise
