"""Label and field selector support for CRD filtering.

Implements Kubernetes-style label selectors and field selectors for filtering
CRD resources in list and watch operations.
"""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class LabelSelector(BaseModel):
    """Kubernetes label selector."""
    
    match_labels: Optional[Dict[str, str]] = None
    match_expressions: Optional[List[Dict[str, Any]]] = None


class FieldSelector(BaseModel):
    """Kubernetes field selector."""
    
    field: str
    operator: str  # =, ==, !=
    value: str


def parse_label_selector(selector_str: Optional[str]) -> Optional[LabelSelector]:
    """Parse label selector string into structured format.
    
    Supports:
    - Equality: environment=production
    - Inequality: tier!=frontend
    - Set membership: environment in (production, staging)
    - Set exclusion: tier notin (frontend, backend)
    - Existence: has_label
    - Non-existence: !has_label
    
    Examples:
        "environment=production" -> {match_labels: {environment: production}}
        "environment=production,tier=frontend" -> multiple labels
        "environment in (production,staging)" -> match expression
    
    Args:
        selector_str: Label selector string (comma-separated)
        
    Returns:
        LabelSelector or None if selector_str is None
    """
    if not selector_str:
        return None
    
    match_labels = {}
    match_expressions = []
    
    # Split by commas (not inside parentheses)
    parts = []
    current = ""
    paren_depth = 0
    
    for char in selector_str:
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif char == ',' and paren_depth == 0:
            parts.append(current.strip())
            current = ""
            continue
        current += char
    
    if current:
        parts.append(current.strip())
    
    for part in parts:
        part = part.strip()
        
        # Check for set operators: in, notin
        if ' in ' in part:
            field, values_str = part.split(' in ', 1)
            field = field.strip()
            values_str = values_str.strip('()')
            values = [v.strip() for v in values_str.split(',')]
            match_expressions.append({
                "key": field,
                "operator": "In",
                "values": values,
            })
        elif ' notin ' in part:
            field, values_str = part.split(' notin ', 1)
            field = field.strip()
            values_str = values_str.strip('()')
            values = [v.strip() for v in values_str.split(',')]
            match_expressions.append({
                "key": field,
                "operator": "NotIn",
                "values": values,
            })
        # Check for existence/non-existence
        elif part.startswith('!'):
            field = part[1:].strip()
            match_expressions.append({
                "key": field,
                "operator": "DoesNotExist",
            })
        elif '=' not in part and '!' not in part:
            # Just a field name = exists
            match_expressions.append({
                "key": part,
                "operator": "Exists",
            })
        # Equality/inequality
        elif '!=' in part:
            field, value = part.split('!=', 1)
            match_expressions.append({
                "key": field.strip(),
                "operator": "NotIn",
                "values": [value.strip()],
            })
        elif '==' in part or '=' in part:
            separator = '==' if '==' in part else '='
            field, value = part.split(separator, 1)
            match_labels[field.strip()] = value.strip()
    
    return LabelSelector(
        match_labels=match_labels if match_labels else None,
        match_expressions=match_expressions if match_expressions else None,
    )


def parse_field_selector(selector_str: Optional[str]) -> List[FieldSelector]:
    """Parse field selector string.
    
    Examples:
        "metadata.name=production-mas"
        "metadata.namespace=default,status.phase=Active"
    
    Args:
        selector_str: Field selector string (comma-separated)
        
    Returns:
        List of FieldSelector objects
    """
    if not selector_str:
        return []
    
    selectors = []
    parts = selector_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        if '!=' in part:
            field, value = part.split('!=', 1)
            selectors.append(FieldSelector(
                field=field.strip(),
                operator='!=',
                value=value.strip(),
            ))
        elif '==' in part:
            field, value = part.split('==', 1)
            selectors.append(FieldSelector(
                field=field.strip(),
                operator='==',
                value=value.strip(),
            ))
        elif '=' in part:
            field, value = part.split('=', 1)
            selectors.append(FieldSelector(
                field=field.strip(),
                operator='=',
                value=value.strip(),
            ))
    
    return selectors


def matches_label_selector(labels: Dict[str, str], selector: Optional[LabelSelector]) -> bool:
    """Check if labels match a label selector.
    
    Args:
        labels: Resource labels
        selector: Label selector to match against
        
    Returns:
        True if labels match selector
    """
    if not selector:
        return True
    
    # Check match_labels
    if selector.match_labels:
        for key, value in selector.match_labels.items():
            if labels.get(key) != value:
                return False
    
    # Check match_expressions
    if selector.match_expressions:
        for expr in selector.match_expressions:
            key = expr["key"]
            operator = expr["operator"]
            
            if operator == "In":
                if labels.get(key) not in expr["values"]:
                    return False
            elif operator == "NotIn":
                if labels.get(key) in expr.get("values", []):
                    return False
            elif operator == "Exists":
                if key not in labels:
                    return False
            elif operator == "DoesNotExist":
                if key in labels:
                    return False
    
    return True


def matches_field_selector(resource: Dict[str, Any], selectors: List[FieldSelector]) -> bool:
    """Check if resource matches field selectors.
    
    Args:
        resource: CRD resource as dictionary
        selectors: List of field selectors
        
    Returns:
        True if all selectors match
    """
    if not selectors:
        return True
    
    for selector in selectors:
        # Navigate nested fields (e.g., metadata.name)
        parts = selector.field.split('.')
        value = resource
        
        try:
            for part in parts:
                value = value[part]
        except (KeyError, TypeError):
            # Field doesn't exist
            if selector.operator == '!=':
                continue  # Not equal to non-existent is true
            return False
        
        # Compare
        if selector.operator in ('=', '=='):
            if str(value) != selector.value:
                return False
        elif selector.operator == '!=':
            if str(value) == selector.value:
                return False
    
    return True
