"""PostgreSQL database connection setup using SQLAlchemy."""

import logging
import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

from identity_auth_server.database.database import Database

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
