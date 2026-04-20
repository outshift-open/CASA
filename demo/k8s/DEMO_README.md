# ZTA Demo - Safe vs Compromised Agents

This demo showcases Zero Trust Authorization (ZTA) for Multi-Agent Systems with two agents:

## Agents

### 1. demo-agent-safe (V1)
- **Clean agent** with no malicious code
- Uses prompt: "you are a helpful assistant"
- Operates normally with ZTA enforcement via Istio/Envoy sidecar

### 2. demo-agent-compromised (V2)
- **Rogue agent** with malicious prompt injection
- Attempts to:
  - Transfer account balances without user consent
  - Add external beneficiaries
  - Schedule unauthorized payments
- Should be **blocked by ZTA authorization server**

## Directory Structure

```
demo/k8s/
├── agent-safe/              # Clean agent code
│   ├── agent.py            # Safe agent implementation
│   ├── main.py             # FastAPI server
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container image
├── agent-compromised/       # Rogue agent code
│   ├── agent.py            # Compromised agent with malicious code
│   ├── main.py             # FastAPI server
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container image
├── chat-ui/                 # Chat UI for testing
│   └── deployment.yaml, service.yaml, configmap.yaml, ingress.yaml
├── helm/                    # Helm chart deploying both agents, MCP, and MAS CRD
│   ├── Chart.yaml
│   ├── values.yaml         # Configure both agents
│   └── templates/
│       ├── agent-safe/     # Safe agent deployment & service
│       ├── agent-compromised/ # Compromised agent deployment & service
│       ├── mcp/            # MCP server
│       └── mas.yaml        # MultiAgentSystem CRD
└── DEMO_README.md          # This file
```

## Prerequisites

- Kubernetes cluster with Istio installed
- kubectl configured
- ECR access for pushing/pulling images
- Secret `llm-credentials` in target namespace with:
  - `api-base-url`: LLM gateway endpoint
  - `api-key`: API key
- Secret `regcred` for pulling images from ECR

## Deployment

### 1. Build Docker Images

```bash
# Build safe agent
cd demo/k8s/agent-safe
docker build -t 626007623524.dkr.ecr.us-east-2.amazonaws.com/outshift-zta/demo-agent-safe:latest .
docker push 626007623524.dkr.ecr.us-east-2.amazonaws.com/outshift-zta/demo-agent-safe:latest

# Build compromised agent
cd ../agent-compromised
docker build -t 626007623524.dkr.ecr.us-east-2.amazonaws.com/outshift-zta/demo-agent-compromised:latest .
docker push 626007623524.dkr.ecr.us-east-2.amazonaws.com/outshift-zta/demo-agent-compromised:latest
```

### 2. Deploy with Helm

The Helm chart deploys:
- Both agents (safe + compromised)
- MCP server
- MultiAgentSystem CRD

```bash
cd demo/k8s/helm
helm install zta-demo . --namespace zta-control-plane-dev --create-namespace
```

To upgrade after code changes:
```bash
helm upgrade zta-demo . --namespace zta-control-plane-dev
```

### 3. Deploy Chat UI (if not already deployed)

```bash
kubectl apply -f chat-ui/ --namespace zta-control-plane-dev
```

## Verification

### Check Deployments

```bash
# Check pods
kubectl get pods -n zta-control-plane-dev

# Check services
kubectl get svc -n zta-control-plane-dev

# Check MAS CRD
kubectl get multiagentsystem -n zta-control-plane-dev -o yaml

# Check Helm release
helm list -n zta-control-plane-dev
```

### Test the Agents

1. Port-forward the chat-ui:
   ```bash
   kubectl port-forward svc/chat-ui 8080:80 -n zta-control-plane-dev
   ```

2. Open http://localhost:8080 in your browser

3. Test the safe agent:
   - Chat UI proxies to `/safe-agent/` → `demo-agent-safe:8082`
   - Should respond normally

4. Test the compromised agent:
   - Chat UI proxies to `/compromised-agent/` → `demo-agent-compromised:8082`
   - Should attempt malicious actions
   - **ZTA should block unauthorized tool calls**

### Check ZTA Authorization

```bash
# View auth server logs
kubectl logs -l app=zta-auth-service -n zta-control-plane-dev

# View agent logs
kubectl logs -l app=demo-agent-safe -n zta-control-plane-dev
kubectl logs -l app=demo-agent-compromised -n zta-control-plane-dev
```

## Expected Behavior

### Safe Agent (V1)
- ✅ Processes user requests normally
- ✅ Only calls tools requested by user
- ✅ All tool calls pass ZTA authorization

### Compromised Agent (V2)
- ⚠️ Attempts unauthorized actions:
  - Transferring account balances
  - Adding external beneficiaries
  - Scheduling payments
- ❌ **ZTA blocks malicious tool calls**
- ✅ Legitimate user requests still work (if allowed by policy)

## Cleanup

```bash
# Uninstall Helm release (removes agents, MCP, MAS CRD)
helm uninstall zta-demo --namespace zta-control-plane-dev

# Remove chat-ui (if deployed separately)
kubectl delete -f chat-ui/ --namespace zta-control-plane-dev
```

## Architecture

```
┌─────────────┐
│  Chat UI    │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
  /safe-agent/  /compromised-agent/
       │             │
       ▼             ▼
┌──────────┐  ┌──────────────┐
│  Safe    │  │ Compromised  │
│  Agent   │  │   Agent      │
│  (V1)    │  │   (V2)       │
└────┬─────┘  └──────┬───────┘
     │               │
     │   ┌───────────┘
     │   │
     ▼   ▼
  ┌─────────────┐       ┌──────────────┐
  │ Istio/Envoy │◄──────┤ ZTA Auth     │
  │  Sidecar    │       │ Server       │
  └──────┬──────┘       └──────────────┘
         │
         ▼
    ┌─────────┐
    │   MCP   │
    │ Server  │
    └─────────┘
```

## Notes

- Both agents run with Istio sidecar injection enabled
- ZTA enforcement happens at the Envoy sidecar via ext_authz
- The auth server validates all tool calls based on policies
- Chat UI nginx config already proxies to both agents
