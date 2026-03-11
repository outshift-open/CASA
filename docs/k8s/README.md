# Kubernetes CRD Support

This directory contains Kubernetes Custom Resource Definitions (CRDs) and documentation for the Zero Trust Architecture Multi-Agent System.

## Contents

### CRD Definitions
- **multiagentsystem-crd.yaml** - CRD definition for MultiAgentSystem resources
- **ztapolicy-crd.yaml** - CRD definition for ZTAPolicy resources

### Examples
- **multiagentsystem-examples.yaml** - Example MultiAgentSystem resources (production, dev, simple)
- **ztapolicy-examples.yaml** - Example ZTAPolicy resources (agent, MCP server, client policies)

### Documentation
- **CRD_BACKEND_API.md** - Complete API documentation for backend CRD support

## Quick Start

### Install CRDs

```bash
kubectl apply -f multiagentsystem-crd.yaml
kubectl apply -f ztapolicy-crd.yaml
```

### Deploy Example Resources

```bash
# Create a namespace
kubectl create namespace production-mas

# Deploy MultiAgentSystem
kubectl apply -f multiagentsystem-examples.yaml

# Deploy ZTAPolicy
kubectl apply -f ztapolicy-examples.yaml
```

### View Resources

```bash
# List MultiAgentSystems
kubectl get mas -A
kubectl get multiagentsystems -A

# View details
kubectl describe mas production-mas -n production-mas

# List ZTAPolicies
kubectl get ztap -A
kubectl get ztapolicies -A

# View details
kubectl describe ztapolicy agent-policy -n production-mas
```

## Backend API Integration

The backend REST APIs support these CRDs through the following endpoints:

### MultiAgentSystem APIs
- `POST /k8s/mas` - Create or update MAS
- `GET /k8s/mas/{namespace}/{name}` - Get MAS by name
- `GET /k8s/mas` - List all MAS resources
- `DELETE /k8s/mas/{namespace}/{name}` - Delete MAS
- `PATCH /k8s/mas/{namespace}/{name}/status` - Update MAS status

### ZTAPolicy APIs
- `POST /k8s/policies` - Create or update policy
- `GET /k8s/policies/{namespace}/{name}` - Get policy by name
- `GET /k8s/policies` - List all policies
- `DELETE /k8s/policies/{namespace}/{name}` - Delete policy
- `PATCH /k8s/policies/{namespace}/{name}/status` - Update policy status

See [CRD_BACKEND_API.md](./CRD_BACKEND_API.md) for complete API documentation.

## Architecture

```
┌──────────────────────────────────────────────┐
│         Kubernetes Cluster                   │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  MultiAgentSystem CRD                  │ │
│  │  - Manages MAS lifecycle               │ │
│  │  - Creates Keycloak realms             │ │
│  │  - Registers apps                      │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  ZTAPolicy CRD                         │ │
│  │  - Defines network policies            │ │
│  │  - Generates CiliumNetworkPolicy       │ │
│  │  - Controls protocol access            │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  ZTA Operator (Future)                 │ │
│  │  - Watches CRD changes                 │ │
│  │  - Calls backend APIs                  │ │
│  │  - Updates CRD status                  │ │
│  └────────────────────────────────────────┘ │
└──────────────┬───────────────────────────────┘
               │ HTTP/REST
               ▼
┌──────────────────────────────────────────────┐
│     ZTA Backend (identity-auth-server)       │
│  - /k8s/mas APIs                             │
│  - /k8s/policies APIs                        │
│  - Keycloak integration                      │
│  - Database persistence                      │
└──────────────────────────────────────────────┘
```

## Implementation Status

✅ **Completed (Iteration 1)**:
- CRD schemas (MultiAgentSystem, ZTAPolicy)
- Backend REST APIs for CRD management
- Data models for CRD specs and status
- Service layer for CRD-to-internal-model conversion
- Example resource manifests
- Complete API documentation

🔜 **Future Work**:
- Kubernetes Operator implementation (controller-runtime)
- Admission webhook for CRD validation
- Automatic CiliumNetworkPolicy generation
- Watch/streaming API support
- OpenAPI schema generation

## Design Principles

1. **Kubernetes-Native**: Use standard CRD patterns and kubectl workflows
2. **Declarative**: Users declare desired state, operator reconciles
3. **Zero Trust by Default**: All policies deny-by-default
4. **Observable**: Status fields show reconciliation state
5. **Composable**: CRDs work together (MAS + ZTAPolicy)

## Related Files

### Backend Implementation
- `src/identity_auth_server/core/k8s_types.py` - Pydantic models for CRD specs/status
- `src/identity_auth_server/services/k8s_crd_service.py` - Service layer for CRD management
- `src/identity_auth_server/api/routes/k8s_crd.py` - FastAPI routes for CRD endpoints

### Specifications
- `../../SPECS.md` - Full architecture specification
- `../../BUILD.md` - Existing system architecture

## Testing

### Manual API Testing

```bash
# Start the backend server
cd identity-auth-server
make run

# Test MAS creation
curl -X POST http://localhost:3000/k8s/mas \
  -H "Content-Type: application/json" \
  -d '{
    "apiVersion": "zta.io/v1alpha1",
    "kind": "MultiAgentSystem",
    "metadata": {"name": "test-mas", "namespace": "default"},
    "spec": {
      "name": "Test MAS",
      "authorizationServer": "test-realm",
      "apps": [
        {"name": "test-app", "type": "client", "baseUrl": "http://test:8000"}
      ]
    }
  }'

# Get MAS
curl http://localhost:3000/k8s/mas/default/test-mas

# List all MAS
curl http://localhost:3000/k8s/mas
```

### Integration Testing (with Kubernetes)

```bash
# Apply CRDs
kubectl apply -f multiagentsystem-crd.yaml
kubectl apply -f ztapolicy-crd.yaml

# Create test resources
kubectl apply -f multiagentsystem-examples.yaml

# Check status
kubectl get mas -A
kubectl describe mas production-mas -n production-mas
```

## Contributing

When extending CRD support:

1. Update CRD schemas in `*-crd.yaml` files
2. Update Pydantic models in `k8s_types.py`
3. Update service layer in `k8s_crd_service.py`
4. Update API routes in `k8s_crd.py`
5. Add examples to `*-examples.yaml`
6. Update documentation in `CRD_BACKEND_API.md`

## Support

For questions or issues:
- Review `CRD_BACKEND_API.md` for API details
- Check `../../SPECS.md` for architecture decisions
- See `../Developer_notes.md` for development setup
