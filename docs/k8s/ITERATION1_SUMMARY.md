# CRD Backend Implementation - Iteration 1 Summary

## Overview

This iteration implements the backend REST APIs and data models to support Kubernetes Custom Resource Definitions (CRDs) for the Zero Trust Architecture Multi-Agent System (ZTA-MAS), as specified in SPECS.md §7.2.

## What Was Implemented

### 1. Data Models (`src/identity_auth_server/core/k8s_types.py`)

Created Pydantic models for two CRDs:

#### MultiAgentSystem CRD Models
- `MultiAgentSystemMetadata` - Kubernetes metadata (name, namespace)
- `MASAppSpec` - Application specification within a MAS
- `MultiAgentSystemSpec` - MAS configuration (name, realm, tool checks, apps)
- `MultiAgentSystemStatus` - Reconciliation status (phase, apps ready, sync time)
- `MultiAgentSystemResource` - Complete CRD resource (apiVersion, kind, metadata, spec, status)

#### ZTAPolicy CRD Models
- `ZTAPolicyMetadata` - Kubernetes metadata
- `TargetRef` - Reference to target workload (Deployment/StatefulSet/Pod)
- `AllowedEndpoint` - Allowed destination endpoint
- `LLMEndpoint` - External LLM configuration
- `ZTAPolicySpec` - Policy configuration (protocols, endpoints, LLM access)
- `ZTAPolicyStatus` - Reconciliation status (phase, Cilium policy name, sync time)
- `ZTAPolicyResource` - Complete CRD resource

### 2. Service Layer (`src/identity_auth_server/services/k8s_crd_service.py`)

Created `K8sCRDService` with the following capabilities:

**MultiAgentSystem Management**:
- `create_or_update_mas()` - Convert CRD spec to internal MAS, create Keycloak realm, register apps
- `get_mas()` - Retrieve MAS and convert to CRD format
- `list_mas()` - List all MAS resources (optional namespace filter)
- `delete_mas()` - Delete MAS and clean up Keycloak realm
- `update_mas_status()` - Update CRD status after reconciliation

**ZTAPolicy Management**:
- `create_or_update_policy()` - Store policy configuration and generate Cilium policy name
- `get_policy()` - Retrieve policy and convert to CRD format
- `list_policies()` - List all policies (optional namespace filter)
- `delete_policy()` - Delete policy
- `update_policy_status()` - Update policy status after reconciliation

**Key Features**:
- Converts CRD specs to internal database models
- Integrates with existing MAS and App services
- Maps tool check flags (CRD enum → internal bitmask)
- Manages status updates for operator feedback

### 3. REST API Endpoints (`src/identity_auth_server/api/routes/k8s_crd.py`)

Created FastAPI routes under `/k8s` prefix:

**MultiAgentSystem Endpoints**:
- `POST /k8s/mas` - Create or update MAS
- `GET /k8s/mas/{namespace}/{name}` - Get specific MAS
- `GET /k8s/mas` - List all MAS (with optional `?namespace=` filter)
- `DELETE /k8s/mas/{namespace}/{name}` - Delete MAS
- `PATCH /k8s/mas/{namespace}/{name}/status` - Update MAS status

**ZTAPolicy Endpoints**:
- `POST /k8s/policies` - Create or update policy
- `GET /k8s/policies/{namespace}/{name}` - Get specific policy
- `GET /k8s/policies` - List all policies (with optional `?namespace=` filter)
- `DELETE /k8s/policies/{namespace}/{name}` - Delete policy
- `PATCH /k8s/policies/{namespace}/{name}/status` - Update policy status

### 4. CRD Schema Definitions

**MultiAgentSystem CRD** (`docs/k8s/multiagentsystem-crd.yaml`):
- OpenAPI v3 schema validation
- Support for tool checks (DETERMINISTIC_TOOL_SELECTED, DETERMINISTIC_LLM_SELECTED_TOOLS, AI_POWERED_TOOL_MATCH)
- App definitions with type validation (agent, client, mcp_server)
- Status subresource for operator updates
- kubectl printer columns for easy viewing

**ZTAPolicy CRD** (`docs/k8s/ztapolicy-crd.yaml`):
- Network policy specification
- Protocol restrictions (mcp, a2a, http)
- Allowed endpoint definitions
- External LLM endpoint configuration
- Status subresource tracking Cilium policy generation

### 5. Example Resources

**MultiAgentSystem Examples** (`docs/k8s/multiagentsystem-examples.yaml`):
- Production MAS with full tool checks
- Development MAS with minimal checks
- Simple minimal MAS

**ZTAPolicy Examples** (`docs/k8s/ztapolicy-examples.yaml`):
- Agent policy with MCP, A2A, and LLM access
- MCP server policy (receive-only)
- Client policy (MCP-only)
- Restricted agent policy (no LLM)

### 6. Documentation

**Complete API Documentation** (`docs/k8s/CRD_BACKEND_API.md`):
- Architecture overview with diagrams
- CRD field specifications
- REST API endpoint documentation
- Request/response examples
- Error handling
- Operator integration guide with Go code example
- Testing instructions

**Quick Start Guide** (`docs/k8s/README.md`):
- Installation instructions
- Quick start examples
- Architecture diagram
- Implementation status
- Testing procedures

### 7. Integration

**Dependency Injection** (`api/dependencies.py`):
- Added `K8sCRDService` to container
- Wired up dependencies (repositories, IdP client)

**Main App** (`api/app.py`):
- Registered k8s_crd routes
- Available at startup

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  MultiAgentSystem CRD                                 │  │
│  │  ZTAPolicy CRD                                        │  │
│  │  (Future: ZTA Operator reconciles these)             │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │ HTTP/REST                                 │
└──────────────────┼───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              ZTA Backend (identity-auth-server)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  NEW: /k8s/mas/* - MultiAgentSystem APIs             │  │
│  │  NEW: /k8s/policies/* - ZTAPolicy APIs               │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │                                           │
│  ┌───────────────▼───────────────────────────────────────┐  │
│  │  NEW: K8sCRDService                                   │  │
│  │  - CRD spec → internal model conversion              │  │
│  │  - Status management                                  │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │                                           │
│  ┌───────────────▼───────────────────────────────────────┐  │
│  │  EXISTING: MAS, App, AuthServer Services              │  │
│  │  - Database (PostgreSQL)                              │  │
│  │  - Keycloak integration                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Monolithic Backend**: Kept existing Python monolith, added new APIs (per requirement)
2. **CRD-to-Internal Mapping**: Service layer converts CRD specs to existing database models
3. **Status Subresources**: Separate status endpoints for operator status updates
4. **Namespace Support**: CRDs are namespaced, APIs accept namespace parameter
5. **Tool Check Mapping**: Convert CRD enum array to internal bitmask flags
6. **Keycloak Integration**: Reuse existing MAS service for realm/client creation

## Files Created

### Core Implementation
- `src/identity_auth_server/core/k8s_types.py` (276 lines)
- `src/identity_auth_server/services/k8s_crd_service.py` (385 lines)
- `src/identity_auth_server/api/routes/k8s_crd.py` (231 lines)

### CRD Definitions
- `docs/k8s/multiagentsystem-crd.yaml` (112 lines)
- `docs/k8s/ztapolicy-crd.yaml` (115 lines)

### Examples
- `docs/k8s/multiagentsystem-examples.yaml` (59 lines)
- `docs/k8s/ztapolicy-examples.yaml` (87 lines)

### Documentation
- `docs/k8s/CRD_BACKEND_API.md` (626 lines)
- `docs/k8s/README.md` (212 lines)

### Files Modified
- `src/identity_auth_server/api/app.py` (added k8s_crd routes)
- `src/identity_auth_server/api/dependencies.py` (added K8sCRDService)

**Total**: ~2,103 lines of new code and documentation

## Alignment with SPECS.md

This implementation directly addresses:

- **SPECS.md §7.2.1**: MultiAgentSystem CRD with exact schema as specified
- **SPECS.md §7.2.2**: ZTAPolicy CRD with exact schema as specified
- **SPECS.md §7.2.3**: Backend APIs for operator reconciliation (Go example provided in docs)

## Testing

### Manual Testing

```bash
# Start backend
cd identity-auth-server
make run

# Create MAS
curl -X POST http://localhost:3000/k8s/mas \
  -H "Content-Type: application/json" \
  -d @docs/k8s/multiagentsystem-examples.yaml

# Get MAS
curl http://localhost:3000/k8s/mas/production-mas/production-mas

# List all
curl http://localhost:3000/k8s/mas
```

### With Kubernetes

```bash
# Install CRDs
kubectl apply -f docs/k8s/multiagentsystem-crd.yaml
kubectl apply -f docs/k8s/ztapolicy-crd.yaml

# Create resources
kubectl apply -f docs/k8s/multiagentsystem-examples.yaml
kubectl apply -f docs/k8s/ztapolicy-examples.yaml

# View
kubectl get mas -A
kubectl describe mas production-mas -n production-mas
```

## What's NOT Included (Future Work)

Per the requirements ("implement only the CRDs for the MAS configuration"), the following are **out of scope** for this iteration:

❌ Kubernetes Operator implementation (controller-runtime in Go)
❌ Automatic CiliumNetworkPolicy generation
❌ Admission webhooks for validation
❌ Watch/streaming APIs
❌ Sidecar injection
❌ Microservices decomposition

These will be addressed in future iterations as the system evolves toward full Kubernetes-native deployment.

## How to Use

### For Backend Developers

1. Review data models in `core/k8s_types.py`
2. Understand service layer in `services/k8s_crd_service.py`
3. Check API routes in `api/routes/k8s_crd.py`
4. Test endpoints with curl or Python requests

### For Operator Developers

1. Read `docs/k8s/CRD_BACKEND_API.md` for API contract
2. Install CRD definitions from `docs/k8s/*-crd.yaml`
3. Call backend APIs during reconciliation
4. Update CRD status via PATCH endpoints

### For Platform Engineers

1. Apply CRD definitions to cluster
2. Deploy example resources
3. Verify with `kubectl get mas` and `kubectl describe mas`
4. Review documentation in `docs/k8s/README.md`

## Success Criteria

✅ **Backend APIs**: REST endpoints for CRD management implemented
✅ **CRD Schemas**: OpenAPI v3 schemas matching SPECS.md
✅ **Data Models**: Pydantic models for specs and status
✅ **Examples**: Multiple example resources for testing
✅ **Documentation**: Complete API docs with examples
✅ **Integration**: Wired into existing FastAPI app
✅ **No Microservices**: Kept monolithic architecture per requirements

## Next Steps (Future Iterations)

1. **Iteration 2**: Implement Kubernetes Operator using controller-runtime
2. **Iteration 3**: Add CiliumNetworkPolicy generation logic
3. **Iteration 4**: Implement admission webhooks for validation
4. **Iteration 5**: Add watch/streaming API support
5. **Iteration 6**: Integrate with sidecar injection mechanism

## References

- **SPECS.md §7.2**: Custom Resource Definitions specification
- **BUILD.md**: Existing system architecture
- **docs/k8s/CRD_BACKEND_API.md**: Complete API documentation
- **docs/k8s/README.md**: Quick start guide
