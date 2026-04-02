---
id: install-demo-mas
sidebar_position: 3
title: Install Demo MAS
---

# Install the Demo MAS

The demo MAS deploys a minimal Multi-Agent System (one agent + one MCP server) that you can use to explore ZTA enforcement. It is intended for learning and testing, not production use.

## About the Demo

The demo consists of:

- **Demo Agent** — a Python agent that accepts chat requests, calls an LLM, and invokes tools via MCP
- **Demo MCP Server** — a Python MCP server exposing simple tools (account summary, scheduled payments)

The agent calls the LLM through the sidecar (token-gated), and the MCP server validates tokens before executing any tool.

## Prerequisites

The demo MAS chart requires:
- ZTA control plane installed (see [Install Control Plane](control-plane.md))
- Istio sidecar injection enabled for the target namespace (see [Istio deployment guide](/deployment-modes/istio))
- An OpenAI-compatible API endpoint and key

> **Note on images:** The default `values.yaml` references images in a private ECR registry. To run the demo, you must either:
> - Build the images from `demo/k8s/agent/` and `demo/k8s/mcp/` and push to your own registry, or
> - Update `demo/k8s/helm/values.yaml` with an accessible registry and image tags

## Configure Values

Edit `demo/k8s/helm/values.yaml`:

```yaml
namespace: zta-sidecar

agent:
  replicas: 1
  serviceName: zta-demo-agent
  servicePort: 8082
  docker:
    registry: YOUR_REGISTRY_HERE      # e.g. ghcr.io/your-org
    image: zta-demo-agent
    suffix: ''
  tagversion: latest

  mcp_server_url: http://zta-demo-mcp:3000/mcp

  secret:
    openai_api_base: https://api.openai.com   # or your LiteLLM proxy
    openai_api_key: YOUR_OPENAI_KEY_HERE

mcp:
  replicas: 1
  serviceName: zta-demo-mcp
  servicePort: 3000
  docker:
    registry: YOUR_REGISTRY_HERE
    image: zta-demo-mcp
    suffix: ''
  tagversion: latest
```

## Enable Sidecar Injection

```bash
kubectl create namespace zta-sidecar
kubectl label namespace zta-sidecar istio-injection=enabled
```

## Install the Demo

```bash
helm install zta-mas demo/k8s/helm/ \
  --namespace zta-sidecar \
  -f demo/k8s/helm/values.yaml
```

Or using the Makefile:

```bash
make mas-helm-install
```

Wait for pods:

```bash
kubectl -n zta-sidecar wait --for=condition=ready pod --all --timeout=120s
```

## Register the Demo MAS with ZTA

Apply the `MultiAgentSystem` CRD:

```bash
kubectl apply -f - <<EOF
apiVersion: zta.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: demo-mas
  namespace: zta-sidecar
spec:
  name: "ZTA Demo MAS"
  authorizationServer: "demo-realm"
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  - DETERMINISTIC_LLM_SELECTED_TOOLS
  apps:
  - name: demo-agent
    type: agent
    baseUrl: "http://zta-demo-agent.zta-sidecar.svc.cluster.local:8082"
  - name: demo-mcp
    type: mcp_server
    baseUrl: "http://zta-demo-mcp.zta-sidecar.svc.cluster.local:3000"
EOF
```

## Test the Demo

```bash
kubectl -n zta-sidecar port-forward svc/zta-demo-agent 8082:8082 &

curl -X POST http://localhost:8082/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "Get the account summary and scheduled payments"}'
```

Expected: a JSON response with the agent's reply, and ZTA enforcement events visible in the control plane UI.

## View Enforcement Events

```bash
kubectl -n zta-control-plane port-forward svc/zta-ui-explorer 8080:80 &
# Open http://localhost:8080 to see token events and tool decisions
```

## Next Steps

- [Demo Walkthrough](/demo/walkthrough) — step-by-step with expected output
- [Configuration — Control Plane Values](/configuration/control-plane-values) — tune ZTA settings
