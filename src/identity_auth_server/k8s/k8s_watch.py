"""Watch API support for real-time CRD updates.

This module implements Server-Sent Events (SSE) streaming for Kubernetes-style
watch endpoints, enabling operators to receive real-time notifications when
CRD resources change.
"""

import asyncio
import logging
from enum import Enum
from typing import Any, AsyncGenerator, Dict, Optional

from pydantic import BaseModel

from identity_auth_server.k8s.k8s_types import MultiAgentSystemCRD

logger = logging.getLogger(__name__)


class WatchEventType(str, Enum):
    """Kubernetes watch event types."""

    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    ERROR = "ERROR"
    BOOKMARK = "BOOKMARK"


class WatchEvent(BaseModel):
    """Kubernetes watch event structure."""

    type: WatchEventType
    object: Dict[str, Any]


class ResourceWatcher:
    """Manages watch subscriptions for CRD resources.

    This class implements a pub/sub pattern where operators can subscribe
    to watch specific resource types and receive real-time updates via
    Server-Sent Events.
    """

    def __init__(self):
        """Initialize the ResourceWatcher with empty subscriber and version maps."""
        self._mas_subscribers: Dict[str, list] = {}
        self._policy_subscribers: Dict[str, list] = {}
        self._resource_versions: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def subscribe_mas(
        self,
        namespace: Optional[str] = None,
        resource_version: Optional[str] = None,
    ) -> AsyncGenerator[WatchEvent, None]:
        """Subscribe to MultiAgentSystem CRD watch events.

        Args:
            namespace: Optional namespace filter
            resource_version: Start watching from this version

        Yields:
            WatchEvent objects for each change
        """
        queue: asyncio.Queue = asyncio.Queue()

        async with self._lock:
            key = f"mas-{namespace or 'all'}"
            if key not in self._mas_subscribers:
                self._mas_subscribers[key] = []
            self._mas_subscribers[key].append(queue)

        try:
            logger.info(f"Watch started for MultiAgentSystem in namespace={namespace}")

            # Send initial bookmark
            yield WatchEvent(
                type=WatchEventType.BOOKMARK,
                object={
                    "kind": "MultiAgentSystem",
                    "apiVersion": "zta.io/v1alpha1",
                    "metadata": {
                        "resourceVersion": resource_version or "0",
                    },
                },
            )

            # Stream events
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event
                except asyncio.TimeoutError:
                    # Send keepalive bookmark every 30s
                    current_version = self._resource_versions.get(key, 0)
                    yield WatchEvent(
                        type=WatchEventType.BOOKMARK,
                        object={
                            "kind": "MultiAgentSystem",
                            "apiVersion": "zta.io/v1alpha1",
                            "metadata": {
                                "resourceVersion": str(current_version),
                            },
                        },
                    )
        finally:
            # Cleanup on disconnect
            async with self._lock:
                if key in self._mas_subscribers:
                    self._mas_subscribers[key].remove(queue)
                    if not self._mas_subscribers[key]:
                        del self._mas_subscribers[key]
            logger.info(f"Watch closed for MultiAgentSystem in namespace={namespace}")

    async def notify_mas_event(
        self,
        event_type: WatchEventType,
        mas: MultiAgentSystemCRD,
        namespace: Optional[str] = None,
    ):
        """Notify all subscribers of a MultiAgentSystem change.

        Args:
            event_type: Type of change (ADDED, MODIFIED, DELETED)
            mas: The CRD object that changed
            namespace: Namespace of the resource
        """
        async with self._lock:
            # Increment resource version
            key = f"mas-{namespace or 'all'}"
            current_version = self._resource_versions.get(key, 0) + 1
            self._resource_versions[key] = current_version

            # Update resource version in metadata
            mas.metadata.resource_version = str(current_version)

            # Create watch event
            event = WatchEvent(
                type=event_type,
                object=mas.model_dump(mode="json", exclude_none=True),
            )

            # Notify namespace-specific subscribers
            if key in self._mas_subscribers:
                for queue in self._mas_subscribers[key]:
                    try:
                        await queue.put(event)
                    except Exception as e:
                        logger.error(f"Failed to notify subscriber: {e}")

            # Also notify 'all' subscribers if this is a namespaced event
            if namespace:
                all_key = "mas-all"
                if all_key in self._mas_subscribers:
                    for queue in self._mas_subscribers[all_key]:
                        try:
                            await queue.put(event)
                        except Exception as e:
                            logger.error(f"Failed to notify all subscriber: {e}")

    def get_subscriber_count(self, resource_type: str, namespace: Optional[str] = None) -> int:
        """Get the number of active subscribers for a resource type."""
        key = f"{resource_type}-{namespace or 'all'}"
        if resource_type == "mas":
            return len(self._mas_subscribers.get(key, []))
        elif resource_type == "policy":
            return len(self._policy_subscribers.get(key, []))
        return 0


# Global watcher instance
_watcher: Optional[ResourceWatcher] = None


def get_watcher() -> ResourceWatcher:
    """Get or create the global resource watcher instance."""
    global _watcher
    if _watcher is None:
        _watcher = ResourceWatcher()
    return _watcher
