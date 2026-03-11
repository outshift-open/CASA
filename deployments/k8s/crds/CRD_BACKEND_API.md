# Kubernetes CRD Backend APIs

## Overview

This document describes the backend REST APIs that support Kubernetes Custom Resource Definitions (CRDs) for the Zero Trust Architecture Multi-Agent System (ZTA-MAS). These APIs enable Kubernetes Operators to interact with the ZTA control plane to reconcile CRD resources.

## Architecture

The CRD backend APIs bridge Kubernetes-native resource management with the existing ZTA backend services:

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ZTA Operator (controller-runtime)                    │  │
│  │  - Watches MultiAgentSystem and ZTAPolicy CRDs        │  │
│  │  - Calls backend APIs for reconciliation              │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │ HTTP/REST                                 │
└──────────────────┼───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              ZTA Backend (identity-auth-server)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  /k8s/mas/* - MultiAgentSystem CRD APIs               │  │
│  │  /k8s/policies/* - ZTAPolicy CRD APIs                 │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │                                           │
│  ┌───────────────▼───────────────────────────────────────┐  │
│  │  K8sCRDService                                         │  │
│  │  - Converts CRD specs to internal models              │  │
│  │  - Manages MAS lifecycle                              │  │
│  │  - Updates CRD status                                 │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │                                           │
│  ┌───────────────▼───────────────────────────────────────┐  │
│  │  Existing Services (MAS, App, AuthServer)             │  │
│  │  - Database persistence                               │  │
│  │  - Keycloak integration                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Custom Resource Definitions

### 1. MultiAgentSystem CRD

The `MultiAgentSystem` CRD represents a complete multi-agent system with its applications, authorization server, and tool check configuration.

**API Group**: `zta.io`  
**Version**: `v1alpha1`  
**Kind**: `MultiAgentSystem`  
**Short Name**: `mas`

#### Spec Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable name for the MAS |
| `authorizationServer` | string | Yes | Keycloak realm name |
| `enabledToolChecks` | array[string] | No | List of enabled tool authorization checks |
| `apps` | array[object] | No | List of applications in this MAS |

**Tool Check Options**:
- `DETERMINISTIC_TOOL_SELECTED` - Basic deterministic tool authorization
- `DETERMINISTIC_LLM_SELECTED_TOOLS` - Check tools selected by LLM
- `AI_POWERED_TOOL_MATCH` - AI-powered tool intent matching

**App Object**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique application name |
| `type` | string | Yes | Application type: `agent`, `client`, or `mcp_server` |
| `baseUrl` | string | Yes | Service URL (e.g., `http://service.namespace.svc.cluster.local:8000`) |

#### Status Fields

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Current phase: `Pending`, `Active`, `Failed` |
| `appsReady` | integer | Number of successfully configured apps |
| `lastSyncTime` | string (datetime) | Timestamp of last reconciliation |
| `message` | string | Human-readable status message |

#### Example

```yaml
apiVersion: zta.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: production-mas
  namespace: production-mas
spec:
  name: "Production Multi-Agent System"
  authorizationServer: "production-realm"
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  - DETERMINISTIC_LLM_SELECTED_TOOLS
  - AI_POWERED_TOOL_MATCH
  apps:
  - name: user-app
    type: client
    baseUrl: "http://user-app.production-mas.svc.cluster.local:8000"
  - name: orchestrator-agent
    type: agent
    baseUrl: "http://orchestrator-agent.production-mas.svc.cluster.local:8000"
  - name: filesystem-mcp
    type: mcp_server
    baseUrl: "http://filesystem-mcp.production-mas.svc.cluster.local:8080"
```

### 2. ZTAPolicy CRD

The `ZTAPolicy` CRD defines network and protocol policies for workloads, which are translated into CiliumNetworkPolicies.

**API Group**: `zta.io`  
**Version**: `v1alpha1`  
**Kind**: `ZTAPolicy`  
**Short Name**: `ztap`

#### Spec Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `targetRef` | object | Yes | Reference to target workload |
| `allowedProtocols` | array[string] | No | Allowed protocols: `mcp`, `a2a`, `http` |
| `allowedEndpoints` | array[object] | No | List of allowed destination endpoints |
| `llmEndpoint` | object | No | External LLM endpoint configuration |

**Target Reference**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | Workload kind: `Deployment`, `StatefulSet`, `Pod` |
| `name` | string | Yes | Workload name |

**Allowed Endpoint**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Target service name |
| `namespace` | string | Yes | Target namespace |
| `port` | integer | Yes | Port number |

**LLM Endpoint**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fqdn` | string | Yes | Fully qualified domain name |
| `port` | integer | Yes | Port number |

#### Status Fields

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Current phase: `Pending`, `Active`, `Failed` |
| `ciliumPolicyName` | string | Name of generated CiliumNetworkPolicy |
| `lastSyncTime` | string (datetime) | Timestamp of last reconciliation |
| `message` | string | Human-readable status message |

#### Example

```yaml
apiVersion: zta.io/v1alpha1
kind: ZTAPolicy
metadata:
  name: agent-policy
  namespace: production-mas
spec:
  targetRef:
    kind: Deployment
    name: orchestrator-agent
  allowedProtocols:
  - mcp
  - a2a
  allowedEndpoints:
  - name: filesystem-mcp
    namespace: production-mas
    port: 8080
  - name: zta-auth-service
    namespace: zta-control-plane
    port: 8443
  llmEndpoint:
    fqdn: api.openai.com
    port: 443
```

## REST API Endpoints

### MultiAgentSystem CRD APIs

#### Create or Update MultiAgentSystem

```http
POST /k8s/mas
Content-Type: application/json
```

**Request Body**:
```json
{
  "apiVersion": "zta.io/v1alpha1",
  "kind": "MultiAgentSystem",
  "metadata": {
    "name": "production-mas",
    "namespace": "production-mas"
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
        "name": "user-app",
        "type": "client",
        "baseUrl": "http://user-app.production-mas.svc.cluster.local:8000"
      }
    ]
  }
}
```

**Response** (200 OK):
```json
{
  "apiVersion": "zta.io/v1alpha1",
  "kind": "MultiAgentSystem",
  "metadata": {
    "name": "production-mas",
    "namespace": "production-mas"
  },
  "spec": { ... },
  "status": {
    "phase": "Active",
    "appsReady": 1,
    "lastSyncTime": "2025-01-15T10:30:00Z",
    "message": "Successfully created MAS with 1 apps"
  }
}
```

#### Get MultiAgentSystem

```http
GET /k8s/mas/{namespace}/{name}
```

**Response** (200 OK): Full MultiAgentSystem resource with status

#### List MultiAgentSystems

```http
GET /k8s/mas
```

**Optional Query Parameters**:
- `namespace` - Filter by namespace

**Response** (200 OK):
```json
{
  "items": [
    { ... MultiAgentSystem resource ... }
  ]
}
```

#### Delete MultiAgentSystem

```http
DELETE /k8s/mas/{namespace}/{name}
```

**Response** (200 OK):
```json
{
  "message": "MultiAgentSystem 'production-mas' deleted successfully"
}
```

#### Update MultiAgentSystem Status

```http
PATCH /k8s/mas/{namespace}/{name}/status
Content-Type: application/json
```

**Request Body**:
```json
{
  "status": {
    "phase": "Active",
    "appsReady": 3,
    "lastSyncTime": "2025-01-15T10:35:00Z",
    "message": "All apps configured successfully"
  }
}
```

**Response** (200 OK): Updated MultiAgentSystem resource

### ZTAPolicy CRD APIs

#### Create or Update ZTAPolicy

```http
POST /k8s/policies
Content-Type: application/json
```

**Request Body**:
```json
{
  "apiVersion": "zta.io/v1alpha1",
  "kind": "ZTAPolicy",
  "metadata": {
    "name": "agent-policy",
    "namespace": "production-mas"
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
        "namespace": "production-mas",
        "port": 8080
      }
    ],
    "llmEndpoint": {
      "fqdn": "api.openai.com",
      "port": 443
    }
  }
}
```

**Response** (200 OK):
```json
{
  "apiVersion": "zta.io/v1alpha1",
  "kind": "ZTAPolicy",
  "metadata": { ... },
  "spec": { ... },
  "status": {
    "phase": "Active",
    "ciliumPolicyName": "agent-policy-cilium",
    "lastSyncTime": "2025-01-15T10:30:00Z",
    "message": "CiliumNetworkPolicy generated successfully"
  }
}
```

#### Get ZTAPolicy

```http
GET /k8s/policies/{namespace}/{name}
```

**Response** (200 OK): Full ZTAPolicy resource with status

#### List ZTAPolicies

```http
GET /k8s/policies
```

**Optional Query Parameters**:
- `namespace` - Filter by namespace

#### Delete ZTAPolicy

```http
DELETE /k8s/policies/{namespace}/{name}
```

**Response** (200 OK):
```json
{
  "message": "ZTAPolicy 'agent-policy' deleted successfully"
}
```

#### Update ZTAPolicy Status

```http
PATCH /k8s/policies/{namespace}/{name}/status
Content-Type: application/json
```

**Request Body**:
```json
{
  "status": {
    "phase": "Active",
    "ciliumPolicyName": "agent-policy-cilium",
    "lastSyncTime": "2025-01-15T10:35:00Z",
    "message": "Policy reconciled successfully"
  }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request body: missing required field 'name'"
}
```

### 404 Not Found
```json
{
  "detail": "MultiAgentSystem 'production-mas' not found in namespace 'production-mas'"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: failed to create Keycloak realm"
}
```

## Operator Integration

### Typical Reconciliation Flow

1. **Watch CRD Events**: Operator watches for MultiAgentSystem and ZTAPolicy changes
2. **Call Backend API**: On create/update, operator calls `POST /k8s/mas` or `POST /k8s/policies`
3. **Backend Processing**:
   - Validates CRD spec
   - Creates/updates internal resources (MAS, apps, authorization servers)
   - Integrates with Keycloak
   - Returns updated resource with status
4. **Update CRD Status**: Operator updates Kubernetes CRD status via `PATCH` endpoint
5. **Generate Network Policies**: For ZTAPolicy, operator generates CiliumNetworkPolicy manifests

### Example Operator Code (Go)

```go
func (r *MultiAgentSystemReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // Get CRD from Kubernetes
    mas := &ztav1alpha1.MultiAgentSystem{}
    if err := r.Get(ctx, req.NamespacedName, mas); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Call backend API
    resp, err := r.BackendClient.CreateOrUpdateMAS(ctx, mas)
    if err != nil {
        // Update status to Failed
        mas.Status.Phase = "Failed"
        mas.Status.Message = err.Error()
        r.Status().Update(ctx, mas)
        return ctrl.Result{}, err
    }

    // Update CRD status from backend response
    mas.Status = resp.Status
    if err := r.Status().Update(ctx, mas); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}
```

## Implementation Details

### Service Layer

The `K8sCRDService` handles:
- **CRD to Model Conversion**: Converts Kubernetes CRD specs to internal database models
- **MAS Lifecycle Management**: Creates/updates/deletes Multi-Agent Systems
- **App Registration**: Registers apps with Keycloak and internal database
- **Tool Check Configuration**: Maps CRD tool check flags to internal bitmask
- **Status Management**: Tracks reconciliation status and app readiness

### Database Schema

The CRD APIs reuse existing database tables:
- `MultiAgentSystem` - Stores MAS configuration
- `App` - Stores application definitions
- `AuthorizationServer` - Stores Keycloak realm information
- `Scope` - Stores scopes and tool mappings

### Keycloak Integration

For each MultiAgentSystem:
1. Create Keycloak realm (if not exists)
2. Create client credentials for each app
3. Configure scopes and roles
4. Store client credentials in database

## Testing

### Manual Testing with curl

```bash
# Create MultiAgentSystem
curl -X POST http://localhost:3000/k8s/mas \
  -H "Content-Type: application/json" \
  -d @multiagentsystem-example.json

# Get MultiAgentSystem
curl http://localhost:3000/k8s/mas/production-mas/production-mas

# List all MAS
curl http://localhost:3000/k8s/mas

# Delete MultiAgentSystem
curl -X DELETE http://localhost:3000/k8s/mas/production-mas/production-mas
```

### Testing with Python SDK

```python
from identity_auth_sdk import Client

client = Client(base_url="http://localhost:3000")

# Create MAS via CRD API
mas_resource = {
    "apiVersion": "zta.io/v1alpha1",
    "kind": "MultiAgentSystem",
    "metadata": {"name": "test-mas", "namespace": "default"},
    "spec": {
        "name": "Test MAS",
        "authorizationServer": "test-realm",
        "apps": [
            {
                "name": "test-client",
                "type": "client",
                "baseUrl": "http://test-client:8000"
            }
        ]
    }
}

response = client.post("/k8s/mas", json=mas_resource)
print(response.json())
```

## Files

- **CRD Definitions**: `docs/k8s/multiagentsystem-crd.yaml`, `docs/k8s/ztapolicy-crd.yaml`
- **Example Resources**: `docs/k8s/multiagentsystem-examples.yaml`, `docs/k8s/ztapolicy-examples.yaml`
- **Data Models**: `src/identity_auth_server/core/k8s_types.py`
- **Service Layer**: `src/identity_auth_server/services/k8s_crd_service.py`
- **API Routes**: `src/identity_auth_server/api/routes/k8s_crd.py`

## Related Documentation

- [SPECS.md §7.2](../../SPECS.md#72-custom-resource-definitions-crds) - CRD Architecture Specification
- [BUILD.md](../../BUILD.md) - Existing ZTA Architecture
- [Developer_notes.md](../Developer_notes.md) - Development Guide

## Future Enhancements

1. **Webhook Validation**: Add Kubernetes admission webhooks to validate CRD specs
2. **OpenAPI v3 Schema**: Generate OpenAPI schema from CRD definitions
3. **Watch API**: Implement watch/streaming endpoints for real-time updates
4. **Batch Operations**: Support bulk create/update/delete operations
5. **Dry-Run Mode**: Support `?dryRun=true` for validation without side effects
