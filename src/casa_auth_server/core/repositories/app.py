# Copyright 2026 Google LLC
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

"""PostgreSQL implementation of AppRepository."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from casa_auth_server.core.types import App, Tool


class AppRepository(ABC):
    """Interface for AppRepository."""

    @abstractmethod
    def create_app(self, app: App) -> App:
        """Create a new app."""

    @abstractmethod
    def update_app(self, app: App) -> App:
        """Update an existing app."""
        pass

    @abstractmethod
    def get_app_by_id(self, app_id: str) -> App | None:
        """Retrieve a app by app_id."""

    @abstractmethod
    def get_all_apps(self) -> List[App]:
        """Retrieve all apps."""

    @abstractmethod
    def get_mas_apps(self, mas_id: str) -> List[App]:
        """Retrieve all apps in a MAS."""

    @abstractmethod
    def delete_app(self, app: App) -> None:
        """Delete an app."""

    @abstractmethod
    def create_tool(self, tool: Tool) -> Tool:
        """Create a new tool."""


class AppPostgresRepository(AppRepository):
    """PostgreSQL implementation of AppRepository."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self._session = session

    def create_app(self, app: App) -> App:
        """Create a new app in the database."""
        try:
            self._session.add(app)
            return app
        except IntegrityError as e:
            raise ValueError(f"App with app_id '{app.id}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating app: {e}") from e

    def update_app(self, app: App) -> App:
        """Update an existing app in the database."""
        try:
            self._session.add(app)
            return app
        except Exception as e:
            raise Exception(f"Error updating app with id '{app.id}': {e}") from e

    def get_app_by_id(self, app_id: str) -> App | None:
        """Retrieve an app by its ID."""
        if app_id == "":
            return None

        try:
            app = self._session.exec(
                select(App)
                .where(App.id == app_id)
                .where(App.deleted_at == None)
                .options(joinedload(App.tools).joinedload(Tool.scopes))
            )
            return app.first()
        except Exception as e:
            raise Exception(f"Error retrieving app with id '{app_id}': {e}") from e

    def get_all_apps(self) -> List[App]:
        """Retrieve all apps."""
        try:
            apps = self._session.exec(select(App).where(App.deleted_at == None).options(joinedload(App.mas))).all()
            return list(apps)
        except Exception as e:
            raise Exception(f"Error retrieving apps: {e}") from e

    def get_mas_apps(self, mas_id):
        """Retrieve all apps in a MAS."""
        try:
            apps = self._session.exec(
                select(App).where(App.mas_id == mas_id).where(App.deleted_at == None).options(joinedload(App.mas))
            ).all()
            return list(apps)
        except Exception as e:
            raise Exception(f"Error retrieving apps: {e}") from e

    def delete_app(self, app: App) -> None:
        """Soft-delete an app by setting deleted_at."""
        try:
            app.deleted_at = datetime.now(timezone.utc)
            self._session.add(app)
        except Exception as e:
            raise Exception(f"Error deleting app with id '{app.id}': {e}") from e

    def create_tool(self, tool: Tool) -> Tool:
        """Create a new tool in the database."""
        try:
            self._session.add(tool)

            return tool
        except IntegrityError as e:
            raise ValueError(f"Tool with tool_id '{tool.id}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating tool: {e}") from e
