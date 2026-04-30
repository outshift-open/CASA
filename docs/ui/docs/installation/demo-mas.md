---
id: install-demo-mas
sidebar_position: 3
title: Install Demo MAS
---

# Install the Demo MAS

The demo MAS deploys a complete Multi-Agent System you can use to explore CASA enforcement. It models a "safe" agent vs. a "compromised" agent interacting with the same MCP server, enforced by CASA.

## About the Demo

| Component | Source | Description |
|---|---|---|
| **Agent Safe** | `demo/src/agent-safe/` | A well-behaved Python agent that calls the LLM and invokes tools via MCP |
| **Agent Compromised** | `demo/src/agent-compromised/` | A Python agent that simulates prompt-injection behaviour |
| **Demo MCP Server** | `demo/src/mcp/` | A Python MCP server exposing simple tools (account summary, scheduled payments) |
| **Chat UI** | `demo/src/chat-ui/` | A shared React chat interface; two instances are deployed — one per agent |

Both agents share the same MCP server. CASA enforces separate policies for each agent via two `MultiAgentSystem` CRDs (`masSafe` and `masCompromised`).

## Prerequisites

- CASA runtime installed (see [Install Runtime](runtime.md))
- Istio sidecar injection enabled for the target namespace (see [Istio deployment guide](/deployment-modes/istio))
- An OpenAI-compatible API endpoint and key

## Images

All demo images are published publicly to GHCR alongside the runtime images:

| Image | GHCR path |
|---|---|
| Agent Safe | `ghcr.io/outshift-open/outshift-casa/demo/agent-safe` |
| Agent Compromised | `ghcr.io/outshift-open/outshift-casa/demo/agent-compromised` |
| MCP Server | `ghcr.io/outshift-open/outshift-casa/demo/mcp` |
| Chat UI | `ghcr.io/outshift-open/outshift-casa/demo/chat-ui` |

No authentication is required to pull these images.

## Configure Values

Create a `values-demo.yaml` (or pass `--set` flags):

```yaml
agentSafe:
  docker:
    registry: ghcr.io/outshift-open
    image: outshift-casa/demo/agent-safe
  tagversion: latest
  mcp_server_url: http://casa-demo-mcp:3000/mcp

agentCompromised:
  docker:
    registry: ghcr.io/outshift-open
    image: outshift-casa/demo/agent-compromised
  tagversion: latest
  mcp_server_url: http://casa-demo-mcp:3000/mcp

mcp:
  docker:
    registry: ghcr.io/outshift-open
    image: outshift-casa/demo/mcp
  tagversion: latest

chatUis:
  - name: safe
    docker:
      registry: ghcr.io/outshift-open
      image: outshift-casa/demo/chat-ui
    tagversion: latest
    agentUrl: /safe-agent
    ingress:
      enabled: true
      className: "nginx"             # adjust to your cluster's ingress class
      apiDomainName: "your.domain.com"
      domainPrefix: "casa-chat-safe"
      annotations: {}               # e.g. cert-manager.io/cluster-issuer: letsencrypt

  - name: compromised
    docker:
      registry: ghcr.io/outshift-open
      image: outshift-casa/demo/chat-ui
    tagversion: latest
    agentUrl: /compromised-agent
    ingress:
      enabled: true
      className: "nginx"
      apiDomainName: "your.domain.com"
      domainPrefix: "casa-chat-compromised"
      annotations: {}

llmCredentials:
  apiBaseUrl: https://api.openai.com   # or your LiteLLM proxy
  apiKey: YOUR_LLM_KEY

masSafe:
  name: "CASA Demo Safe"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
    - AI_POWERED_TOOL_MATCH
  llm_host: ""   # LLM hostname for eBPF restriction (leave empty to skip)

masCompromised:
  name: "CASA Demo Compromised"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
    - AI_POWERED_TOOL_MATCH
  llm_host: ""
```

## Install the Demo

Install into the same namespace as the runtime (`casa-dev`):

```bash
helm install casa-demo oci://ghcr.io/outshift-open/helm/casa-mas-demo \
  --version 1.2 \
  --namespace casa-dev \
  -f values-demo.yaml
```

No `helm repo add` needed — OCI charts are pulled directly.

Wait for pods:

```bash
kubectl -n casa-dev wait --for=condition=ready pod \
  -l app.kubernetes.io/instance=casa-demo \
  --timeout=120s
```

Expected pods:

```
NAME                                      READY   STATUS
demo-agent-safe-...                       2/2     Running
demo-agent-compromised-...                2/2     Running
casa-demo-mcp-...                         2/2     Running
casa-demo-chat-ui-safe-...                1/1     Running
casa-demo-chat-ui-compromised-...         1/1     Running
```

> Agent and MCP pods show `2/2` because Istio injects a sidecar proxy container alongside the app container.

## Open the Demo

Port-forward the chat UIs:

```bash
kubectl -n casa-dev port-forward svc/casa-demo-chat-ui-safe 3001:80 &
# Open http://localhost:3001

kubectl -n casa-dev port-forward svc/casa-demo-chat-ui-compromised 3002:80 &
# Open http://localhost:3002
```

Type a message like *"Get the account summary and scheduled payments"* and send it. The chat UI forwards the conversation to the agent, which calls the LLM, requests tool tokens from CASA, and invokes the MCP server.

## View Enforcement Events

Open the Explorer UI to see token events and tool decisions:

```bash
kubectl -n casa-dev port-forward svc/casa-dev-ui-explorer 8080:80 &
# Open http://localhost:8080
```

## Next Steps

- [Demo Walkthrough](/demo/walkthrough) — step-by-step with expected output
- [Configuration — Demo MAS Values](/configuration/mas-values) — full values reference
