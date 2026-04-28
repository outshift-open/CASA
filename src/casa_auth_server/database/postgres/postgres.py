# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PostgreSQL database connection setup using SQLAlchemy."""

import logging
import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

from casa_auth_server.database.database import Database

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
