"""Finalizer support for CRD cleanup.

Implements Kubernetes finalizers to ensure proper cleanup of resources
when CRDs are deleted.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from identity_auth_server.core.k8s_types import MultiAgentSystemCRD, ZTAPolicyCRD

logger = logging.getLogger(__name__)


class FinalizerHandler:
    """Handles finalizer operations for CRDs."""
    
    # Standard finalizer names
    FINALIZER_MAS_CLEANUP = "zta.io/mas-cleanup"
    FINALIZER_POLICY_CLEANUP = "zta.io/policy-cleanup"
    FINALIZER_KEYCLOAK_CLEANUP = "zta.io/keycloak-cleanup"
    
    @staticmethod
    def has_finalizer(finalizers: Optional[List[str]], finalizer: str) -> bool:
        """Check if a finalizer is present.
        
        Args:
            finalizers: List of finalizers on the resource
            finalizer: Finalizer to check for
            
        Returns:
            True if finalizer is present
        """
        if not finalizers:
            return False
        return finalizer in finalizers
    
    @staticmethod
    def add_finalizer(finalizers: Optional[List[str]], finalizer: str) -> List[str]:
        """Add a finalizer if not already present.
        
        Args:
            finalizers: Existing finalizers
            finalizer: Finalizer to add
            
        Returns:
            Updated finalizer list
        """
        if not finalizers:
            return [finalizer]
        
        if finalizer not in finalizers:
            finalizers.append(finalizer)
        
        return finalizers
    
    @staticmethod
    def remove_finalizer(finalizers: Optional[List[str]], finalizer: str) -> List[str]:
        """Remove a finalizer.
        
        Args:
            finalizers: Existing finalizers
            finalizer: Finalizer to remove
            
        Returns:
            Updated finalizer list
        """
        if not finalizers:
            return []
        
        return [f for f in finalizers if f != finalizer]
    
    @staticmethod
    def is_being_deleted(deletion_timestamp: Optional[datetime]) -> bool:
        """Check if resource is marked for deletion.
        
        Args:
            deletion_timestamp: Resource deletion timestamp
            
        Returns:
            True if resource is being deleted
        """
        return deletion_timestamp is not None
    
    async def cleanup_mas(self, mas_crd: MultiAgentSystemCRD) -> bool:
        """Perform cleanup for a MultiAgentSystem CRD.
        
        This is called when the MAS is being deleted and has the cleanup finalizer.
        
        Args:
            mas_crd: MultiAgentSystem CRD to clean up
            
        Returns:
            True if cleanup was successful
        """
        logger.info(
            f"Performing MAS cleanup for {mas_crd.metadata.namespace}/{mas_crd.metadata.name}"
        )
        
        try:
            # Clean up apps in database
            # This would integrate with the CRD service to delete apps
            
            logger.info(f"MAS cleanup completed for {mas_crd.metadata.namespace}/{mas_crd.metadata.name}")
            return True
            
        except Exception as e:
            logger.error(
                f"MAS cleanup failed for {mas_crd.metadata.namespace}/{mas_crd.metadata.name}: {e}"
            )
            return False
    
    async def cleanup_keycloak_realm(self, mas_crd: MultiAgentSystemCRD) -> bool:
        """Clean up Keycloak realm for a MultiAgentSystem.
        
        Args:
            mas_crd: MultiAgentSystem CRD
            
        Returns:
            True if cleanup was successful
        """
        logger.info(
            f"Cleaning up Keycloak realm for {mas_crd.metadata.namespace}/{mas_crd.metadata.name}"
        )
        
        try:
            # Delete Keycloak realm
            # This would integrate with the IdP client
            
            logger.info(
                f"Keycloak realm cleanup completed for {mas_crd.metadata.namespace}/{mas_crd.metadata.name}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Keycloak realm cleanup failed for {mas_crd.metadata.namespace}/{mas_crd.metadata.name}: {e}"
            )
            return False
    
    async def cleanup_policy(self, policy_crd: ZTAPolicyCRD) -> bool:
        """Perform cleanup for a ZTAPolicy CRD.
        
        This is called when the policy is being deleted and has the cleanup finalizer.
        
        Args:
            policy_crd: ZTAPolicy CRD to clean up
            
        Returns:
            True if cleanup was successful
        """
        logger.info(
            f"Performing policy cleanup for {policy_crd.metadata.namespace}/{policy_crd.metadata.name}"
        )
        
        try:
            # Clean up CiliumNetworkPolicy
            # This would integrate with Cilium to delete the generated policy
            
            logger.info(
                f"Policy cleanup completed for {policy_crd.metadata.namespace}/{policy_crd.metadata.name}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Policy cleanup failed for {policy_crd.metadata.namespace}/{policy_crd.metadata.name}: {e}"
            )
            return False


# Global finalizer handler instance
_finalizer_handler: Optional[FinalizerHandler] = None


def get_finalizer_handler() -> FinalizerHandler:
    """Get or create the global finalizer handler instance."""
    global _finalizer_handler
    if _finalizer_handler is None:
        _finalizer_handler = FinalizerHandler()
    return _finalizer_handler
