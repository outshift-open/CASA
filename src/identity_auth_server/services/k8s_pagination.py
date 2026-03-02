"""Pagination support for CRD list operations.

Implements Kubernetes-style pagination with continue tokens for efficient
handling of large resource lists.
"""

import base64
import json
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class ListMeta(BaseModel):
    """Metadata for list responses."""
    
    resource_version: Optional[str] = Field(
        None,
        description="Resource version at time of list",
    )
    continue_token: Optional[str] = Field(
        None,
        alias="continue",
        description="Token to continue listing from",
    )
    remaining_item_count: Optional[int] = Field(
        None,
        description="Estimated number of items remaining",
    )


class PaginatedList(BaseModel, Generic[T]):
    """Generic paginated list response."""
    
    api_version: str
    kind: str
    metadata: ListMeta
    items: List[T]


class PaginationParams(BaseModel):
    """Parameters for pagination."""
    
    limit: Optional[int] = Field(
        None,
        ge=1,
        le=500,
        description="Maximum number of items to return",
    )
    continue_token: Optional[str] = Field(
        None,
        alias="continue",
        description="Token to continue from previous list",
    )


def encode_continue_token(offset: int, total: int) -> str:
    """Encode a continue token for pagination.
    
    The token contains:
    - offset: Index to start from
    - total: Total number of items (for validation)
    
    Args:
        offset: Starting offset for next page
        total: Total number of items
        
    Returns:
        Base64-encoded continue token
    """
    data = {"offset": offset, "total": total}
    json_str = json.dumps(data)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_continue_token(token: str) -> tuple[int, int]:
    """Decode a continue token.
    
    Args:
        token: Base64-encoded continue token
        
    Returns:
        Tuple of (offset, total)
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        json_str = base64.urlsafe_b64decode(token.encode()).decode()
        data = json.loads(json_str)
        return data["offset"], data["total"]
    except Exception as e:
        raise ValueError(f"Invalid continue token: {e}") from e


def paginate_list(
    items: List[T],
    limit: Optional[int] = None,
    continue_token: Optional[str] = None,
) -> tuple[List[T], Optional[str], Optional[int]]:
    """Paginate a list of items.
    
    Args:
        items: Full list of items to paginate
        limit: Maximum items per page
        continue_token: Token from previous page
        
    Returns:
        Tuple of (page_items, next_continue_token, remaining_count)
    """
    total = len(items)
    
    # Default limit
    if limit is None:
        limit = 100
    
    # Determine starting offset
    offset = 0
    if continue_token:
        try:
            decoded_offset, decoded_total = decode_continue_token(continue_token)
            # Validate total hasn't changed significantly
            if abs(decoded_total - total) > total * 0.1:  # 10% tolerance
                # Total changed significantly, start over
                offset = 0
            else:
                offset = decoded_offset
        except ValueError:
            # Invalid token, start from beginning
            offset = 0
    
    # Slice items
    end = min(offset + limit, total)
    page_items = items[offset:end]
    
    # Calculate remaining
    remaining = total - end
    
    # Generate next token if there are more items
    next_token = None
    if end < total:
        next_token = encode_continue_token(end, total)
    
    return page_items, next_token, remaining if remaining > 0 else None


class PaginationHelper:
    """Helper for building paginated responses."""
    
    @staticmethod
    def create_list_response(
        api_version: str,
        kind: str,
        items: List[T],
        resource_version: str,
        limit: Optional[int] = None,
        continue_token: Optional[str] = None,
    ) -> PaginatedList[T]:
        """Create a paginated list response.
        
        Args:
            api_version: API version
            kind: Resource kind (e.g., "MultiAgentSystemList")
            items: Full list of items
            resource_version: Current resource version
            limit: Page size limit
            continue_token: Continue token from previous page
            
        Returns:
            PaginatedList response
        """
        # Paginate
        page_items, next_token, remaining = paginate_list(items, limit, continue_token)
        
        # Build metadata
        metadata = ListMeta(
            resource_version=resource_version,
            continue_token=next_token,
            remaining_item_count=remaining,
        )
        
        return PaginatedList(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            items=page_items,
        )
