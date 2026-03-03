# ZTA Identity Auth Server Scripts

This directory contains utility scripts for managing and populating the ZTA Identity Auth Server.

## Demo Data Generator

The `create_demo_data.py` script generates realistic demo data for testing and demonstration purposes.

### Prerequisites

1. **Backend must be running**: Ensure the ZTA Identity Auth Server is running (typically at `http://localhost:8000`)

2. **Python dependencies**: Install required packages:
   ```bash
   pip install requests python-dotenv colorama
   ```

   Or if you're using the project's virtual environment:
   ```bash
   source ../.venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install requests python-dotenv colorama
   ```

### Usage

#### Using Make Commands (Recommended)

The easiest way to run the script is using the provided Make commands:

```bash
# Preview what would be created (dry-run)
make demo-data-dry-run

# Create demo data
make demo-data

# Clear all data and create fresh demo data
make demo-data-clear
```

#### Direct Python Usage

Alternatively, you can run the script directly:

```bash
# Basic usage (create demo data)
python create_demo_data.py --verbose

# Preview without creating (dry-run)
python create_demo_data.py --dry-run

# Clear existing data and create new
python create_demo_data.py --clear --verbose

# Use custom backend URL
python create_demo_data.py --backend-url http://localhost:8000
```

Or with the project's virtual environment:
```bash
.venv/bin/python create_demo_data.py --verbose
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--backend-url URL` | Backend API URL (default: `http://localhost:8000`) |
| `--verbose`, `-v` | Enable verbose logging |
| `--dry-run` | Preview what would be created without actually creating anything |
| `--clear` | Delete all existing data before creating new demo data |
| `--help`, `-h` | Show help message |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BACKEND_URL` | Backend API URL | `http://localhost:8000` |

Example:
```bash
export BACKEND_URL=http://localhost:8000
python create_demo_data.py --verbose
```

### What Data is Created

The script creates the following demo data:

#### Multi-Agent Systems (MAS)
- **E-commerce Platform** - Online shopping system
- **Customer Support System** - Support ticket management
- **Financial Services** - Financial transaction processing

#### Applications
Each MAS includes multiple apps of different types:

- **Agent apps** (e.g., "Shopping Assistant Agent", "Support Agent")
- **Client apps** (e.g., "Web Dashboard", "Support Portal")
- **MCP Server apps** (e.g., "Product Database MCP", "Transaction Database MCP")

#### Tools
Each app includes realistic tools with JSON schemas:
- `get_user_profile` - Retrieve user information
- `search_products` - Search product catalog
- `process_payment` - Handle payments
- `send_email` - Send email notifications
- `query_database` - Execute database queries
- `analyze_sentiment` - Analyze text sentiment
- `create_ticket` - Create support tickets
- `get_inventory` - Check inventory levels

#### Scopes
Authorization scopes for access control:
- `read:products`, `write:products`
- `read:orders`, `write:orders`
- `read:users`, `write:users`
- `read:tickets`, `write:tickets`
- `process:payments`
- `send:notifications`
- `execute:admin`

### Examples

1. **First time setup - create demo data:**
   ```bash
   make demo-data
   # or
   python create_demo_data.py --verbose
   ```

2. **Preview before creating:**
   ```bash
   make demo-data-dry-run
   # or
   python create_demo_data.py --dry-run
   ```

3. **Reset and recreate data:**
   ```bash
   make demo-data-clear
   # or
   python create_demo_data.py --clear --verbose
   ```

4. **Use with Docker backend:**
   ```bash
   python create_demo_data.py --backend-url http://localhost:8000 --verbose
   ```

### Output

The script provides colored, structured output:

```
=== ZTA Identity Auth Server Demo Data Generator ===

✓ Backend is accessible at http://localhost:8000

Planning to create:
  • 3 Multi-Agent Systems
  • 7 Applications
  • 15 Scopes

────────────────────────────────────────────────────────────
MAS: E-commerce Platform
────────────────────────────────────────────────────────────

✓ Created MAS: E-commerce Platform (ID: 123e4567-e89b...)

Creating Scopes...
✓ Created Scope: read:products (ID: 234e5678-f90a...)
✓ Created Scope: write:products (ID: 345e6789-01ab...)
...

Creating Applications...
✓ Created App: Shopping Assistant Agent (ID: 456e789a-12bc...)
...

============================================================
Summary
============================================================

✓ Successfully created: 25 items
```

### Troubleshooting

#### Backend not accessible
```
✗ Cannot connect to backend at http://localhost:8000: ...
```

**Solution:** Ensure the backend server is running:
```bash
# Start the backend
make run
# or
uvicorn identity_auth_server.api.app:app --reload
```

#### Import errors
```
Error: 'requests' library not found. Install it with: pip install requests
```

**Solution:** Install required dependencies:
```bash
pip install requests python-dotenv colorama
```

#### Permission denied
```
Permission denied: ./create_demo_data.py
```

**Solution:** Make the script executable:
```bash
chmod +x create_demo_data.py
./create_demo_data.py --verbose
```

### Verification

After running the script, verify the data in the ZTA Explorer UI:

1. Open `http://localhost:5173` (or your UI URL)
2. Navigate to the **MAS** page - you should see 3 MAS instances
3. Click on each MAS to view its associated apps
4. Navigate to the **Applications** page - you should see all created apps
5. Navigate to the **Scopes** page - you should see all created scopes

### Notes

- The script uses the backend REST API, so all data validation and business logic from the backend is applied
- Each MAS automatically gets its own Authorization Server (Keycloak realm)
- Apps are automatically assigned client credentials for OAuth2 authentication
- Tools are linked to scopes for fine-grained authorization
- The `--clear` flag will delete ALL data, not just demo data - use with caution in non-development environments

### Development

To modify the demo data:

1. Edit the `get_sample_mas_configs()` function to add/modify MAS configurations
2. Edit the `get_sample_tool_schemas()` function to add new tool types
3. Update scopes and app configurations as needed

Example adding a new MAS:
```python
{
    "name": "Your New MAS",
    "scopes": ["read:data", "write:data"],
    "apps": [
        {
            "type": "agent",
            "name": "Your Agent",
            "base_url": "https://example.com/agent",
            "tools": [...]
        }
    ]
}
```
