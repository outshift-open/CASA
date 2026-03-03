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
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install it with: pip install requests")
    sys.exit(1)

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


def create_mas(config: Config, name: str) -> Optional[Dict]:
    """Create a Multi-Agent System."""
    log_info(f"Creating MAS: {name}", config)

    if config.dry_run:
        log_info(f"[DRY RUN] Would create MAS: {name}", config)
        return {"id": "dry-run-mas-id", "name": name}

    try:
        response = requests.put(f"{config.backend_url}/mas", json={"name": name}, timeout=30)
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

    args = parser.parse_args()

    config = Config()
    if args.backend_url:
        config.backend_url = args.backend_url.rstrip("/")
    config.verbose = args.verbose
    config.dry_run = args.dry_run
    config.clear = args.clear

    try:
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
