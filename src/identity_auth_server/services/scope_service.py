"""Service layer for managing scopes."""

import logging
from uuid import UUID

from pydantic import BaseModel

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.idp.idp_client import IdpClient
from identity_auth_server.core.repositories.multi_agent_system import MultiAgentSystemRepository
from identity_auth_server.core.repositories.scope import ScopeRepository
from identity_auth_server.core.types import Scope

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class ScopeCreateRequest(BaseModel):
    """Request model for scope creation."""

    name: str
    mas_id: str


class ScopeUpdateRequest(BaseModel):
    """Request model for scope updates."""

    name: str | None = None  # Optional: if provided, change name; if not, keep current name
    mas_id: str | None = None  # Optional: if provided, change MAS; if not, keep current MAS


class ScopeService:
    """Service for managing scope lifecycle and operations."""

    def __init__(
        self,
        scope_repository: ScopeRepository,
        mas_repository: MultiAgentSystemRepository,
        idp_client: IdpClient,
    ):
        """Create a scope service.

        Args:
            scope_repository: Repository used to persist and query scopes.
            mas_repository: Repository used to query multi-agent systems.
            idp_client: Client used to interact with the identity provider.
        """
        self.scope_repository = scope_repository
        self.mas_repository = mas_repository
        self.idp_client = idp_client

    def create_scope(self, request: ScopeCreateRequest) -> Scope:
        """Create a new scope."""
        # Validate UUID format
        try:
            UUID(request.mas_id)
        except ValueError:
            raise ValueError(f"Invalid UUID format for mas_id: {request.mas_id}")

        # Validate MAS exists
        try:
            mas = self.mas_repository.get_by_id(request.mas_id)
        except Exception as e:
            raise ValueError(f"Invalid Multi Agent System ID: {request.mas_id}") from e

        if mas is None:
            raise ResourceNotFoundError(f"Multi Agent System with id {request.mas_id} not found.")

        # Create scope in database
        scope = Scope(name=request.name, mas_id=request.mas_id)
        db_scope = self.scope_repository.create_scope(scope)

        # Sync to Keycloak if MAS has authorization server
        if mas.authorization_server:
            try:
                self.idp_client.create_scopes(mas.authorization_server, [db_scope.name])
                logger.info(f"Created scope {db_scope.name} in Keycloak realm {mas.authorization_server.realm}")
            except Exception as e:
                logger.error(f"Failed to create scope {db_scope.name} in Keycloak: {e}")

        return db_scope

    def update_scope(self, scope_id: str, request: ScopeUpdateRequest) -> Scope:
        """Update an existing scope."""
        scope = self.scope_repository.get_scope_by_id(scope_id)
        if not scope:
            raise ResourceNotFoundError(f"Scope with id '{scope_id}' not found")

        # Load the MAS relationship if not already loaded
        if scope.mas_id and not scope.mas:
            scope.mas = self.mas_repository.get_by_id(str(scope.mas_id))

        # Store old values for Keycloak operations
        old_name = scope.name
        old_mas = scope.mas
        mas_changed = request.mas_id is not None and request.mas_id != str(scope.mas_id)

        # Update scope in database
        if request.name is not None:
            scope.name = request.name
        if request.mas_id is not None:
            # Validate UUID format
            try:
                UUID(request.mas_id)
            except ValueError:
                raise ValueError(f"Invalid UUID format for mas_id: {request.mas_id}")

            # Validate new MAS exists
            try:
                new_mas = self.mas_repository.get_by_id(request.mas_id)
            except Exception as e:
                raise ValueError(f"Invalid Multi Agent System ID: {request.mas_id}") from e

            if new_mas is None:
                raise ResourceNotFoundError(f"Multi Agent System with id {request.mas_id} not found.")
            scope.mas_id = request.mas_id
            # IMPORTANT: Reload the mas relationship to point to the new MAS
            scope.mas = new_mas

        db_scope = self.scope_repository.update_scope(scope)

        # Sync to Keycloak
        name_changed = request.name is not None and old_name != request.name
        logger.debug(f"Keycloak sync - mas_changed: {mas_changed}, name_changed: {name_changed}, old_name: {old_name}, new_name: {scope.name}")
        logger.debug(f"Keycloak sync - scope.mas: {scope.mas is not None}, old_mas: {old_mas is not None}")
        if mas_changed:
            logger.debug(
                f"MAS change details - old realm: {old_mas.authorization_server.realm if old_mas and old_mas.authorization_server else 'None'}, "
                f"new realm: {scope.mas.authorization_server.realm if scope.mas and scope.mas.authorization_server else 'None'}"
            )

        if mas_changed:
            logger.info(f"MAS changed - moving scope from old realm to new realm")
            # MAS changed: delete from old realm, create in new realm
            if old_mas and old_mas.authorization_server:
                try:
                    logger.debug(f"Deleting scope {old_name} from old realm {old_mas.authorization_server.realm}")
                    self.idp_client.delete_scope(old_mas.authorization_server, old_name)
                    logger.info(f"Deleted scope {old_name} from old Keycloak realm {old_mas.authorization_server.realm}")
                except Exception as e:
                    logger.error(f"Failed to delete scope {old_name} from old Keycloak realm: {e}")

            if scope.mas and scope.mas.authorization_server:
                try:
                    logger.debug(f"Creating scope {scope.name} in new realm {scope.mas.authorization_server.realm}")
                    self.idp_client.create_scopes(scope.mas.authorization_server, [scope.name])
                    logger.info(f"Created scope {scope.name} in new Keycloak realm {scope.mas.authorization_server.realm}")
                except Exception as e:
                    logger.error(f"Failed to create scope {scope.name} in new Keycloak realm: {e}")
        else:
            # Same MAS: just rename in Keycloak (if name changed)
            if name_changed:
                logger.debug(f"Name changed from {old_name} to {scope.name}, updating in Keycloak")
                if scope.mas and scope.mas.authorization_server:
                    try:
                        logger.debug(f"Updating scope in realm {scope.mas.authorization_server.realm}")
                        self.idp_client.update_scope(scope.mas.authorization_server, old_name, scope.name)
                        logger.info(
                            f"Updated scope {old_name} to {scope.name} in Keycloak realm {scope.mas.authorization_server.realm}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to update scope {old_name} to {scope.name} in Keycloak: {e}")
                else:
                    logger.warning(f"Scope has no MAS or authorization server, skipping Keycloak update")
            else:
                logger.debug(f"Name unchanged ({old_name}), no Keycloak update needed")

        return db_scope

    def delete_scope(self, scope_id: str) -> None:
        """Delete a scope."""
        scope = self.scope_repository.get_scope_by_id(scope_id)
        if not scope:
            raise ResourceNotFoundError(f"Scope with id '{scope_id}' not found")

        # Load the MAS relationship if not already loaded
        if scope.mas_id and not scope.mas:
            scope.mas = self.mas_repository.get_by_id(str(scope.mas_id))

        # Sync to Keycloak FIRST (safer for rollback if DB delete fails)
        if scope.mas and scope.mas.authorization_server:
            try:
                self.idp_client.delete_scope(scope.mas.authorization_server, scope.name)
                logger.info(f"Deleted scope {scope.name} from Keycloak realm {scope.mas.authorization_server.realm}")
            except Exception as e:
                logger.error(f"Failed to delete scope {scope.name} from Keycloak: {e}")

        # Delete from database
        self.scope_repository.delete_scope(scope)

    def get_scope_by_id(self, scope_id: str) -> Scope | None:
        """Get a scope by ID."""
        return self.scope_repository.get_scope_by_id(scope_id)

    def get_scope_by_name(self, name: str) -> Scope | None:
        """Get a scope by name."""
        return self.scope_repository.get_scope_by_name(name)

    def get_scopes_by_names(self, names: list[str]) -> list[Scope]:
        """Get scopes by names."""
        return self.scope_repository.get_scopes_by_names(names)

    def get_all_scopes(self) -> list[Scope]:
        """Get all scopes."""
        return self.scope_repository.get_all_scopes()
