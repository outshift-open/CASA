# CASA Demo

This demo illustrates CASA's intent-scoped authorization by running two agents side-by-side in a Kubernetes cluster:

- **Safe agent** — operates within its declared intent; all tool calls are authorized.
- **Compromised agent** — attempts calls outside its declared intent; CASA blocks them at the network layer.

Both agents connect to a shared MCP server (a fictitious banking app) and are exposed through a chat UI.

---

## Components

| Component | Source | Description |
|---|---|---|
| `agent-safe` | `demo/src/agent-safe/` | FastAPI agent, uses only authorized MCP tools |
| `agent-compromised` | `demo/src/agent-compromised/` | FastAPI agent, attempts unauthorized tool calls |
| `mcp` | `demo/src/mcp/` | FastMCP banking MCP server |
| `chat-ui` | `demo/src/chat-ui/` | React chat interface, one instance per agent |
| Helm chart | `demo/helm/` | Deploys all of the above plus `MultiAgentSystem` CRDs |

---

## Prerequisites

- Kubernetes cluster with CASA control plane installed (see [control plane setup](../docs/ui/docs/installation/control-plane.md))
- Helm 3.x
- An OpenAI-compatible LLM endpoint and API key
- Container images built and pushed (or local registry configured)

---

## Build Container Images

```bash
# From repo root
docker build -t demo-agent-safe    demo/src/agent-safe/
docker build -t demo-agent-compromised demo/src/agent-compromised/
docker build -t demo-mcp           demo/src/mcp/
docker build -t chat-ui            demo/src/chat-ui/
```

---

## Deploy

### 1. Configure values

Copy `demo/helm/values.yaml` and set:

```yaml
llmCredentials:
  apiBaseUrl: "https://<your-llm-endpoint>"
  apiKey: "<your-api-key>"
```

Set the `docker.registry` and `tagversion` fields if pulling images from a registry.

### 2. Install with Helm

```bash
helm install casa-demo demo/helm/ \
  --namespace casa-demo \
  --create-namespace \
  -f demo/helm/values.yaml
```

### 3. Upgrade

```bash
helm upgrade casa-demo demo/helm/ \
  --namespace casa-demo \
  -f demo/helm/values.yaml
```

### 4. Uninstall

```bash
helm uninstall casa-demo --namespace casa-demo
```

---

## Access the Chat UI

By default the ingress is disabled. Enable it in `values.yaml`:

```yaml
chatUis:
  - name: safe
    ingress:
      enabled: true
      className: "nginx"
      apiDomainName: "<your-cluster-domain>"
      domainPrefix: "casa-demo-safe"
  - name: compromised
    ingress:
      enabled: true
      className: "nginx"
      apiDomainName: "<your-cluster-domain>"
      domainPrefix: "casa-demo-compromised"
```

Or use port-forwarding for local access:

```bash
kubectl port-forward svc/demo-agent-safe 8082:8082 -n casa-demo
```

---

## Try It

Open the safe chat UI and ask:

- `"What is my account balance?"` — authorized, succeeds.
- `"Transfer $500 to account 999."` — if the compromised agent attempts this without it being in its declared intent, CASA blocks it.

The CASA Explorer UI shows the authorization trace for each request.
