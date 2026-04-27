---
id: crds-reference
sidebar_position: 3
title: CRDs Reference
---

# CRDs Field Reference

Full field reference for the `casa.io/v1alpha1` CRDs. For conceptual explanations, see [Concepts — CRDs](/concepts/crds).

## MultiAgentSystem

**API group:** `casa.io`  
**Version:** `v1alpha1`  
**Kind:** `MultiAgentSystem`  
**Short name:** `mas`  
**Scope:** Namespaced

### Spec

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Human-readable display name for the MAS |
| `authorizationServer` | string | Yes | Keycloak realm name. **Transitional — scheduled for removal.** |
| `enabledToolChecks` | string[] | No | Tool check types to enable. See below. |
| `apps` | object[] | No | Applications registered in this MAS |
| `apps[].name` | string | Yes | Unique application name within the MAS |
| `apps[].type` | string | Yes | `agent`, `client`, or `mcp_server` |
| `apps[].baseUrl` | string | Yes | K8s service URL (`http://svc.ns.svc.cluster.local:port`) |

**Allowed values for `enabledToolChecks`:**

| Value | Description |
|---|---|
| `DETERMINISTIC_TOOL_SELECTED` | Requested tool must be in token's allowed tools list |
| `DETERMINISTIC_LLM_SELECTED_TOOLS` | Requested tool must have been selected by the LLM |
| `AI_POWERED_TOOL_MATCH` | Semantic matching of tool to original user intent |

### Status

| Field | Type | Description |
|---|---|---|
| `phase` | string | `Pending`, `Active`, or `Failed` |
| `appsReady` | integer | Number of apps successfully configured |
| `lastSyncTime` | string (datetime) | Timestamp of last successful reconciliation |
| `message` | string | Human-readable status description |

### Complete Example

```yaml
apiVersion: casa.io/v1alpha1
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
  - name: database-mcp
    type: mcp_server
    baseUrl: "http://database-mcp.production-mas.svc.cluster.local:8080"
```

---

## CASAPolicy

**API group:** `casa.io`  
**Version:** `v1alpha1`  
**Kind:** `CASAPolicy`  
**Short name:** `casap`  
**Scope:** Namespaced

:::caution In Development
`CASAPolicy` is currently in development. Field names and semantics may change before the stable release. It controls per-workload **allowed protocols** and **LLM endpoint** allow-lists.
:::


### Spec

| Field | Type | Required | Description |
|---|---|---|---|
| `targetRef.kind` | string | Yes | `Deployment`, `StatefulSet`, or `Pod` |
| `targetRef.name` | string | Yes | Name of the target workload |
| `allowedProtocols` | string[] | No | Protocols allowed for this workload: `mcp`, `a2a`, `http` |
| `allowedEndpoints` | object[] | No | K8s services this workload may communicate with |
| `allowedEndpoints[].name` | string | Yes | Target service name |
| `allowedEndpoints[].namespace` | string | Yes | Target service namespace |
| `allowedEndpoints[].port` | integer | Yes | Target port number |
| `llmEndpoint.fqdn` | string | No | FQDN of the allowed external LLM service |
| `llmEndpoint.port` | integer | No | Port for the LLM service (typically 443) |

### Status

| Field | Type | Description |
|---|---|---|
| `phase` | string | `Pending`, `Active`, or `Failed` |
| `lastSyncTime` | string (datetime) | Timestamp of last successful reconciliation |
| `message` | string | Human-readable status description |

### Complete Examples

**Agent with MCP and A2A access:**

```yaml
apiVersion: casa.io/v1alpha1
kind: CASAPolicy
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
  - name: casa-auth-service
    namespace: casa-control-plane
    port: 8443
  llmEndpoint:
    fqdn: api.openai.com
    port: 443
```

**MCP server (inbound only):**

```yaml
apiVersion: casa.io/v1alpha1
kind: CASAPolicy
metadata:
  name: mcp-server-policy
  namespace: production-mas
spec:
  targetRef:
    kind: Deployment
    name: filesystem-mcp
  allowedProtocols:
  - mcp
  allowedEndpoints:
  - name: casa-auth-service
    namespace: casa-control-plane
    port: 8443
```

**Restricted agent (no LLM access):**

```yaml
apiVersion: casa.io/v1alpha1
kind: CASAPolicy
metadata:
  name: restricted-agent-policy
  namespace: production-mas
spec:
  targetRef:
    kind: StatefulSet
    name: worker-agent
  allowedProtocols:
  - mcp
  allowedEndpoints:
  - name: filesystem-mcp
    namespace: production-mas
    port: 8080
  - name: casa-auth-service
    namespace: casa-control-plane
    port: 8443
  # No llmEndpoint — this agent cannot call external LLMs
```
