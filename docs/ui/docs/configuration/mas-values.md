---
id: mas-values
sidebar_position: 2
title: Demo MAS Values
---

# Demo MAS Helm Values

Reference for `demo/helm/values.yaml`.

The demo MAS chart deploys a client UI, an agent, and an MCP server into a specified namespace.

## Full Values Reference

```yaml
namespace: casa-sidecar        # Target namespace

client:
  replicas: 1
  serviceName: casa-demo-client
  servicePort: 3001
  docker:
    registry: YOUR_REGISTRY_HERE      # e.g. ghcr.io/your-org
    image: casa-demo-client
    tagversion: latest
  agent_a2a_url: http://casa-demo-agent:8082   # agent A2A endpoint

agent:
  replicas: 1
  serviceName: casa-demo-agent
  servicePort: 8082
  docker:
    registry: YOUR_REGISTRY_HERE
    image: casa-demo-agent
    tagversion: latest
  mcp_server_url: http://casa-demo-mcp:3000/mcp
  secret:
    openai_api_base: https://api.openai.com   # replace with your LLM endpoint
    openai_api_key: YOUR_OPENAI_KEY_HERE      # replace with your API key

mcp:
  replicas: 1
  serviceName: casa-demo-mcp
  servicePort: 3000
  docker:
    registry: YOUR_REGISTRY_HERE
    image: casa-demo-mcp
    tagversion: latest
```

## Field Reference

| Field | Description |
|---|---|
| `namespace` | Kubernetes namespace to deploy into. Must exist and have sidecar injection enabled. |
| `client.serviceName` | Kubernetes Service name for the client UI. Used by in-cluster DNS. |
| `client.servicePort` | Port the client UI listens on. |
| `client.docker.registry` | Container registry hostname. |
| `client.docker.image` | Image name within the registry. |
| `client.tagversion` | Image tag. |
| `client.agent_a2a_url` | A2A endpoint of the agent. This is the only config the client UI needs. |
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
# Build demo client UI
docker build -t your-registry/casa-demo-client:latest demo/src/client/
docker push your-registry/casa-demo-client:latest

# Build demo agent
docker build -t your-registry/casa-demo-agent:latest demo/src/agent/
docker push your-registry/casa-demo-agent:latest

# Build demo MCP server
docker build -t your-registry/casa-demo-mcp:latest demo/src/mcp/
docker push your-registry/casa-demo-mcp:latest
```

Then update `values.yaml`:

```yaml
client:
  docker:
    registry: your-registry
    image: casa-demo-client
  tagversion: latest

agent:
  docker:
    registry: your-registry
    image: casa-demo-agent
  tagversion: latest

mcp:
  docker:
    registry: your-registry
    image: casa-demo-mcp
  tagversion: latest
```
