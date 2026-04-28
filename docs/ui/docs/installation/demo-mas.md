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

> **Note on images:** The default `values.yaml` references images in a private registry. Build and push your own:
>
> ```bash
> docker build -t your-registry/demo-agent-safe:latest         demo/src/agent-safe/
> docker build -t your-registry/demo-agent-compromised:latest  demo/src/agent-compromised/
> docker build -t your-registry/demo-mcp:latest                demo/src/mcp/
> docker build -t your-registry/chat-ui:latest                 demo/src/chat-ui/
> ```

## Configure Values

Edit `demo/helm/values.yaml`:

```yaml
namespace: casa-sidecar   # target namespace

agentSafe:
  replicas: 3
  serviceName: demo-agent-safe
  servicePort: 8082
  docker:
    registry: your-registry
    image: outshift-casa/demo-agent-safe
    suffix: ''
  tagversion: latest
  mcp_server_url: http://casa-demo-mcp:3000/mcp

agentCompromised:
  replicas: 3
  serviceName: demo-agent-compromised
  servicePort: 8082
  docker:
    registry: your-registry
    image: outshift-casa/demo-agent-compromised
    suffix: ''
  tagversion: latest
  mcp_server_url: http://casa-demo-mcp:3000/mcp

mcp:
  replicas: 1
  serviceName: casa-demo-mcp
  servicePort: 3000
  docker:
    registry: your-registry
    image: outshift-casa/k8s-demo-mcp
    suffix: ''
  tagversion: latest

chatUis:
  - name: safe
    docker:
      registry: your-registry
      image: outshift-casa/chat-ui
    tagversion: latest
    agentUrl: /safe-agent
    ingress:
      enabled: true
      className: "nginx"
      apiDomainName: "your.domain.com"
      domainPrefix: "casa-demo-safe"
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt

  - name: compromised
    docker:
      registry: your-registry
      image: outshift-casa/chat-ui
    tagversion: latest
    agentUrl: /compromised-agent
    ingress:
      enabled: true
      className: "nginx"
      apiDomainName: "your.domain.com"
      domainPrefix: "casa-demo-compromised"
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt

llmCredentials:
  apiBaseUrl: https://api.openai.com   # or your LiteLLM proxy
  apiKey: YOUR_OPENAI_KEY_HERE

masSafe:
  name: "casa Demo Safe"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
    - AI_POWERED_TOOL_MATCH
  llm_host: ""   # LLM hostname for eBPF restriction

masCompromised:
  name: "casa Demo Compromised"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
    - AI_POWERED_TOOL_MATCH
  llm_host: ""
```

## Enable Sidecar Injection

```bash
kubectl create namespace casa-sidecar
kubectl label namespace casa-sidecar istio-injection=enabled
```

## Install the Demo

```bash
helm install casa-mas demo/helm/ \
  --namespace casa-sidecar \
  -f demo/helm/values.yaml
```

Or using the Makefile:

```bash
make mas-helm-install
```

Wait for pods:

```bash
kubectl -n casa-sidecar wait --for=condition=ready pod --all --timeout=120s
```

Expected pods:

```
NAME                                READY   STATUS
demo-agent-safe-...                  1/1     Running
demo-agent-compromised-...           1/1     Running
casa-demo-mcp-...                    1/1     Running
chat-ui-safe-...                     1/1     Running
chat-ui-compromised-...              1/1     Running
```

## Open the Demo

Port-forward a chat UI and open it in your browser:

```bash
# Safe agent chat UI
kubectl -n casa-sidecar port-forward svc/chat-ui-safe 3001:80
# Open http://localhost:3001

# Compromised agent chat UI
kubectl -n casa-sidecar port-forward svc/chat-ui-compromised 3002:80
# Open http://localhost:3002
```

Type a message like *"Get the account summary and scheduled payments"* and send it. The chat UI forwards the conversation to the agent, which calls the LLM, requests tool tokens from CASA, and invokes the MCP server.

## View Enforcement Events

Open the Explorer UI to see the token events and tool decisions generated by your conversation:

```bash
kubectl -n casa-runtime port-forward svc/casa-ui-explorer 8080:80
# Open http://localhost:8080
```

## Next Steps

- [Demo Walkthrough](/demo/walkthrough) — step-by-step with expected output
- [Configuration — Demo MAS Values](/configuration/mas-values) — full values reference
