# K8s CRD API Test Collection (curl)

This document provides curl commands for testing the K8s CRD REST APIs.

## Setup

```bash
# Set base URL
export API_BASE="http://localhost:3000"

# Optional: Set auth token if auth is enabled
export AUTH_TOKEN="your-token-here"
```

## MultiAgentSystem CRD Operations

### 1. Create a MultiAgentSystem

```bash
curl -X POST "${API_BASE}/k8s/namespaces/default/multiagentsystems" \
  -H "Content-Type: application/json" \
  -d '{
    "apiVersion": "zta.io/v1alpha1",
    "kind": "MultiAgentSystem",
    "metadata": {
      "name": "prod-mas",
      "namespace": "default",
      "labels": {
        "environment": "production",
        "team": "platform"
      }
    },
    "spec": {
      "name": "Production Multi-Agent System",
      "authorizationServer": "production-realm",
      "enabledToolChecks": [
        "DETERMINISTIC_TOOL_SELECTED",
        "DETERMINISTIC_LLM_SELECTED_TOOLS",
        "AI_POWERED_TOOL_MATCH"
      ],
      "apps": [
        {
          "name": "orchestrator-agent",
          "type": "agent",
          "baseUrl": "http://orchestrator-agent.default.svc.cluster.local:8000"
        },
        {
          "name": "filesystem-mcp",
          "type": "mcp_server",
          "baseUrl": "http://filesystem-mcp.default.svc.cluster.local:8080"
        },
        {
          "name": "user-app",
          "type": "client",
          "baseUrl": "http://user-app.default.svc.cluster.local:8000"
        }
      ]
    }
  }'
```

### 2. Get a Specific MultiAgentSystem

```bash
curl -X GET "${API_BASE}/k8s/namespaces/default/multiagentsystems/prod-mas"
```

### 3. List MultiAgentSystems in a Namespace

```bash
curl -X GET "${API_BASE}/k8s/namespaces/default/multiagentsystems"
```

### 4. List All MultiAgentSystems (All Namespaces)

```bash
curl -X GET "${API_BASE}/k8s/multiagentsystems"
```

### 5. List MultiAgentSystems with Namespace Filter

```bash
curl -X GET "${API_BASE}/k8s/multiagentsystems?namespace=production"
```

### 6. Update a MultiAgentSystem Spec

```bash
curl -X PUT "${API_BASE}/k8s/namespaces/default/multiagentsystems/prod-mas" \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "name": "Production MAS (Updated)",
      "authorizationServer": "production-realm",
      "enabledToolChecks": [
        "DETERMINISTIC_TOOL_SELECTED",
        "AI_POWERED_TOOL_MATCH"
      ],
      "apps": [
        {
          "name": "orchestrator-agent",
          "type": "agent",
          "baseUrl": "http://orchestrator-agent.default.svc.cluster.local:8000"
        }
      ]
    }
  }'
```

### 7. Update MultiAgentSystem Status (Operator Use)

```bash
curl -X PATCH "${API_BASE}/k8s/namespaces/default/multiagentsystems/prod-mas/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": {
      "phase": "Active",
      "appsReady": 3,
      "lastSyncTime": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
      "message": "All apps successfully reconciled"
    }
  }'
```

### 8. Delete a MultiAgentSystem

```bash
curl -X DELETE "${API_BASE}/k8s/namespaces/default/multiagentsystems/prod-mas"
```

## ZTAPolicy CRD Operations

### 1. Create a ZTAPolicy

```bash
curl -X POST "${API_BASE}/k8s/namespaces/default/ztapolicies" \
  -H "Content-Type: application/json" \
  -d '{
    "apiVersion": "zta.io/v1alpha1",
    "kind": "ZTAPolicy",
    "metadata": {
      "name": "agent-policy",
      "namespace": "default",
      "labels": {
        "app": "orchestrator-agent"
      }
    },
    "spec": {
      "targetRef": {
        "kind": "Deployment",
        "name": "orchestrator-agent"
      },
      "allowedProtocols": ["mcp", "a2a"],
      "allowedEndpoints": [
        {
          "name": "filesystem-mcp",
          "namespace": "default",
          "port": 8080
        },
        {
          "name": "database-mcp",
          "namespace": "default",
          "port": 8080
        },
        {
          "name": "zta-auth-service",
          "namespace": "zta-control-plane",
          "port": 8443
        }
      ],
      "llmEndpoint": {
        "fqdn": "api.openai.com",
        "port": 443
      }
    }
  }'
```

### 2. Get a Specific ZTAPolicy

```bash
curl -X GET "${API_BASE}/k8s/namespaces/default/ztapolicies/agent-policy"
```

### 3. List ZTAPolicies in a Namespace

```bash
curl -X GET "${API_BASE}/k8s/namespaces/default/ztapolicies"
```

### 4. List All ZTAPolicies (All Namespaces)

```bash
curl -X GET "${API_BASE}/k8s/ztapolicies"
```

### 5. Update a ZTAPolicy Spec

```bash
curl -X PUT "${API_BASE}/k8s/namespaces/default/ztapolicies/agent-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "targetRef": {
        "kind": "Deployment",
        "name": "orchestrator-agent"
      },
      "allowedProtocols": ["mcp"],
      "allowedEndpoints": [
        {
          "name": "filesystem-mcp",
          "namespace": "default",
          "port": 8080
        }
      ]
    }
  }'
```

### 6. Update ZTAPolicy Status (Operator Use)

```bash
curl -X PATCH "${API_BASE}/k8s/namespaces/default/ztapolicies/agent-policy/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": {
      "phase": "Active",
      "ciliumPolicyName": "cnp-agent-policy",
      "lastSyncTime": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
      "message": "CiliumNetworkPolicy applied successfully"
    }
  }'
```

### 7. Delete a ZTAPolicy

```bash
curl -X DELETE "${API_BASE}/k8s/namespaces/default/ztapolicies/agent-policy"
```

## Testing Scenarios

### Scenario 1: Create Complete MAS with Validation

```bash
# Create MAS
curl -X POST "${API_BASE}/k8s/namespaces/test/multiagentsystems" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "apiVersion": "zta.io/v1alpha1",
  "kind": "MultiAgentSystem",
  "metadata": {
    "name": "test-mas",
    "namespace": "test"
  },
  "spec": {
    "name": "Test MAS",
    "authorizationServer": "test-realm",
    "enabledToolChecks": ["DETERMINISTIC_TOOL_SELECTED"],
    "apps": [
      {
        "name": "test-agent",
        "type": "agent",
        "baseUrl": "http://test-agent:8000"
      }
    ]
  }
}
EOF

# Verify it was created
curl -X GET "${API_BASE}/k8s/namespaces/test/multiagentsystems/test-mas"

# Update status (simulate operator)
curl -X PATCH "${API_BASE}/k8s/namespaces/test/multiagentsystems/test-mas/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": {
      "phase": "Active",
      "appsReady": 1,
      "lastSyncTime": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
    }
  }'

# List all to verify
curl -X GET "${API_BASE}/k8s/namespaces/test/multiagentsystems"
```

### Scenario 2: Policy Creation and Update

```bash
# Create policy
curl -X POST "${API_BASE}/k8s/namespaces/test/ztapolicies" \
  -H "Content-Type: application/json" \
  -d '{
    "apiVersion": "zta.io/v1alpha1",
    "kind": "ZTAPolicy",
    "metadata": {
      "name": "test-policy",
      "namespace": "test"
    },
    "spec": {
      "targetRef": {
        "kind": "Deployment",
        "name": "test-agent"
      },
      "allowedProtocols": ["mcp"],
      "allowedEndpoints": []
    }
  }'

# Get policy
curl -X GET "${API_BASE}/k8s/namespaces/test/ztapolicies/test-policy"

# Update to add LLM endpoint
curl -X PUT "${API_BASE}/k8s/namespaces/test/ztapolicies/test-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "targetRef": {
        "kind": "Deployment",
        "name": "test-agent"
      },
      "allowedProtocols": ["mcp"],
      "allowedEndpoints": [],
      "llmEndpoint": {
        "fqdn": "api.openai.com",
        "port": 443
      }
    }
  }'
```

### Scenario 3: Error Handling

```bash
# Try invalid app type (should get 422)
curl -X POST "${API_BASE}/k8s/namespaces/test/multiagentsystems" \
  -H "Content-Type: application/json" \
  -d '{
    "apiVersion": "zta.io/v1alpha1",
    "kind": "MultiAgentSystem",
    "metadata": {"name": "bad-mas", "namespace": "test"},
    "spec": {
      "name": "Bad MAS",
      "authorizationServer": "test-realm",
      "apps": [
        {
          "name": "bad-app",
          "type": "invalid_type",
          "baseUrl": "http://bad:8000"
        }
      ]
    }
  }'

# Try to get non-existent resource (should get 404)
curl -X GET "${API_BASE}/k8s/namespaces/test/multiagentsystems/does-not-exist"

# Try invalid target ref kind (should get 422)
curl -X POST "${API_BASE}/k8s/namespaces/test/ztapolicies" \
  -H "Content-Type: application/json" \
  -d '{
    "apiVersion": "zta.io/v1alpha1",
    "kind": "ZTAPolicy",
    "metadata": {"name": "bad-policy", "namespace": "test"},
    "spec": {
      "targetRef": {
        "kind": "InvalidKind",
        "name": "test"
      },
      "allowedProtocols": ["mcp"],
      "allowedEndpoints": []
    }
  }'
```

## Cleanup

```bash
# Delete all test resources
curl -X DELETE "${API_BASE}/k8s/namespaces/test/multiagentsystems/test-mas"
curl -X DELETE "${API_BASE}/k8s/namespaces/test/ztapolicies/test-policy"
```

## Tips

1. **Pretty print JSON responses**: Add `| jq` to any curl command
   ```bash
   curl -X GET "${API_BASE}/k8s/namespaces/default/multiagentsystems" | jq
   ```

2. **Save response to file**:
   ```bash
   curl -X GET "${API_BASE}/k8s/namespaces/default/multiagentsystems/prod-mas" > mas-prod.json
   ```

3. **Check HTTP status only**:
   ```bash
   curl -X GET "${API_BASE}/k8s/namespaces/default/multiagentsystems/prod-mas" -w "%{http_code}\n" -o /dev/null -s
   ```

4. **Verbose output for debugging**:
   ```bash
   curl -v -X POST "${API_BASE}/k8s/namespaces/default/multiagentsystems" -d @payload.json
   ```
