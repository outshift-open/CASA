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
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

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
    """Create a Multi-Agent System, returning existing one if it already exists."""
    log_info(f"Creating MAS: {name}", config)

    if config.dry_run:
        log_info(f"[DRY RUN] Would create MAS: {name}", config)
        return {"id": "dry-run-mas-id", "name": name}

    try:
        # Check if MAS with this name already exists
        existing_resp = requests.get(f"{config.backend_url}/mas", timeout=10)
        existing_resp.raise_for_status()
        existing = next((m for m in existing_resp.json() if m["name"] == name), None)
        if existing:
            log_info(f"MAS already exists: {name} (ID: {existing['id']})", config)
            return existing

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
        if response.status_code == 409:
            # Scope name is globally unique — fetch by name only
            existing = requests.get(f"{config.backend_url}/scopes", timeout=10)
            existing.raise_for_status()
            match = next((s for s in existing.json() if s["name"] == name), None)
            if match:
                log_info(f"Scope already exists: {name} (ID: {match['id']})", config)
                return match
            log_warning(f"Scope '{name}' conflict but could not find existing entry — skipping")
            return None
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
        "get_build_status": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string", "description": "Pipeline identifier"},
                        "branch": {"type": "string", "description": "Git branch name"},
                    },
                    "required": ["pipeline_id"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["pending", "running", "success", "failed"]},
                        "commit_sha": {"type": "string"},
                        "duration_s": {"type": "integer"},
                    },
                }
            ),
        },
        "trigger_deploy": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "Service name to deploy"},
                        "version": {"type": "string", "description": "Version tag (e.g. v2.3.1)"},
                        "environment": {"type": "string", "enum": ["dev", "staging", "prod"]},
                    },
                    "required": ["service", "version", "environment"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "deploy_id": {"type": "string"},
                        "status": {"type": "string"},
                    },
                }
            ),
        },
        "rollback_deployment": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "deploy_id": {"type": "string", "description": "Deployment ID to roll back"},
                        "reason": {"type": "string", "description": "Reason for rollback"},
                    },
                    "required": ["deploy_id", "reason"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "rollback_id": {"type": "string"},
                        "status": {"type": "string"},
                    },
                }
            ),
        },
        "create_incident": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
                        "description": {"type": "string"},
                    },
                    "required": ["title", "severity", "description"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "incident_id": {"type": "string"},
                        "status": {"type": "string"},
                    },
                }
            ),
        },
        "read_patient_record": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string", "description": "Patient identifier"},
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of fields to return",
                        },
                    },
                    "required": ["patient_id"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "name": {"type": "string"},
                        "dob": {"type": "string"},
                        "diagnoses": {"type": "array", "items": {"type": "string"}},
                    },
                }
            ),
        },
        "write_prescription": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "medication": {"type": "string"},
                        "dosage": {"type": "string"},
                        "duration_days": {"type": "integer"},
                    },
                    "required": ["patient_id", "medication", "dosage", "duration_days"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "prescription_id": {"type": "string"},
                        "status": {"type": "string"},
                    },
                }
            ),
        },
        "schedule_appointment": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "provider_id": {"type": "string"},
                        "datetime": {"type": "string", "description": "ISO 8601 datetime"},
                        "type": {"type": "string", "description": "Appointment type (e.g. follow-up, consult)"},
                    },
                    "required": ["patient_id", "provider_id", "datetime", "type"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "appointment_id": {"type": "string"},
                        "confirmed": {"type": "boolean"},
                    },
                }
            ),
        },
        "get_lab_results": {
            "input_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "test_type": {"type": "string", "description": "Type of lab test"},
                        "since": {"type": "string", "description": "ISO 8601 date — return results after this date"},
                    },
                    "required": ["patient_id", "test_type"],
                }
            ),
            "output_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "results": {"type": "array", "items": {"type": "object"}},
                        "count": {"type": "integer"},
                    },
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
        {
            "name": "DevOps CI-CD Platform",
            "scopes": ["read:builds", "write:deploys", "read:incidents", "write:incidents", "execute:rollback"],
            "apps": [
                {
                    "type": "client",
                    "name": "CI/CD Dashboard",
                    "base_url": "https://devops.example.com/dashboard",
                    "tools": [],
                },
                {
                    "type": "agent",
                    "name": "Deploy Orchestrator Agent",
                    "base_url": "https://devops.example.com/agents/deploy",
                    "tools": [],
                },
                {
                    "type": "agent",
                    "name": "Incident Response Agent",
                    "base_url": "https://devops.example.com/agents/incident",
                    "tools": [],
                },
                {
                    "type": "mcp_server",
                    "name": "Pipeline MCP",
                    "base_url": "https://devops.example.com/mcp/pipeline",
                    "tools": [
                        {
                            "name": "get_build_status",
                            "description": "Get the status of a CI pipeline build",
                            **tool_schemas["get_build_status"],
                            "scopes": ["read:builds"],
                        },
                        {
                            "name": "trigger_deploy",
                            "description": "Trigger a deployment for a service",
                            **tool_schemas["trigger_deploy"],
                            "scopes": ["write:deploys"],
                        },
                        {
                            "name": "rollback_deployment",
                            "description": "Roll back a deployment to the previous version",
                            **tool_schemas["rollback_deployment"],
                            "scopes": ["execute:rollback"],
                        },
                        {
                            "name": "create_incident",
                            "description": "Create an incident in the incident management system",
                            **tool_schemas["create_incident"],
                            "scopes": ["write:incidents"],
                        },
                    ],
                },
            ],
        },
        {
            "name": "Healthcare Records System",
            "scopes": ["read:patients", "write:prescriptions", "read:labs", "write:appointments", "execute:admin"],
            "apps": [
                {
                    "type": "client",
                    "name": "Clinical Portal",
                    "base_url": "https://healthcare.example.com/portal",
                    "tools": [],
                },
                {
                    "type": "agent",
                    "name": "Clinical Assistant Agent",
                    "base_url": "https://healthcare.example.com/agents/clinical",
                    "tools": [],
                },
                {
                    "type": "agent",
                    "name": "Pharmacy Agent",
                    "base_url": "https://healthcare.example.com/agents/pharmacy",
                    "tools": [],
                },
                {
                    "type": "mcp_server",
                    "name": "EHR MCP",
                    "base_url": "https://healthcare.example.com/mcp/ehr",
                    "tools": [
                        {
                            "name": "read_patient_record",
                            "description": "Read a patient's electronic health record",
                            **tool_schemas["read_patient_record"],
                            "scopes": ["read:patients"],
                        },
                        {
                            "name": "write_prescription",
                            "description": "Write a new prescription for a patient",
                            **tool_schemas["write_prescription"],
                            "scopes": ["write:prescriptions"],
                        },
                        {
                            "name": "schedule_appointment",
                            "description": "Schedule a medical appointment",
                            **tool_schemas["schedule_appointment"],
                            "scopes": ["write:appointments"],
                        },
                        {
                            "name": "get_lab_results",
                            "description": "Retrieve lab test results for a patient",
                            **tool_schemas["get_lab_results"],
                            "scopes": ["read:labs"],
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

    # Fetch MAS names and per-MAS agent/mcp_server app IDs
    mas_names: Dict[str, str] = {}  # mas_id -> mas_name
    mas_app_ids: Dict[str, Dict[str, Optional[str]]] = {}  # mas_id -> {agent_id, mcp_server_id}
    try:
        resp = requests.get(f"{config.backend_url}/mas", timeout=10)
        if resp.ok:
            for m in resp.json():
                mas_names[m["id"]] = m["name"]
                apps_resp = requests.get(f"{config.backend_url}/mas/{m['id']}/apps", timeout=10)
                if apps_resp.ok:
                    apps = apps_resp.json()
                    mas_app_ids[m["id"]] = {
                        "agent_id": next((a["id"] for a in apps if a["type"] == "agent"), None),
                        "mcp_server_id": next((a["id"] for a in apps if a["type"] == "mcp_server"), None),
                    }
    except Exception:
        pass  # fallback to generic scenarios if API unavailable

    # Per-MAS scenario sets keyed by name substring
    mas_scenarios: Dict[str, List[Dict]] = {
        "E-commerce": [
            {"tool": "search_products", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {"tool": "get_inventory", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {
                "tool": "process_payment",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "tool_not_selected_by_llm",
            },
            {
                "tool": "query_database",
                "blocked": True,
                "blocking_type": "AI_POWERED",
                "blocking_reason": "tool_intent_mismatch",
            },
            {
                "tool": "search_products",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "modified_mcp_tool_defs",
            },
        ],
        "Customer Support": [
            {"tool": "get_user_profile", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {"tool": "analyze_sentiment", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {
                "tool": "send_email",
                "blocked": True,
                "blocking_type": "AI_POWERED",
                "blocking_reason": "tool_intent_mismatch",
            },
            {
                "tool": "create_ticket",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "no_llm_calls_made_by_app",
            },
            {
                "tool": "get_user_profile",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "modified_mcp_tool_defs",
            },
        ],
        "Financial": [
            {"tool": "get_user_profile", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {"tool": "analyze_sentiment", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {
                "tool": "process_payment",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "no_llm_calls_made_by_app",
            },
            {
                "tool": "query_database",
                "blocked": True,
                "blocking_type": "AI_POWERED",
                "blocking_reason": "tool_parameters_mismatch",
            },
            {
                "tool": "analyze_sentiment",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "modified_mcp_tool_defs",
            },
        ],
        "DevOps": [
            {"tool": "get_build_status", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {"tool": "create_incident", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {
                "tool": "trigger_deploy",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "tool_not_selected_by_llm",
            },
            {
                "tool": "rollback_deployment",
                "blocked": True,
                "blocking_type": "AI_POWERED",
                "blocking_reason": "tool_intent_mismatch",
            },
            {
                "tool": "get_build_status",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "modified_mcp_tool_defs",
            },
        ],
        "Healthcare": [
            {"tool": "read_patient_record", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {"tool": "get_lab_results", "blocked": False, "blocking_type": None, "blocking_reason": None},
            {
                "tool": "write_prescription",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "tool_not_selected_by_llm",
            },
            {
                "tool": "schedule_appointment",
                "blocked": True,
                "blocking_type": "AI_POWERED",
                "blocking_reason": "tool_parameters_mismatch",
            },
            {
                "tool": "read_patient_record",
                "blocked": True,
                "blocking_type": "DETERMINISTIC",
                "blocking_reason": "modified_mcp_tool_defs",
            },
        ],
    }

    # Generic fallback scenarios
    fallback_scenarios: List[Dict] = [
        {"tool": "get_user_profile", "blocked": False, "blocking_type": None, "blocking_reason": None},
        {"tool": "analyze_sentiment", "blocked": False, "blocking_type": None, "blocking_reason": None},
        {
            "tool": "process_payment",
            "blocked": True,
            "blocking_type": "DETERMINISTIC",
            "blocking_reason": "tool_not_selected_by_llm",
        },
        {
            "tool": "query_database",
            "blocked": True,
            "blocking_type": "AI_POWERED",
            "blocking_reason": "tool_intent_mismatch",
        },
        {
            "tool": "get_user_profile",
            "blocked": True,
            "blocking_type": "DETERMINISTIC",
            "blocking_reason": "modified_mcp_tool_defs",
        },
    ]

    def _pick_scenarios(mas_id: Optional[str]) -> List[Dict]:
        if mas_id and mas_id in mas_names:
            name = mas_names[mas_id]
            for key, scenarios in mas_scenarios.items():
                if key in name:
                    return scenarios
        return fallback_scenarios

    inserted = 0
    now = datetime.now(timezone.utc)

    for user_input_id, mas_id, app_id in rows:
        ids = mas_app_ids.get(mas_id, {}) if mas_id else {}
        caller_id = ids.get("agent_id") or app_id
        callee_id = ids.get("mcp_server_id") or app_id
        for scenario in _pick_scenarios(mas_id):
            event_id = str(uuid.uuid4())
            event = {
                "id": event_id,
                "user_input_id": str(user_input_id),
                "created_at": now.isoformat(),
                "mas_id": mas_id,
                "app_id": app_id,
                "token": "",
                "caller_app_id": str(caller_id) if caller_id else "",
                "callee_app_id": str(callee_id) if callee_id else "",
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
            status = "blocked" if scenario["blocked"] else "approved"
            log_info(f"  {scenario['tool']} → {status} ({scenario.get('blocking_reason') or 'ok'})", config)
            inserted += 1

    cur.close()
    conn.close()

    log_success(f"Inserted {inserted} mock MCPCallStartedEvent traces")
    return True


def mock_scopes(config: Config) -> bool:
    """Insert mock scope-blocked MCPCallStartedEvent traces into the DB for dashboard testing.

    Fetches existing user_input_ids from the trace table and inserts MCPCallStartedEvent
    rows blocked due to insufficient_scope, simulating scope enforcement in the UI.
    """
    if psycopg2 is None:
        log_error("psycopg2 is required for --mock-scopes. Install it with: pip install psycopg2-binary")
        return False

    print(f"\n{Fore.BLUE}{Style.BRIGHT}=== Inserting Mock Scope-Blocked Traces ==={Style.RESET_ALL}\n")

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

    log_success(f"Found {len(rows)} existing token request(s) to attach mock scope traces to")

    # Fetch MAS names and per-MAS agent/mcp_server app IDs
    mas_names: Dict[str, str] = {}
    mas_app_ids: Dict[str, Dict[str, Optional[str]]] = {}
    try:
        resp = requests.get(f"{config.backend_url}/mas", timeout=10)
        if resp.ok:
            for m in resp.json():
                mas_names[m["id"]] = m["name"]
                apps_resp = requests.get(f"{config.backend_url}/mas/{m['id']}/apps", timeout=10)
                if apps_resp.ok:
                    apps = apps_resp.json()
                    mas_app_ids[m["id"]] = {
                        "agent_id": next((a["id"] for a in apps if a["type"] == "agent"), None),
                        "mcp_server_id": next((a["id"] for a in apps if a["type"] == "mcp_server"), None),
                    }
    except Exception:
        pass

    def _make_scope_blocked(tool: str) -> Dict:
        return {
            "tool": tool,
            "blocked": True,
            "blocking_type": "DETERMINISTIC",
            "blocking_reason": "insufficient_scope",
        }

    def _make_approved(tool: str) -> Dict:
        return {"tool": tool, "blocked": False, "blocking_type": None, "blocking_reason": None}

    mas_scenarios: Dict[str, List[Dict]] = {
        "E-commerce": [
            _make_approved("search_products"),
            _make_approved("get_inventory"),
            _make_scope_blocked("process_payment"),
            _make_scope_blocked("query_database"),
        ],
        "Customer Support": [
            _make_approved("get_user_profile"),
            _make_approved("analyze_sentiment"),
            _make_scope_blocked("send_email"),
            _make_scope_blocked("create_ticket"),
        ],
        "Financial": [
            _make_approved("get_user_profile"),
            _make_approved("analyze_sentiment"),
            _make_scope_blocked("process_payment"),
            _make_scope_blocked("query_database"),
        ],
        "DevOps": [
            _make_approved("get_build_status"),
            _make_approved("create_incident"),
            _make_scope_blocked("trigger_deploy"),
            _make_scope_blocked("rollback_deployment"),
        ],
        "Healthcare": [
            _make_approved("read_patient_record"),
            _make_approved("get_lab_results"),
            _make_scope_blocked("write_prescription"),
            _make_scope_blocked("schedule_appointment"),
        ],
    }

    fallback_scenarios: List[Dict] = [
        _make_approved("get_user_profile"),
        _make_approved("analyze_sentiment"),
        _make_scope_blocked("process_payment"),
        _make_scope_blocked("query_database"),
    ]

    def _pick_scenarios(mas_id: Optional[str]) -> List[Dict]:
        if mas_id and mas_id in mas_names:
            name = mas_names[mas_id]
            for key, scenarios in mas_scenarios.items():
                if key in name:
                    return scenarios
        return fallback_scenarios

    inserted = 0
    now = datetime.now(timezone.utc)

    for user_input_id, mas_id, app_id in rows:
        ids = mas_app_ids.get(mas_id, {}) if mas_id else {}
        caller_id = ids.get("agent_id") or app_id
        callee_id = ids.get("mcp_server_id") or app_id
        for scenario in _pick_scenarios(mas_id):
            event_id = str(uuid.uuid4())
            event = {
                "id": event_id,
                "user_input_id": str(user_input_id),
                "created_at": now.isoformat(),
                "mas_id": mas_id,
                "app_id": app_id,
                "token": "",
                "caller_app_id": str(caller_id) if caller_id else "",
                "callee_app_id": str(callee_id) if callee_id else "",
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
            status = "blocked (insufficient_scope)" if scenario["blocked"] else "approved"
            log_info(f"  {scenario['tool']} → {status}", config)
            inserted += 1

    cur.close()
    conn.close()

    log_success(f"Inserted {inserted} mock scope-blocked MCPCallStartedEvent traces")
    return True


def mock_llm(config: Config) -> bool:
    """Insert mock LLM call traces via the API for dashboard testing.

    For each MAS, fetches its client and agent apps, obtains tokens, then
    posts LLMCallStartedEvent and LLMCallEndedEvent traces through the live backend.
    Requires a running backend and Keycloak (same as --test-flow).
    """
    print(f"\n{Fore.BLUE}{Style.BRIGHT}=== Inserting Mock LLM Call Traces ==={Style.RESET_ALL}\n")

    if not check_backend_health(config):
        log_error("Backend is not accessible. Please ensure the server is running.")
        return False

    # Per-MAS prompt scenarios: (user_input, call_end_response, tool_name)
    mas_prompts: Dict[str, List[tuple]] = {
        "E-commerce": [
            ("Find me a laptop under $1000", "I will search for laptops under $1000", "search_products"),
            ("Is the blue shirt in stock?", "I will check the inventory for the blue shirt", "get_inventory"),
        ],
        "Customer Support": [
            (
                "I need help with my broken order",
                "I will create a support ticket for your order issue",
                "create_ticket",
            ),
            (
                "How satisfied is this customer?",
                "I will analyze the sentiment of the customer message",
                "analyze_sentiment",
            ),
        ],
        "Financial": [
            ("Show my last 10 transactions", "I will query your recent transactions", "query_database"),
            (
                "Transfer $500 to my savings account",
                "I will process the transfer to your savings account",
                "process_payment",
            ),
        ],
        "DevOps": [
            (
                "What is the status of the main branch build?",
                "I will check the build status for the main branch",
                "get_build_status",
            ),
            ("Deploy version 2.3.1 to staging", "I will trigger the deployment of v2.3.1 to staging", "trigger_deploy"),
        ],
        "Healthcare": [
            (
                "Pull up patient Jane Doe's record",
                "I will retrieve the patient record for Jane Doe",
                "read_patient_record",
            ),
            (
                "Schedule a follow-up for next Tuesday",
                "I will schedule a follow-up appointment",
                "schedule_appointment",
            ),
        ],
    }

    # Fetch all MAS
    try:
        resp = requests.get(f"{config.backend_url}/mas", timeout=10)
        resp.raise_for_status()
        all_mas = resp.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to fetch MAS list: {e}")
        return False

    if not all_mas:
        log_error("No MAS found. Run demo data generation first.")
        return False

    total_inserted = 0

    for mas in all_mas:
        mas_id = mas["id"]
        mas_name = mas["name"]

        # Find matching prompt set
        prompts = None
        for key, prompt_list in mas_prompts.items():
            if key in mas_name:
                prompts = prompt_list
                break
        if not prompts:
            log_warning(f"No prompt scenarios for MAS '{mas_name}' — skipping")
            continue

        # Fetch apps for this MAS
        try:
            apps_resp = requests.get(f"{config.backend_url}/mas/{mas_id}/apps", timeout=10)
            apps_resp.raise_for_status()
            apps = apps_resp.json()
        except requests.exceptions.RequestException as e:
            log_warning(f"Failed to fetch apps for MAS '{mas_name}': {e} — skipping")
            continue

        client_app = next((a for a in apps if a["type"] == "client"), None)
        agent_app = next((a for a in apps if a["type"] == "agent"), None)

        if not client_app or not agent_app:
            log_warning(f"MAS '{mas_name}' missing client or agent app — skipping")
            continue

        client_app_id = client_app["id"]

        realm = _get_mas_realm(mas_id, config)
        if not realm:
            log_warning(f"Could not determine Keycloak realm for MAS '{mas_name}' — skipping")
            continue

        client_creds = _get_app_credentials(client_app_id, realm, config)
        if not client_creds:
            log_warning(f"Could not fetch credentials for client app in MAS '{mas_name}' — skipping")
            continue

        print(f"\n{Fore.CYAN}MAS: {mas_name}{Style.RESET_ALL}")

        for user_input, llm_response, tool_name in prompts:
            call_id = str(uuid.uuid4())

            # Step 1: Get client token
            try:
                token_resp = requests.post(
                    f"{config.backend_url}/{client_app_id}/oauth2/token",
                    data={
                        "client_id": client_creds["client_id"],
                        "client_secret": client_creds["client_secret"],
                        "user_input": user_input,
                    },
                    timeout=30,
                )
                token_resp.raise_for_status()
                client_token = token_resp.json()["access_token"]
            except requests.exceptions.RequestException as e:
                log_warning(f"  Failed to get token for '{user_input[:40]}': {e}")
                continue

            # Step 2: LLM call started
            try:
                requests.post(
                    f"{config.backend_url}/trace/llm/call_start",
                    json={"call_id": call_id, "prompt": user_input},
                    headers={"Authorization": f"Bearer {client_token}"},
                    timeout=10,
                ).raise_for_status()
            except requests.exceptions.RequestException as e:
                log_warning(f"  Failed to record call_start for '{user_input[:40]}': {e}")
                continue

            # Step 3: LLM call ended (selected a tool)
            try:
                requests.post(
                    f"{config.backend_url}/trace/llm/call_end",
                    json={
                        "call_id": call_id,
                        "response": llm_response,
                        "tools": f"[Tool(name='{tool_name}')]",
                    },
                    headers={"Authorization": f"Bearer {client_token}"},
                    timeout=10,
                ).raise_for_status()
            except requests.exceptions.RequestException as e:
                log_warning(f"  Failed to record call_end for '{user_input[:40]}': {e}")
                continue

            log_info(f"  '{user_input[:50]}' → {tool_name}", config)
            log_success(f"  Inserted LLM trace pair for: {user_input[:50]}")
            total_inserted += 1

    if total_inserted == 0:
        log_error("No LLM traces inserted. Check that MAS and apps exist and credentials are accessible.")
        return False

    log_success(f"Inserted {total_inserted} LLM call trace pairs")
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
  python create_demo_data.py --mock-scopes --verbose
  python create_demo_data.py --mock-llm --verbose
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
    parser.add_argument(
        "--mock-scopes",
        action="store_true",
        help="Insert mock scope-blocked MCPCallStartedEvent traces into the DB for dashboard testing",
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Insert mock LLM call traces via the API for dashboard testing (requires live backend + Keycloak)",
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
        elif args.mock_scopes:
            success = mock_scopes(config)
        elif args.mock_llm:
            success = mock_llm(config)
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
