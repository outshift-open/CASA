---
id: mas-values
sidebar_position: 2
title: Demo MAS Values
---

# Demo MAS Helm Values

Reference for `demo/helm/values.yaml`.

The demo MAS chart deploys two agents (safe and compromised), a shared MCP server, and two chat-UI instances into a specified namespace.

## Full Values Reference

```yaml
namespace: casa-sidecar     # target namespace

agentSafe:
  replicas: 3
  serviceName: demo-agent-safe
  servicePort: 8082
  docker:
    registry: ""            # e.g. 626007623524.dkr.ecr.us-east-2.amazonaws.com
    image: outshift-casa/demo-agent-safe
    suffix: ''
  tagversion: latest
  mcp_server_url: http://casa-demo-mcp:3000/mcp

agentCompromised:
  replicas: 3
  serviceName: demo-agent-compromised
  servicePort: 8082
  docker:
    registry: ""
    image: outshift-casa/demo-agent-compromised
    suffix: ''
  tagversion: latest
  mcp_server_url: http://casa-demo-mcp:3000/mcp

mcp:
  replicas: 1
  serviceName: casa-demo-mcp
  servicePort: 3000
  docker:
    registry: ""
    image: outshift-casa/k8s-demo-mcp
    suffix: ''
  tagversion: latest

chatUis:
  - name: safe
    docker:
      registry: ""
      image: outshift-casa/chat-ui
    tagversion: latest
    agentUrl: /safe-agent
    ingress:
      enabled: false
      className: "nginx"
      apiDomainName: ""
      domainPrefix: "casa-demo-safe"
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt

  - name: compromised
    docker:
      registry: ""
      image: outshift-casa/chat-ui
    tagversion: latest
    agentUrl: /compromised-agent
    ingress:
      enabled: false
      className: "nginx"
      apiDomainName: ""
      domainPrefix: "casa-demo-compromised"
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt

llmCredentials:
  apiBaseUrl: ""            # e.g. https://api.openai.com
  apiKey: ""                # your LLM API key (stored as K8s Secret)

masSafe:
  name: "casa Demo Safe"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
    - AI_POWERED_TOOL_MATCH
  llm_host: ""              # LLM hostname for eBPF LLM endpoint restriction

masCompromised:
  name: "casa Demo Compromised"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
    - AI_POWERED_TOOL_MATCH
  llm_host: ""
```

## Field Reference

| Field | Description |
|---|---|
| `namespace` | Kubernetes namespace to deploy into. Must exist and have sidecar injection enabled. |
| `agentSafe.replicas` | Number of replicas for the safe agent deployment. |
| `agentSafe.serviceName` | K8s Service name for the safe agent. Used for in-cluster DNS. |
| `agentSafe.servicePort` | Port the safe agent listens on (A2A endpoint). |
| `agentSafe.docker.registry` | Container registry hostname. |
| `agentSafe.docker.image` | Image name within the registry (e.g. `outshift-casa/demo-agent-safe`). |
| `agentSafe.tagversion` | Image tag. |
| `agentSafe.mcp_server_url` | Full MCP server URL the agent calls, including path (e.g. `http://casa-demo-mcp:3000/mcp`). |
| `agentCompromised.*` | Same fields as `agentSafe.*`, for the compromised agent. |
| `mcp.serviceName` | K8s Service name for the MCP server (e.g. `casa-demo-mcp`). |
| `mcp.servicePort` | Port the MCP server listens on. |
| `mcp.docker.image` | MCP server image name (e.g. `outshift-casa/k8s-demo-mcp`). |
| `chatUis[].name` | Instance name (`safe` or `compromised`). Determines service name (`chat-ui-<name>`). |
| `chatUis[].agentUrl` | Path prefix the chat UI routes agent calls to (proxied by Nginx). |
| `chatUis[].ingress.enabled` | Set `true` to expose the chat UI via Ingress. |
| `chatUis[].ingress.domainPrefix` | Subdomain prefix for the Ingress (e.g. `casa-demo-safe`). |
| `chatUis[].ingress.annotations` | Ingress annotations (e.g. `cert-manager.io/cluster-issuer: letsencrypt`). |
| `llmCredentials.apiBaseUrl` | Base URL for the OpenAI-compatible LLM API. |
| `llmCredentials.apiKey` | API key for the LLM service. Stored as a Kubernetes Secret. |
| `masSafe.name` | Human-readable name for the safe MAS (written to `MultiAgentSystem` CRD). |
| `masSafe.enabledToolChecks` | Tool checks enabled for the safe MAS. |
| `masSafe.llm_host` | LLM FQDN used for eBPF LLM endpoint restriction (e.g. `litellm.prod.example.com`). |
| `masCompromised.*` | Same fields as `masSafe.*`, for the compromised MAS. |

## Building Your Own Images

```bash
docker build -t your-registry/demo-agent-safe:latest         demo/src/agent-safe/
docker build -t your-registry/demo-agent-compromised:latest  demo/src/agent-compromised/
docker build -t your-registry/demo-mcp:latest                demo/src/mcp/
docker build -t your-registry/chat-ui:latest                 demo/src/chat-ui/
```
