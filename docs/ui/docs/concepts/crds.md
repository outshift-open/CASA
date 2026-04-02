---
id: crds
sidebar_position: 2
title: CRDs
---

# Custom Resource Definitions

ZTA defines two CRDs in the `zta.io/v1alpha1` API group:

- `MultiAgentSystem` — declares the applications in a MAS and the tool checks to apply
- `ZTAPolicy` — declares per-workload network and protocol policies (reconciled into CiliumNetworkPolicy)

Both are installed as part of the `zta-control-plane` Helm chart.

## MultiAgentSystem

**Short name:** `mas`  
**API:** `multiagentsystems.zta.io`

### Purpose

Declares a Multi-Agent System: which applications belong to it, what types they are, and which tool authorization checks are active.

### Example

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

### Field Reference

| Field | Required | Description |
|---|---|---|
| `spec.name` | Yes | Human-readable name |
| `spec.authorizationServer` | Yes (transitional) | Keycloak realm name — scheduled for removal |
| `spec.enabledToolChecks` | No | List of tool check types to enable |
| `spec.apps` | No | List of applications in the MAS |
| `spec.apps[].name` | Yes | Unique name within the MAS |
| `spec.apps[].type` | Yes | One of: `agent`, `client`, `mcp_server` |
| `spec.apps[].baseUrl` | Yes | K8s service URL for this application |

**Allowed values for `enabledToolChecks`:**
- `DETERMINISTIC_TOOL_SELECTED` — verify the requested tool was in the token's allowed list
- `DETERMINISTIC_LLM_SELECTED_TOOLS` — verify the requested tool was selected by the LLM
- `AI_POWERED_TOOL_MATCH` — AI check that the tool matches the original user intent

### Status

| Field | Description |
|---|---|
| `status.phase` | `Pending`, `Active`, or `Failed` |
| `status.appsReady` | Number of apps successfully configured |
| `status.lastSyncTime` | Timestamp of last successful reconciliation |
| `status.message` | Human-readable status description |

---

## ZTAPolicy

**Short name:** `ztap`  
**API:** `ztapolicies.zta.io`

### Purpose

Declares per-workload network access rules. The ZTA operator reconciles these into `CiliumNetworkPolicy` resources.

### Example

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

### Field Reference

| Field | Required | Description |
|---|---|---|
| `spec.targetRef.kind` | Yes | `Deployment`, `StatefulSet`, or `Pod` |
| `spec.targetRef.name` | Yes | Name of the workload |
| `spec.allowedProtocols` | No | List of allowed protocols: `mcp`, `a2a`, `http` |
| `spec.allowedEndpoints` | No | List of K8s services this workload may reach |
| `spec.allowedEndpoints[].name` | Yes | Service name |
| `spec.allowedEndpoints[].namespace` | Yes | Service namespace |
| `spec.allowedEndpoints[].port` | Yes | Port number |
| `spec.llmEndpoint.fqdn` | No | Allowed external LLM FQDN |
| `spec.llmEndpoint.port` | No | LLM service port (typically 443) |

### Status

| Field | Description |
|---|---|
| `status.phase` | `Pending`, `Active`, or `Failed` |
| `status.ciliumPolicyName` | Name of the generated `CiliumNetworkPolicy` |
| `status.lastSyncTime` | Timestamp of last successful reconciliation |
| `status.message` | Human-readable status description |

---

## Checking CRD Status

```bash
# List all MAS resources
kubectl get mas --all-namespaces

# List all ZTA policies
kubectl get ztap --all-namespaces

# Describe a specific MAS
kubectl describe mas production-mas -n production-mas
```
