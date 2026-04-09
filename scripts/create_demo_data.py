#!/usr/bin/env python3
"""Demo data generator for ZTA Identity Auth Server.

This script populates the backend with sample data including:
- Multi-Agent Systems (MAS)
- Applications (Agents, Clients, MCP Servers)
- Tools with realistic schemas
- Scopes for authorization

Usage:
    python create_demo_data.py --verbose
    python create_demo_data.py --dry-run
    python create_demo_data.py --clear --verbose
    python create_demo_data.py --backend-url http://localhost:8000
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install it with: pip install requests")
    sys.exit(1)

try:
    import psycopg2
except ImportError:
    psycopg2 = None  # type: ignore[assignment]

try:
    from colorama import Fore, Style
    from colorama import init as colorama_init

    colorama_init(autoreset=True)
    COLORS_ENABLED = True
except ImportError:
    # Fallback if colorama is not installed
    COLORS_ENABLED = False

    class Fore:  # type: ignore[no-redef]
        """Fallback color class when colorama is not installed."""

        GREEN = RED = YELLOW = BLUE = CYAN = ""

    class Style:  # type: ignore[no-redef]
        """Fallback style class when colorama is not installed."""

        RESET_ALL = BRIGHT = ""


class Config:
    """Configuration for the demo data generator."""

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.verbose = False
        self.dry_run = False
        self.clear = False


def log_info(message: str, config: Config):
    """Log info message."""
    if config.verbose or config.dry_run:
        print(f"{Fore.CYAN}INFO: {message}{Style.RESET_ALL}")


def log_success(message: str):
    """Log success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def log_error(message: str):
    """Log error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def log_warning(message: str):
    """Log warning message."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def check_backend_health(config: Config) -> bool:
    """Check if the backend is accessible."""
    try:
        log_info(f"Checking backend at {config.backend_url}...", config)
        response = requests.get(f"{config.backend_url}/docs", timeout=5)
        if response.status_code == 200:
            log_success(f"Backend is accessible at {config.backend_url}")
            return True
        else:
            log_error(f"Backend returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        log_error(f"Cannot connect to backend at {config.backend_url}: {e}")
        return False


def create_mas(config: Config, name: str, enabled_tool_checks: Optional[int] = None) -> Optional[Dict]:
    """Create a Multi-Agent System."""
    log_info(f"Creating MAS: {name}", config)

    if config.dry_run:
        log_info(f"[DRY RUN] Would create MAS: {name}", config)
        return {"id": "dry-run-mas-id", "name": name}

    try:
        payload: Dict = {"name": name}
        if enabled_tool_checks is not None:
            payload["enabled_tool_checks"] = enabled_tool_checks
        response = requests.put(f"{config.backend_url}/mas", json=payload, timeout=30)
        response.raise_for_status()
        mas_data = response.json()
        log_success(f"Created MAS: {name} (ID: {mas_data['id']})")
        return mas_data
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to create MAS '{name}': {e}")
        return None


def create_app(config: Config, mas_id: str, app_data: Dict) -> Optional[Dict]:
    """Create an Application."""
    log_info(f"Creating App: {app_data['name']} ({app_data['type']})", config)

    if config.dry_run:
        log_info(f"[DRY RUN] Would create App: {app_data['name']}", config)
        return {"id": "dry-run-app-id", **app_data}

    try:
        payload = {
            "type": app_data["type"],
            "name": app_data["name"],
            "base_url": app_data["base_url"],
            "mas_id": mas_id,
            "tools": app_data.get("tools", []),
        }

        response = requests.post(f"{config.backend_url}/apps", json=payload, timeout=30)
        response.raise_for_status()
        created_app = response.json()
        log_success(f"Created App: {app_data['name']} (ID: {created_app['id']})")
        return created_app
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to create App '{app_data['name']}': {e}")
        if hasattr(e, "response") and e.response is not None:
            log_error(f"Response: {e.response.text}")
        return None


def create_scope(config: Config, mas_id: str, name: str) -> Optional[Dict]:
    """Create a Scope."""
    log_info(f"Creating Scope: {name}", config)

    if config.dry_run:
        log_info(f"[DRY RUN] Would create Scope: {name}", config)
        return {"id": "dry-run-scope-id", "name": name, "mas_id": mas_id}

    try:
        response = requests.post(f"{config.backend_url}/scopes", json={"name": name, "mas_id": mas_id}, timeout=30)
        response.raise_for_status()
        scope_data = response.json()
        log_success(f"Created Scope: {name} (ID: {scope_data['id']})")
        return scope_data
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to create Scope '{name}': {e}")
        return None


def delete_all_data(config: Config):
    """Delete all existing MAS, Apps, and Scopes."""
    log_warning("Clearing all existing data...")

    if config.dry_run:
        log_info("[DRY RUN] Would delete all existing data", config)
        return

    try:
        # Get and delete all MAS (this cascades to apps)
        response = requests.get(f"{config.backend_url}/mas", timeout=10)
        if response.status_code == 200:
            mas_list = response.json()
            for mas in mas_list:
                try:
                    requests.delete(f"{config.backend_url}/mas/{mas['id']}", timeout=30)
                    log_success(f"Deleted MAS: {mas['name']}")
                except Exception as e:
                    log_warning(f"Failed to delete MAS {mas['name']}: {e}")

        # Get and delete all scopes
        response = requests.get(f"{config.backend_url}/scopes", timeout=10)
        if response.status_code == 200:
            scopes_list = response.json()
            for scope in scopes_list:
                try:
                    requests.delete(f"{config.backend_url}/scopes/{scope['id']}", timeout=30)
                    log_success(f"Deleted Scope: {scope['name']}")
                except Exception as e:
                    log_warning(f"Failed to delete Scope {scope['name']}: {e}")

        log_success("Cleared all existing data")
    except Exception as e:
        log_error(f"Error during cleanup: {e}")


def get_sample_tool_schemas() -> Dict[str, Dict]:
    """Generate realistic tool input/output schemas."""
    return {
        "get_user_profile": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"},
                    },
                    "required": ["user_id"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                }
            ),
        },
        "search_products": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "category": {"type": "string", "description": "Product category"},
                        "max_results": {"type": "integer", "default": 10},
                    },
                    "required": ["query"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "products": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "price": {"type": "number"},
                                },
                            },
                        }
                    },
                }
            ),
        },
        "process_payment": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "description": "Payment amount"},
                        "currency": {"type": "string", "default": "USD"},
                        "payment_method": {"type": "string"},
                    },
                    "required": ["amount", "payment_method"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "transaction_id": {"type": "string"},
                        "status": {"type": "string"},
                        "timestamp": {"type": "string"},
                    },
                }
            ),
        },
        "send_email": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["to", "subject", "body"],
                }
            ),
            "output_schema": json.dumps(
                {"type": "object", "properties": {"message_id": {"type": "string"}, "status": {"type": "string"}}}
            ),
        },
        "query_database": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query"},
                        "parameters": {"type": "object"},
                    },
                    "required": ["query"],
                }
            ),
            "output_schema": json.dumps(
                {"type": "object", "properties": {"rows": {"type": "array"}, "row_count": {"type": "integer"}}}
            ),
        },
        "analyze_sentiment": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "Text to analyze"}},
                    "required": ["text"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                        "confidence": {"type": "number"},
                    },
                }
            ),
        },
        "create_ticket": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    },
                    "required": ["title", "description"],
                }
            ),
            "output_schema": json.dumps(
                {"type": "object", "properties": {"ticket_id": {"type": "string"}, "status": {"type": "string"}}}
            ),
        },
        "get_inventory": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {"product_id": {"type": "string"}, "warehouse_id": {"type": "string"}},
                    "required": ["product_id"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {"available_quantity": {"type": "integer"}, "reserved_quantity": {"type": "integer"}},
                }
            ),
        },
    }


def get_sample_mas_configs() -> List[Dict]:
    """Generate sample MAS configurations with apps and scopes."""
    tool_schemas = get_sample_tool_schemas()

    return [
        {
            "name": "E-commerce Platform",
            "scopes": ["read:products", "write:products", "read:orders", "write:orders", "process:payments"],
            "apps": [
                {
                    "type": "agent",
                    "name": "Shopping Assistant Agent",
                    "base_url": "https://ecommerce.example.com/shopping-agent",
                    "tools": [],
                },
                {
                    "type": "client",
                    "name": "Web Dashboard",
                    "base_url": "https://ecommerce.example.com/dashboard",
                    "tools": [],
                },
                {
                    "type": "mcp_server",
                    "name": "Product Database MCP",
                    "base_url": "https://ecommerce.example.com/mcp/products",
                    "tools": [
                        {
                            "name": "search_products",
                            "description": "Search for products in the catalog",
                            **tool_schemas["search_products"],
                            "scopes": ["read:products"],
                        },
                        {
                            "name": "get_inventory",
                            "description": "Check product inventory levels",
                            **tool_schemas["get_inventory"],
                            "scopes": ["read:products"],
                        },
                        {
                            "name": "query_database",
                            "description": "Query the product database",
                            **tool_schemas["query_database"],
                            "scopes": ["read:products"],
                        },
                        {
                            "name": "process_payment",
                            "description": "Process customer payment",
                            **tool_schemas["process_payment"],
                            "scopes": ["process:payments", "write:orders"],
                        },
                    ],
                },
            ],
        },
        {
            "name": "Customer Support System",
            "scopes": ["read:users", "write:users", "read:tickets", "write:tickets", "send:notifications"],
            "apps": [
                {
                    "type": "agent",
                    "name": "Support Agent",
                    "base_url": "https://support.example.com/agent",
                    "tools": [],
                },
                {
                    "type": "client",
                    "name": "Support Portal",
                    "base_url": "https://support.example.com/portal",
                    "tools": [],
                },
                {
                    "type": "mcp_server",
                    "name": "Support Services MCP",
                    "base_url": "https://support.example.com/mcp/services",
                    "tools": [
                        {
                            "name": "get_user_profile",
                            "description": "Retrieve customer profile information",
                            **tool_schemas["get_user_profile"],
                            "scopes": ["read:users"],
                        },
                        {
                            "name": "create_ticket",
                            "description": "Create a support ticket",
                            **tool_schemas["create_ticket"],
                            "scopes": ["write:tickets"],
                        },
                        {
                            "name": "analyze_sentiment",
                            "description": "Analyze customer message sentiment",
                            **tool_schemas["analyze_sentiment"],
                            "scopes": ["read:tickets"],
                        },
                        {
                            "name": "send_email",
                            "description": "Send email notifications to customers",
                            **tool_schemas["send_email"],
                            "scopes": ["send:notifications"],
                        },
                    ],
                },
            ],
        },
        {
            "name": "Financial Services",
            "scopes": ["read:accounts", "write:accounts", "read:transactions", "write:transactions", "execute:admin"],
            "apps": [
                {
                    "type": "agent",
                    "name": "Financial Advisor Agent",
                    "base_url": "https://finserv.example.com/advisor",
                    "tools": [],
                },
                {
                    "type": "client",
                    "name": "Banking Dashboard",
                    "base_url": "https://finserv.example.com/dashboard",
                    "tools": [],
                },
                {
                    "type": "mcp_server",
                    "name": "Transaction Database MCP",
                    "base_url": "https://finserv.example.com/mcp/transactions",
                    "tools": [
                        {
                            "name": "get_user_profile",
                            "description": "Get customer account information",
                            **tool_schemas["get_user_profile"],
                            "scopes": ["read:accounts"],
                        },
                        {
                            "name": "analyze_sentiment",
                            "description": "Analyze market sentiment",
                            **tool_schemas["analyze_sentiment"],
                            "scopes": ["read:transactions"],
                        },
                        {
                            "name": "query_database",
                            "description": "Query transaction database",
                            **tool_schemas["query_database"],
                            "scopes": ["read:transactions"],
                        },
                        {
                            "name": "process_payment",
                            "description": "Process financial transaction",
                            **tool_schemas["process_payment"],
                            "scopes": ["write:transactions"],
                        },
                    ],
                },
            ],
        },
    ]


def generate_demo_data(config: Config):
    """Generate all demo data."""
    print(f"\n{Fore.BLUE}{Style.BRIGHT}=== ZTA Identity Auth Server Demo Data Generator ==={Style.RESET_ALL}\n")

    if config.dry_run:
        log_info("Running in DRY RUN mode - no data will be created", config)

    if not config.dry_run and not check_backend_health(config):
        log_error("Backend is not accessible. Please ensure the server is running.")
        return False

    if config.clear:
        delete_all_data(config)
        log_success("Data cleanup completed")
        return True

    mas_configs = get_sample_mas_configs()

    total_mas = len(mas_configs)
    total_apps = sum(len(mas_config["apps"]) for mas_config in mas_configs)
    total_scopes = sum(len(mas_config["scopes"]) for mas_config in mas_configs)

    print(f"\n{Fore.BLUE}Planning to create:{Style.RESET_ALL}")
    print(f"  • {total_mas} Multi-Agent Systems")
    print(f"  • {total_apps} Applications")
    print(f"  • {total_scopes} Scopes")
    print()

    success_count = 0
    failure_count = 0

    for mas_config in mas_configs:
        print(f"\n{Fore.BLUE}{'─' * 60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}MAS: {mas_config['name']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'─' * 60}{Style.RESET_ALL}\n")

        # Create MAS
        mas = create_mas(config, mas_config["name"])
        if not mas:
            failure_count += 1
            continue

        success_count += 1
        mas_id = mas["id"]

        # Create Scopes
        print(f"\n{Fore.CYAN}Creating Scopes...{Style.RESET_ALL}")
        for scope_name in mas_config["scopes"]:
            scope = create_scope(config, mas_id, scope_name)
            if scope:
                success_count += 1
            else:
                failure_count += 1

        # Create Apps
        print(f"\n{Fore.CYAN}Creating Applications...{Style.RESET_ALL}")
        for app_config in mas_config["apps"]:
            app = create_app(config, mas_id, app_config)
            if app:
                success_count += 1
            else:
                failure_count += 1

    # Summary
    print(f"\n{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{Style.BRIGHT}Summary{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}\n")

    if config.dry_run:
        log_info("DRY RUN completed - no data was actually created", config)
    else:
        print(f"{Fore.GREEN}✓ Successfully created: {success_count} items{Style.RESET_ALL}")
        if failure_count > 0:
            print(f"{Fore.RED}✗ Failed to create: {failure_count} items{Style.RESET_ALL}")

    print()
    return failure_count == 0


def _get_client_secret_from_keycloak(client_id: str, realm: str, config: Config) -> Optional[str]:
    """Fetch client secret from Keycloak admin API."""
    idp_url = os.getenv("IDP_SERVER_URL", "http://localhost:8081").rstrip("/")
    idp_user = os.getenv("IDP_ADMIN_USERNAME", "admin")
    idp_pass = os.getenv("IDP_ADMIN_PASSWORD", "admin")

    try:
        # Get admin token
        token_resp = requests.post(
            f"{idp_url}/realms/master/protocol/openid-connect/token",
            data={"grant_type": "password", "client_id": "admin-cli", "username": idp_user, "password": idp_pass},
            timeout=10,
        )
        token_resp.raise_for_status()
        admin_token = token_resp.json()["access_token"]

        # Find client internal ID
        clients_resp = requests.get(
            f"{idp_url}/admin/realms/{realm}/clients",
            params={"clientId": client_id},
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10,
        )
        clients_resp.raise_for_status()
        clients = clients_resp.json()
        if not clients:
            log_error(f"Client '{client_id}' not found in realm '{realm}'")
            return None
        internal_id = clients[0]["id"]

        # Get secret
        secret_resp = requests.get(
            f"{idp_url}/admin/realms/{realm}/clients/{internal_id}/client-secret",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10,
        )
        secret_resp.raise_for_status()
        return secret_resp.json().get("value")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to get secret from Keycloak: {e}")
        return None


def _get_mas_realm(mas_id: str, config: Config) -> Optional[str]:
    """Get the Keycloak realm name for a MAS (format: {name}-{id}-auth-server)."""
    try:
        resp = requests.get(f"{config.backend_url}/mas/{mas_id}", timeout=10)
        resp.raise_for_status()
        mas_data = resp.json()
        return f"{mas_data['name']}-{mas_id}-auth-server"
    except requests.exceptions.RequestException:
        return None


def _get_app_credentials(app_id: str, realm: str, config: Config) -> Optional[Dict]:
    """Get client_id and client_secret for an app."""
    try:
        meta_resp = requests.get(f"{config.backend_url}/{app_id}/oauth2/client-metadata.json", timeout=10)
        meta_resp.raise_for_status()
        client_id = meta_resp.json()["client_id"]
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to fetch metadata for app {app_id}: {e}")
        return None

    client_secret = _get_client_secret_from_keycloak(client_id, realm, config)
    if not client_secret:
        return None

    return {"client_id": client_id, "client_secret": client_secret}


def test_flow(config: Config):
    """Create a full MAS (client + agent + MCP server) and run the complete token flow."""
    print(f"\n{Fore.BLUE}{Style.BRIGHT}=== ZTA Full Token Flow Test ==={Style.RESET_ALL}\n")

    tool_schemas = get_sample_tool_schemas()

    # 1. Create MAS with tool checks disabled (no real MCP server available in test)
    mas = create_mas(config, "Test MAS", enabled_tool_checks=0)
    if not mas:
        return False
    mas_id = mas["id"]
    realm = _get_mas_realm(mas_id, config)
    if not realm:
        log_error("Could not determine Keycloak realm for MAS")
        return False
    print(f"  mas_id = {mas_id}")
    print(f"  realm  = {realm}\n")

    # 2. Create all three app types
    client_app = create_app(
        config,
        mas_id,
        {
            "type": "client",
            "name": "Test Client",
            "base_url": f"{config.backend_url}/test-client",
            "tools": [],
        },
    )
    agent_app = create_app(
        config,
        mas_id,
        {
            "type": "agent",
            "name": "Test Agent",
            "base_url": f"{config.backend_url}/test-agent",
            "tools": [],
        },
    )
    mcp_app = create_app(
        config,
        mas_id,
        {
            "type": "mcp_server",
            "name": "Test MCP Server",
            "base_url": f"{config.backend_url}/test-mcp",
            "tools": [
                {
                    "name": "get_account_balance",
                    "description": "Get the account balance for a user",
                    **tool_schemas["get_user_profile"],
                    "scopes": [],
                }
            ],
        },
    )

    if not client_app or not agent_app or not mcp_app:
        return False

    client_app_id = client_app["id"]
    agent_app_id = agent_app["id"]
    mcp_app_id = mcp_app["id"]

    # 3. Fetch credentials for client and agent (MCP server needs them for token_exchange)
    print(f"\n{Fore.CYAN}Fetching credentials from Keycloak...{Style.RESET_ALL}")
    client_creds = _get_app_credentials(client_app_id, realm, config)
    agent_creds = _get_app_credentials(agent_app_id, realm, config)
    mcp_creds = _get_app_credentials(mcp_app_id, realm, config)

    if not client_creds or not agent_creds or not mcp_creds:
        log_error("Failed to retrieve credentials for one or more apps")
        return False

    log_success(f"client  {client_app_id}: {client_creds['client_id'][:50]}...")
    log_success(f"agent   {agent_app_id}: {agent_creds['client_id'][:50]}...")
    log_success(f"mcp     {mcp_app_id}: {mcp_creds['client_id'][:50]}...")

    # 4. Client gets initial token
    print(f"\n{Fore.CYAN}Step 1: Client gets initial token...{Style.RESET_ALL}")
    try:
        resp = requests.post(
            f"{config.backend_url}/{client_app_id}/oauth2/token",
            data={
                "client_id": client_creds["client_id"],
                "client_secret": client_creds["client_secret"],
                "user_input": "Show me my account balance",
            },
            timeout=30,
        )
        resp.raise_for_status()
        client_token = resp.json()["access_token"]
        log_success(f"Client token: {client_token[:50]}...")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to get client token: {e}")
        if hasattr(e, "response") and e.response is not None:
            log_error(f"Response: {e.response.text}")
        return False

    # 5. Agent reports LLM call started
    print(f"\n{Fore.CYAN}Step 2: Agent records LLM call_start...{Style.RESET_ALL}")
    try:
        resp = requests.post(
            f"{config.backend_url}/trace/llm/call_start",
            json={"call_id": "test-call-1", "prompt": "Show me my account balance"},
            headers={"Authorization": f"Bearer {client_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        log_success(f"LLMCallStartedEvent: mas_id = {resp.json().get('mas_id')}")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to record LLM call_start: {e}")
        return False

    # 6. Agent exchanges token
    print(f"\n{Fore.CYAN}Step 3: Agent exchanges token...{Style.RESET_ALL}")
    try:
        resp = requests.post(
            f"{config.backend_url}/{agent_app_id}/oauth2/token_exchange",
            data={
                "client_id": agent_creds["client_id"],
                "client_secret": agent_creds["client_secret"],
                "subject_token": client_token,
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            },
            timeout=30,
        )
        resp.raise_for_status()
        agent_token = resp.json()["access_token"]
        log_success(f"Agent token: {agent_token[:50]}...")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to exchange agent token: {e}")
        if hasattr(e, "response") and e.response is not None:
            log_error(f"Response: {e.response.text}")
        return False

    # 7. Agent reports LLM call ended (selected a tool)
    print(f"\n{Fore.CYAN}Step 4: Agent records LLM call_end...{Style.RESET_ALL}")
    try:
        resp = requests.post(
            f"{config.backend_url}/trace/llm/call_end",
            json={
                "call_id": "test-call-1",
                "response": "I will check your balance",
                "tools": "[Tool(name='get_account_balance')]",
            },
            headers={"Authorization": f"Bearer {agent_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        log_success(f"LLMCallEndedEvent: mas_id = {resp.json().get('mas_id')}")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to record LLM call_end: {e}")
        return False

    # 8. MCP server exchanges token (no tool check — no real MCP server running)
    print(f"\n{Fore.CYAN}Step 5: MCP server exchanges token...{Style.RESET_ALL}")
    try:
        resp = requests.post(
            f"{config.backend_url}/{mcp_app_id}/oauth2/token_exchange",
            data={
                "client_id": mcp_creds["client_id"],
                "client_secret": mcp_creds["client_secret"],
                "subject_token": agent_token,
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            },
            timeout=30,
        )
        resp.raise_for_status()
        mcp_token = resp.json()["access_token"]
        log_success(f"MCP token: {mcp_token[:50]}...")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to exchange MCP token: {e}")
        if hasattr(e, "response") and e.response is not None:
            log_error(f"Response: {e.response.text}")
        return False

    # 9. Introspect MCP token and verify mas_id
    print(f"\n{Fore.CYAN}Step 6: Introspecting MCP token...{Style.RESET_ALL}")
    try:
        resp = requests.post(
            f"{config.backend_url}/oauth2/introspect",
            data={"token": mcp_token, "tools": ["get_account_balance"]},
            timeout=10,
        )
        resp.raise_for_status()
        introspect = resp.json()
        log_success(f"Token active: {introspect.get('active')}")
        print(f"  mas_id = {introspect.get('mas_id')}")
        print(f"  app_id = {introspect.get('app_id')}")
        print(f"  tools  = {introspect.get('tools')}")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to introspect token: {e}")
        return False

    # 10. Verify all traces have correct mas_id
    print(f"\n{Fore.CYAN}Step 7: Verifying all traces have mas_id={mas_id}...{Style.RESET_ALL}")
    try:
        resp = requests.get(f"{config.backend_url}/trace", params={"mas_id": mas_id}, timeout=10)
        resp.raise_for_status()
        traces_data = resp.json()
        total = traces_data.get("total", 0)
        items = traces_data.get("items", {})
        log_success(f"Found {total} trace group(s)")

        all_ok = True
        for _, events in items.items():
            for event in events:
                event_mas_id = event.get("event", {}).get("mas_id")
                if event_mas_id != mas_id:
                    log_error(f"  {event.get('event_type')}: mas_id={event_mas_id} ✗")
                    all_ok = False
                else:
                    print(f"  {event.get('event_type')}: mas_id = {event_mas_id} ✓")

        if all_ok:
            log_success("All trace events have the correct mas_id!")
        return all_ok

    except requests.exceptions.RequestException as e:
        log_error(f"Failed to fetch traces: {e}")
        return False


def mock_tools(config: Config) -> bool:
    """Insert mock MCPCallStartedEvent traces directly into the DB for dashboard testing.

    Fetches existing user_input_ids from the trace table and inserts a realistic
    mix of approved and blocked MCP tool call events against them.
    """
    if psycopg2 is None:
        log_error("psycopg2 is required for --mock-tools. Install it with: pip install psycopg2-binary")
        return False

    print(f"\n{Fore.BLUE}{Style.BRIGHT}=== Inserting Mock MCP Tool Call Traces ==={Style.RESET_ALL}\n")

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USERNAME", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "identity-platform")

    try:
        conn = psycopg2.connect(host=db_host, port=db_port, user=db_user, password=db_pass, dbname=db_name)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        log_error(f"Failed to connect to database: {e}")
        return False

    # Fetch existing user_input_ids and their mas_ids from TokenIssuedEvent traces
    cur.execute(
        """
        SELECT user_input_id, event->>'mas_id', event->>'app_id'
        FROM trace
        WHERE event_type = 'TokenIssuedEvent'
        ORDER BY created_at DESC
        LIMIT 20
        """
    )
    rows = cur.fetchall()

    if not rows:
        log_error("No existing TokenIssuedEvent traces found. Run --test-flow first to create some.")
        cur.close()
        conn.close()
        return False

    log_success(f"Found {len(rows)} existing token request(s) to attach mock tool calls to")

    # Mock tool calls: mix of approved and blocked with varied reasons
    mock_scenarios = [
        {"tool": "get_account_balance", "blocked": False, "blocking_type": None, "blocking_reason": None},
        {"tool": "search_products", "blocked": False, "blocking_type": None, "blocking_reason": None},
        {"tool": "get_user_profile", "blocked": False, "blocking_type": None, "blocking_reason": None},
        {
            "tool": "process_payment",
            "blocked": True,
            "blocking_type": "DETERMINISTIC",
            "blocking_reason": "tool_not_selected_by_llm",
        },
        {
            "tool": "query_database",
            "blocked": True,
            "blocking_type": "DETERMINISTIC",
            "blocking_reason": "tool_not_selected_by_llm",
        },
        {
            "tool": "send_email",
            "blocked": True,
            "blocking_type": "DETERMINISTIC",
            "blocking_reason": "tool_intent_mismatch",
        },
        {
            "tool": "create_ticket",
            "blocked": True,
            "blocking_type": "AI_POWERED",
            "blocking_reason": "tool_intent_mismatch",
        },
        {"tool": "analyze_sentiment", "blocked": False, "blocking_type": None, "blocking_reason": None},
        {
            "tool": "process_payment",
            "blocked": True,
            "blocking_type": "DETERMINISTIC",
            "blocking_reason": "no_llm_calls_made_by_app",
        },
        {"tool": "get_inventory", "blocked": False, "blocking_type": None, "blocking_reason": None},
    ]

    inserted = 0
    now = datetime.now(timezone.utc)

    for i, (user_input_id, mas_id, app_id) in enumerate(rows):
        # Assign 2-4 scenarios per user_input in rotation
        scenarios = mock_scenarios[i % len(mock_scenarios) : i % len(mock_scenarios) + 3] or mock_scenarios[:3]
        for scenario in scenarios:
            event_id = str(uuid.uuid4())
            event = {
                "id": event_id,
                "user_input_id": str(user_input_id),
                "created_at": now.isoformat(),
                "mas_id": mas_id,
                "app_id": app_id,
                "token": "",
                "caller_app_id": str(app_id) if app_id else "",
                "callee_app_id": str(app_id) if app_id else "",
                "tool": scenario["tool"],
                "blocked": scenario["blocked"],
                "blocking_type": scenario["blocking_type"],
                "blocking_reason": scenario["blocking_reason"],
            }
            cur.execute(
                """
                INSERT INTO trace (id, user_input_id, created_at, event_type, event)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (event_id, str(user_input_id), now, "MCPCallStartedEvent", json.dumps(event)),
            )
            status = f"{'blocked' if scenario['blocked'] else 'approved'}"
            log_info(f"  {scenario['tool']} → {status} ({scenario.get('blocking_reason') or 'ok'})", config)
            inserted += 1

    cur.close()
    conn.close()

    log_success(f"Inserted {inserted} mock MCPCallStartedEvent traces")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate demo data for ZTA Identity Auth Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_demo_data.py --verbose
  python create_demo_data.py --dry-run
  python create_demo_data.py --clear --verbose
  python create_demo_data.py --test-flow
  python create_demo_data.py --mock-tools --verbose
  python create_demo_data.py --backend-url http://localhost:8000

Environment Variables:
  BACKEND_URL    Backend API URL (default: http://localhost:8000)
        """,
    )

    parser.add_argument("--backend-url", help="Backend API URL (overrides BACKEND_URL env var)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview what would be created without actually creating anything"
    )
    parser.add_argument("--clear", action="store_true", help="Delete all existing data before creating new demo data")
    parser.add_argument(
        "--test-flow", action="store_true", help="Run end-to-end token flow test to verify mas_id in traces"
    )
    parser.add_argument(
        "--mock-tools",
        action="store_true",
        help="Insert mock MCPCallStartedEvent traces into the DB for dashboard testing",
    )

    args = parser.parse_args()

    config = Config()
    if args.backend_url:
        config.backend_url = args.backend_url.rstrip("/")
    config.verbose = args.verbose
    config.dry_run = args.dry_run
    config.clear = args.clear

    try:
        if args.test_flow:
            success = test_flow(config)
        elif args.mock_tools:
            success = mock_tools(config)
        else:
            success = generate_demo_data(config)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        if config.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
