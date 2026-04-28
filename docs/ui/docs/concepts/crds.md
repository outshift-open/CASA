---
id: crds
sidebar_position: 2
title: CRDs
---

# Custom Resource Definitions

CASA defines two CRDs in the `casa.io/v1alpha1` API group:

- `MultiAgentSystem` — declares the applications in a MAS and the tool checks to apply _(fully supported)_
- `CASAPolicy` — declares per-workload protocol and LLM endpoint policies, reconciled into network enforcement _(in development)_

Both are installed as part of the `casa-runtime` Helm chart.

## MultiAgentSystem

**Short name:** `mas`  
**API:** `multiagentsystems.casa.io`  
**Status: Fully supported**

### Purpose

Declares a Multi-Agent System: which applications belong to it, what types they are, and which tool authorization checks are active.

### Example

```yaml
apiVersion: casa.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: production-mas
  namespace: production-mas
spec:
  name: "Production Multi-Agent System"
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  - DETERMINISTIC_LLM_SELECTED_TOOLS
  - AI_POWERED_TOOL_MATCH
  llm_host: your-llm-host.example.com
  apps:
  - name: user-app
    type: client
    kubernetesWorkloadName: user-app
    baseUrl:
      host: user-app:8000
      scheme: http
  - name: orchestrator-agent
    type: agent
    kubernetesWorkloadName: orchestrator-agent
    baseUrl:
      host: orchestrator-agent:8000
      scheme: http
    httpRequestSchema:
      promptFieldJsonPath: '{.prompt}'
  - name: filesystem-mcp
    type: mcp_server
    kubernetesWorkloadName: filesystem-mcp
    baseUrl:
      host: filesystem-mcp:8080
      scheme: http
```

### Field Reference

| Field                                      | Required | Description                                                     |
| ------------------------------------------ | -------- | --------------------------------------------------------------- |
| `spec.name`                                | Yes      | Human-readable name                                             |
| `spec.enabledToolChecks`                   | No       | List of tool check types to enable                              |
| `spec.llm_host`                            | No       | LLM hostname used for eBPF LLM endpoint restriction             |
| `spec.apps`                                | No       | List of applications in the MAS                                 |
| `spec.apps[].name`                         | Yes      | Unique name within the MAS                                      |
| `spec.apps[].type`                         | Yes      | One of: `agent`, `client`, `mcp_server`                         |
| `spec.apps[].kubernetesWorkloadName`       | Yes      | Name of the Kubernetes workload (Deployment) for this app       |
| `spec.apps[].baseUrl.host`                 | Yes      | `service-name:port` for this application                        |
| `spec.apps[].baseUrl.scheme`               | Yes      | `http` or `https`                                               |
| `spec.apps[].httpRequestSchema.promptFieldJsonPath` | No | JSONPath to the prompt field in the agent's request body (agents only) |

**Allowed values for `enabledToolChecks`:**

- `DETERMINISTIC_TOOL_SELECTED` — verify the requested tool was in the token's allowed list
- `DETERMINISTIC_LLM_SELECTED_TOOLS` — verify the requested tool was selected by the LLM
- `AI_POWERED_TOOL_MATCH` — AI check that the tool matches the original user intent

### Status

| Field                 | Description                                 |
| --------------------- | ------------------------------------------- |
| `status.phase`        | `Pending`, `Active`, or `Failed`            |
| `status.appsReady`    | Number of apps successfully configured      |
| `status.lastSyncTime` | Timestamp of last successful reconciliation |
| `status.message`      | Human-readable status description           |

---

## CASAPolicy

**Short name:** `casap`  
**API:** `casapolicies.casa.io`  
**Status: In Development**

:::caution In Development
`CASAPolicy` is currently in development and not yet available. It will control per-workload **allowed protocols** (`mcp`, `a2a`) and **LLM endpoints** (FQDN allow-list), and will reconcile automatically into network enforcement policies.
:::

### Purpose

Declares per-workload network access rules — specifically which protocols a workload may use and which external LLM endpoints it may reach. The CASA operator reconciles these into network enforcement policies.

### Example

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
          namespace: casa-runtime
          port: 8443
    llmEndpoint:
        fqdn: api.openai.com
        port: 443
```

### Field Reference

| Field                               | Required | Description                                     |
| ----------------------------------- | -------- | ----------------------------------------------- |
| `spec.targetRef.kind`               | Yes      | `Deployment`, `StatefulSet`, or `Pod`           |
| `spec.targetRef.name`               | Yes      | Name of the workload                            |
| `spec.allowedProtocols`             | No       | List of allowed protocols: `mcp`, `a2a`, `http` |
| `spec.allowedEndpoints`             | No       | List of K8s services this workload may reach    |
| `spec.allowedEndpoints[].name`      | Yes      | Service name                                    |
| `spec.allowedEndpoints[].namespace` | Yes      | Service namespace                               |
| `spec.allowedEndpoints[].port`      | Yes      | Port number                                     |
| `spec.llmEndpoint.fqdn`             | No       | Allowed external LLM FQDN                       |
| `spec.llmEndpoint.port`             | No       | LLM service port (typically 443)                |

### Status

| Field                 | Description                                 |
| --------------------- | ------------------------------------------- |
| `status.phase`        | `Pending`, `Active`, or `Failed`            |
| `status.lastSyncTime` | Timestamp of last successful reconciliation |
| `status.message`      | Human-readable status description           |

---

## Checking CRD Status

```bash
# List all MAS resources
kubectl get mas --all-namespaces

# List all CASA policies
kubectl get casap --all-namespaces

# Describe a specific MAS
kubectl describe mas production-mas -n production-mas
```
