"""PostgreSQL implementation of ScopeRepository."""

from abc import ABC, abstractmethod
from typing import Any, cast

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from casa_auth_server.core.exceptions import ResourceAlreadyExistsError
from casa_auth_server.core.types import Scope


class ScopeRepository(ABC):
    """Interface for ScopeRepository."""

    @abstractmethod
    def create_scope(self, scope: Scope) -> Scope:
        """Create a new scope."""

    @abstractmethod
    def update_scope(self, scope: Scope) -> Scope:
        """Update an existing scope."""

    @abstractmethod
    def delete_scope(self, scope: Scope) -> None:
        """Delete a scope."""

    @abstractmethod
    def get_scope_by_id(self, scope_id: str) -> Scope | None:
        """Get a scope by ID."""

    @abstractmethod
    def get_scope_by_name(self, name: str) -> Scope | None:
        """Get a scope by name."""

    @abstractmethod
    def get_scopes_by_names(self, names: list[str]) -> list[Scope]:
        """Get scopes by names."""

    @abstractmethod
    def get_all_scopes(self) -> list[Scope]:
        """Get all scopes."""


class ScopePostgresRepository(ScopeRepository):
    """PostgreSQL implementation of ScopeRepository."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self._session = session

    def create_scope(self, scope: Scope) -> Scope:
        """Create a new scope in the database."""
        try:
            self._session.add(scope)
            # Force SQL execution now (not at request teardown commit) so unique
            # constraint violations can be returned as proper HTTP errors.
            self._session.flush()
            return scope
        except IntegrityError as e:
            raise ResourceAlreadyExistsError(f"Scope with name '{scope.name}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating scope: {e}") from e

    def update_scope(self, scope: Scope) -> Scope:
        """Update an existing scope in the database."""
        try:
            self._session.add(scope)
            # Same rationale as create: surface constraint violations immediately.
            self._session.flush()
            return scope
        except IntegrityError as e:
            raise ResourceAlreadyExistsError(f"Scope with name '{scope.name}' already exists") from e
        except Exception as e:
            raise Exception(f"Error updating scope with id '{scope.id}': {e}") from e

    def delete_scope(self, scope: Scope) -> None:
        """Delete a scope."""
        try:
            self._session.delete(scope)
        except Exception as e:
            raise Exception(f"Error deleting scope with id '{scope.id}': {e}") from e

    def get_scope_by_id(self, scope_id: str) -> Scope | None:
        """Retrieve a scope by its ID."""
        try:
            statement = (
                select(Scope)
                .where(Scope.id == scope_id)
                .options(joinedload(Scope.tools))
                .options(joinedload(Scope.mas))
            )
            return self._session.exec(statement).first()
        except Exception as e:
            raise Exception(f"Error retrieving scope with id '{scope_id}': {e}") from e

    def get_scope_by_name(self, name: str) -> Scope | None:
        """Retrieve a scope by name."""
        try:
            return self._session.exec(select(Scope).where(Scope.name == name)).first()
        except Exception as e:
            raise Exception(f"Error retrieving scope with name '{name}': {e}") from e

    def get_scopes_by_names(self, names: list[str]) -> list[Scope]:
        """Retrieve scopes by name."""
        if not names:
            return []
        try:
            scope_name_col = cast(Any, Scope.name)
            return list(self._session.exec(select(Scope).where(scope_name_col.in_(names))).all())
        except Exception as e:
            raise Exception(f"Error retrieving scopes by names: {e}") from e

    def get_all_scopes(self) -> list[Scope]:
        """Retrieve all scopes."""
        try:
            statement = select(Scope).options(joinedload(Scope.tools)).options(joinedload(Scope.mas))
            return list(self._session.exec(statement).unique().all())
        except Exception as e:
            raise Exception(f"Error retrieving scopes: {e}") from e
