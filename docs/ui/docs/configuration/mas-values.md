---
id: mas-values
sidebar_position: 2
title: Demo MAS Values
---

# Demo MAS Helm Values

Reference for `demo/k8s/helm/values.yaml`.

The demo MAS chart deploys one agent and one MCP server into a specified namespace.

## Full Values Reference

```yaml
namespace: zta-sidecar        # Target namespace

agent:
  replicas: 1
  serviceName: zta-demo-agent
  servicePort: 8082
  docker:
    registry: 626007623524.dkr.ecr.us-east-2.amazonaws.com  # private ECR — replace with yours
    image: outshift-zta/k8s-demo-agent
    suffix: ''
  tagversion: 2026-03-16-a0d1194

  mcp_server_url: http://zta-demo-mcp:3000/mcp

  secret:
    openai_api_base: https://litellm.prod.outshift.ai  # replace with your LLM endpoint
    openai_api_key: SECRET_HERE                         # replace with your API key

mcp:
  replicas: 1
  serviceName: zta-demo-mcp
  servicePort: 3000
  docker:
    registry: 626007623524.dkr.ecr.us-east-2.amazonaws.com  # private ECR — replace with yours
    image: outshift-zta/k8s-demo-mcp
    suffix: ''
  tagversion: 2026-03-16-a0d1194
```

## Field Reference

| Field | Description |
|---|---|
| `namespace` | Kubernetes namespace to deploy into. Must exist and have sidecar injection enabled. |
| `agent.serviceName` | Kubernetes Service name for the agent. Used by in-cluster DNS. |
| `agent.servicePort` | Port the agent listens on. |
| `agent.docker.registry` | Container registry hostname. |
| `agent.docker.image` | Image name within the registry. |
| `agent.tagversion` | Image tag. |
| `agent.mcp_server_url` | URL of the MCP server that the agent will call. |
| `agent.secret.openai_api_base` | Base URL for the OpenAI-compatible LLM API. |
| `agent.secret.openai_api_key` | API key for the LLM service. Stored as a Kubernetes Secret. |
| `mcp.serviceName` | Kubernetes Service name for the MCP server. |
| `mcp.servicePort` | Port the MCP server listens on. |

## Building Your Own Images

If you cannot access the default registry, build and push your own images:

```bash
# Build demo agent
docker build -t your-registry/zta-demo-agent:latest demo/k8s/agent/
docker push your-registry/zta-demo-agent:latest

# Build demo MCP server
docker build -t your-registry/zta-demo-mcp:latest demo/k8s/mcp/
docker push your-registry/zta-demo-mcp:latest
```

Then update `values.yaml`:

```yaml
agent:
  docker:
    registry: your-registry
    image: zta-demo-agent
  tagversion: latest

mcp:
  docker:
    registry: your-registry
    image: zta-demo-mcp
  tagversion: latest
```
