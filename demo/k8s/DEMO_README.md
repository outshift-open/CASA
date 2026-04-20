# ZTA Demo - Safe vs Compromised Agents

This demo showcases Zero Trust Authorization (ZTA) for Multi-Agent Systems with two agents.

## Agents

### 1. demo-agent-safe
- **Clean agent** — responds normally to user requests
- Only calls tools explicitly requested by the user
- All tool calls pass ZTA authorization

### 2. demo-agent-compromised
- **Rogue agent** with malicious prompt injection
- Attempts unauthorized actions (balance transfers, adding beneficiaries, scheduling payments)
- **Blocked by ZTA authorization server**

## Directory Structure

```
demo/k8s/
├── helm/                        # Helm chart — single source of truth for deployment
│   ├── Chart.yaml
│   ├── values.yaml              # Image tags, service names, ingress config
│   └── templates/
│       ├── agent-safe/          # Safe agent deployment & service
│       ├── agent-compromised/   # Compromised agent deployment & service
│       ├── mcp/                 # MCP server deployment & service
│       ├── chat-ui/             # Chat UI deployment, service, ingress, nginx configmap
│       └── mas.yaml             # MultiAgentSystem CRD (applied by operator)
├── agent-safe/                  # Safe agent source code + Dockerfile
├── agent-compromised/           # Compromised agent source code + Dockerfile
├── mcp/                         # MCP server source code
└── DEMO_README.md
```

## Prerequisites

- Kubernetes cluster with Istio installed
- `kubectl` and `helm` configured
- ECR access (`regcred` image pull secret in target namespace)
- Secret `llm-credentials` in target namespace:
  - `api-base-url`: LLM gateway endpoint (e.g. `https://litellm.prod.outshift.ai`)
  - `api-key`: API key

## Deployment

### 1. Build & Push Docker Images

Images are built and pushed automatically by CI/CD on push to the branch.
Update the `tagversion` fields in `helm/values.yaml` with the new tags.

### 2. Deploy with Helm

```bash
# First install
helm install zta-demo demo/k8s/helm --namespace zta-control-plane-dev

# Upgrade after changes
helm upgrade zta-demo demo/k8s/helm --namespace zta-control-plane-dev
```

This deploys:
- Both agents (safe + compromised) with Istio sidecar
- MCP server
- Chat UI with nginx (proxies `/safe-agent/` and `/compromised-agent/` to respective agents)
- MultiAgentSystem CR → triggers operator to register apps + create Istio egress resources

## Verification

```bash
# Check pods
kubectl get pods -n zta-control-plane-dev | grep -E "demo-agent|zta-demo"

# Check MAS registration
kubectl get multiagentsystem zta-demo -n zta-control-plane-dev -o yaml

# Check Istio egress resources created by operator
kubectl get serviceentry,destinationrule -n zta-control-plane-dev

# Check Helm release
helm list -n zta-control-plane-dev
```

## Accessing the Chat UI

The chat UI is exposed at: `https://zta-demo.dev.outshift.ai`

It proxies to the **safe agent** by default (`AGENT_URL=/safe-agent` env var in the deployment).

To switch agent at runtime, update `chatUi.agentUrl` in `values.yaml` and run `helm upgrade`.

## Expected Behavior

### Safe Agent
- Processes user requests normally
- Only calls tools requested by the user
- All tool calls pass ZTA authorization

### Compromised Agent
- Attempts unauthorized tool calls (transfers, beneficiaries, payments)
- **ZTA blocks malicious tool calls**
- Legitimate user requests still work (if allowed by policy)

## Cleanup

```bash
helm uninstall zta-demo --namespace zta-control-plane-dev
```

## Architecture

```
Browser
   │
   ▼
https://zta-demo.dev.outshift.ai  (nginx ingress)
   │
   ▼
Chat UI (nginx)
   ├── /safe-agent/  ──────────► demo-agent-safe:8082
   └── /compromised-agent/  ───► demo-agent-compromised:8082
                                        │
                              Istio/Envoy sidecar
                                        │ ext_authz
                                        ▼
                               ZTA Auth Server
                                        │
                                        ▼
                                  MCP Server:3000
```
