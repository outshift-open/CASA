# MAS Deployment Guide - From Scratch

This guide walks through deploying a Multi-Agent System (MAS) from scratch, assuming you have already deployed the CASA control plane (auth-service, operator, Keycloak, etc.).

## Prerequisites

### Already Deployed (via CI/CD)
- ✅ CASA Control Plane in `casa-control-plane-dev` namespace:
  - Auth-service
  - Operator
  - Keycloak
  - PostgreSQL
  - Ext-authz middleware (protects control plane namespace only)

### What You Need to Deploy
- [ ] Enable Istio sidecar injection for your MAS namespace
- [ ] Deploy ext-authz middleware in your MAS namespace (see [sidecar.md](../dev/sidecar.md) for setup)
- [ ] Your agent application(s)
- [ ] Your MCP server(s) (optional)
- [ ] MultiAgentSystem CRD

## Step 1: Prepare Your Applications

### Option A: Agent with LLM Access

Your agent needs:

1. **LLM API Key** (OpenAI, Anthropic, etc.)
2. **Base URL** where agent listens (must be accessible from auth-service)
3. **Docker image** for the agent

**Example Agent Deployment:**

```yaml
# agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-agent
  namespace: my-namespace
  labels:
    app: my-agent
    version: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-agent
  template:
    metadata:
      labels:
        app: my-agent
        version: v1
    spec:
      containers:
      - name: agent
        image: your-registry/my-agent:latest
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: OPENAI_API_KEY          # or ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-credentials
              key: api-key
        - name: LLM_MODEL
          value: "gpt-4"                 # or "claude-3-opus-20240229"
        - name: AGENT_PORT
          value: "8080"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: my-agent
  namespace: my-namespace
spec:
  selector:
    app: my-agent
  ports:
  - port: 8080
    targetPort: 8080
    name: http
```

**Create LLM credentials secret:**

```bash
kubectl create secret generic llm-credentials \
  --from-literal=api-key='sk-...' \
  -n my-namespace
```

### Option B: MCP Server

MCP servers expose tools/resources to agents. They don't need LLM keys.

**Example MCP Server Deployment:**

```yaml
# mcp-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-mcp-server
  namespace: my-namespace
  labels:
    app: my-mcp-server
    version: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-mcp-server
  template:
    metadata:
      labels:
        app: my-mcp-server
        version: v1
    spec:
      containers:
      - name: mcp-server
        image: your-registry/my-mcp-server:latest
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: MCP_PORT
          value: "3000"
        - name: DATABASE_URL         # If MCP needs database access
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: my-mcp-server
  namespace: my-namespace
spec:
  selector:
    app: my-mcp-server
  ports:
  - port: 3000
    targetPort: 3000
    name: http
```

## Step 2: Deploy Your Applications

**Prerequisites for this step:**
- ✅ Namespace created with Istio injection enabled
- ✅ Ext-authz middleware deployed in your namespace (see [sidecar.md](../dev/sidecar.md))

```bash
# Create secrets (LLM keys, database credentials, etc.)
kubectl create secret generic llm-credentials \
  --from-literal=api-key='YOUR_API_KEY' \
  -n my-namespace

# Deploy agent
kubectl apply -f agent-deployment.yaml

# Deploy MCP server (optional)
kubectl apply -f mcp-server-deployment.yaml

# Verify deployments
kubectl get pods -n my-namespace
# NAME                            READY   STATUS    RESTARTS   AGE
# my-agent-xxxxx                  2/2     Running   0          30s
# my-mcp-server-xxxxx             2/2     Running   0          30s
```

**Important:** Each pod should have 2/2 containers (your app + Istio sidecar).

## Step 3: Create MultiAgentSystem CRD

Now that your apps are running, create the MAS CRD to register them.

```yaml
# mas.yaml
apiVersion: casa.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: my-mas                    # K8s resource name (lowercase, dashes only)
  namespace: my-namespace
spec:
  name: "My MAS"                  # Human-friendly display name
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
  llm_host: your-llm-host.example.com
  apps:
    - name: my-agent
      type: agent
      kubernetesWorkloadName: my-agent
      baseUrl:
        host: my-agent:8080
        scheme: http
      httpRequestSchema:
        promptFieldJsonPath: '{.prompt}'
    - name: my-mcp-server
      type: mcp_server
      kubernetesWorkloadName: my-mcp-server
      baseUrl:
        host: my-mcp-server:3000
        scheme: http
```

**Field Explanations:**

- `metadata.name`: K8s resource identifier (DNS-compliant: lowercase + dashes)
- `spec.name`: Display name shown in UI (can have spaces, capitals)
- `spec.apps[].baseUrl`: Must be `http://service-name:port` format
  - Use the K8s Service name, not pod name
  - Must be accessible from auth-service pod

**Apply the CRD:**

```bash
kubectl apply -f mas.yaml
```

## Step 4: Verify MAS Registration

**Check MAS status:**

```bash
kubectl get mas -n my-namespace
# NAME     PHASE    APPS READY   REALM       AGE
# my-mas   Active   2            my-realm    30s
```

**Expected status:**
- `PHASE`: `Active` (if successful) or `Failed` (if errors)
- `APPS READY`: Should match number of apps in spec
- `REALM`: The Keycloak realm name

**Check detailed status:**

```bash
kubectl get mas my-mas -n my-namespace -o yaml | grep -A10 "status:"
# status:
#   appsReady: 2
#   lastSyncTime: "2026-04-01T10:00:00Z"
#   message: "Registered 2 apps"
#   phase: Active
```

**If status shows Failed:**

```bash
# Check operator logs
kubectl logs -n casa-control-plane-dev deployment/casa-operator -c operator

# Check auth-service logs
kubectl logs -n casa-control-plane-dev deployment/casa-auth-service -c auth-service
```

## Step 5: Verify Keycloak Registration

Your MAS should now have a realm in Keycloak with registered clients.

**Access Keycloak admin console:**

```bash
# Port-forward to Keycloak
kubectl port-forward -n casa-control-plane-dev svc/keycloak 8080:8080

# Open browser: http://localhost:8080/admin
# Login with admin credentials
```

**Verify:**
1. Realm `my-realm` exists
2. Each app has a client registered:
   - Client ID: `<app-name>-<mas-id>-client`
   - Protocol: `openid-connect`
   - Service accounts enabled

## Step 6: Test the Full Flow

### Test 1: Agent Can Get Token

Your agent should be able to authenticate:

```bash
# Get auth-service URL
AUTH_SERVICE_URL="http://localhost:8000"  # or in-cluster URL

# Agent requests token
curl -X POST "$AUTH_SERVICE_URL/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "my-agent-<mas-id>-client",
    "client_secret": "<secret-from-keycloak>",
    "grant_type": "client_credentials"
  }'

# Should return JWT token
```

### Test 2: Make Authenticated Request

```bash
# Get token
TOKEN=$(curl -s -X POST "$AUTH_SERVICE_URL/auth/token" ... | jq -r '.access_token')

# Make request to another app
curl -H "Authorization: Bearer $TOKEN" \
     http://my-mcp-server:3000/tools
```

### Test 3: Verify Ext-Authz Middleware

The ext-authz middleware should intercept and validate requests:

```bash
# Without token (should fail)
curl http://my-agent:8080/health
# Expected: 401 Unauthorized or 403 Forbidden

# With valid token (should succeed)
curl -H "Authorization: Bearer $TOKEN" \
     http://my-agent:8080/health
# Expected: 200 OK
```

## Common Configuration Patterns

### Pattern 1: Simple Single-Agent MAS

```yaml
apiVersion: casa.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: simple-agent
  namespace: my-namespace
spec:
  name: "Simple Agent"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
  apps:
    - name: agent
      type: agent
      kubernetesWorkloadName: agent
      baseUrl:
        host: agent:8080
        scheme: http
      httpRequestSchema:
        promptFieldJsonPath: '{.prompt}'
```

**Required:**
- Agent deployment with LLM credentials
- Agent service on port 8080

### Pattern 2: Agent + Multiple MCP Servers

```yaml
apiVersion: casa.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: agent-with-tools
  namespace: my-namespace
spec:
  name: "Agent with Tools"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
    - AI_POWERED_TOOL_MATCH
  apps:
    - name: main-agent
      type: agent
      kubernetesWorkloadName: main-agent
      baseUrl:
        host: main-agent:8080
        scheme: http
      httpRequestSchema:
        promptFieldJsonPath: '{.prompt}'
    - name: database-mcp
      type: mcp_server
      kubernetesWorkloadName: database-mcp
      baseUrl:
        host: database-mcp:3000
        scheme: http
    - name: api-mcp
      type: mcp_server
      kubernetesWorkloadName: api-mcp
      baseUrl:
        host: api-mcp:3000
        scheme: http
    - name: filesystem-mcp
      type: mcp_server
      kubernetesWorkloadName: filesystem-mcp
      baseUrl:
        host: filesystem-mcp:3000
        scheme: http
```

**Required:**
- 1 agent with LLM credentials
- 3 MCP servers (no LLM credentials needed)

### Pattern 3: Multi-Agent Collaboration

```yaml
apiVersion: casa.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: multi-agent-system
  namespace: my-namespace
spec:
  name: "Multi-Agent System"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
  apps:
    - name: orchestrator-agent
      type: agent
      kubernetesWorkloadName: orchestrator
      baseUrl:
        host: orchestrator:8080
        scheme: http
      httpRequestSchema:
        promptFieldJsonPath: '{.prompt}'
    - name: research-agent
      type: agent
      kubernetesWorkloadName: research
      baseUrl:
        host: research:8080
        scheme: http
    - name: writing-agent
      type: agent
      kubernetesWorkloadName: writing
      baseUrl:
        host: writing:8080
        scheme: http
    - name: tools-mcp
      type: mcp_server
      kubernetesWorkloadName: tools-mcp
      baseUrl:
        host: tools-mcp:3000
        scheme: http
```

**Required:**
- 3 agents (each with LLM credentials)
- 1 MCP server for shared tools

## Complete Example: Deploy a Working MAS

Here's a complete example using a demo agent:

### Step 1: Create namespace and secrets

```bash
kubectl create namespace demo-mas

kubectl create secret generic openai-key \
  --from-literal=api-key='sk-proj-...' \
  -n demo-mas
```

### Step 2: Deploy agent

```yaml
# demo-agent.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-agent
  namespace: demo-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-agent
  template:
    metadata:
      labels:
        app: demo-agent
    spec:
      containers:
      - name: agent
        image: 626007623524.dkr.ecr.us-east-2.amazonaws.com/outshift-casa/demo-agent:latest
        ports:
        - containerPort: 8082
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-key
              key: api-key
        - name: MODEL
          value: "gpt-4"
        - name: PORT
          value: "8082"
---
apiVersion: v1
kind: Service
metadata:
  name: demo-agent
  namespace: demo-mas
spec:
  selector:
    app: demo-agent
  ports:
  - port: 8082
    targetPort: 8082
```

```bash
kubectl apply -f demo-agent.yaml
kubectl wait --for=condition=ready pod -l app=demo-agent -n demo-mas --timeout=60s
```

### Step 3: Deploy MCP server

```yaml
# demo-mcp.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-mcp
  namespace: demo-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-mcp
  template:
    metadata:
      labels:
        app: demo-mcp
    spec:
      containers:
      - name: mcp
        image: 626007623524.dkr.ecr.us-east-2.amazonaws.com/outshift-casa/demo-mcp:latest
        ports:
        - containerPort: 3000
        env:
        - name: PORT
          value: "3000"
---
apiVersion: v1
kind: Service
metadata:
  name: demo-mcp
  namespace: demo-mas
spec:
  selector:
    app: demo-mcp
  ports:
  - port: 3000
    targetPort: 3000
```

```bash
kubectl apply -f demo-mcp.yaml
kubectl wait --for=condition=ready pod -l app=demo-mcp -n demo-mas --timeout=60s
```

### Step 4: Create MAS

```yaml
# demo-mas.yaml
apiVersion: casa.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: demo-mas
  namespace: demo-mas
spec:
  name: "Demo MAS"
  enabledToolChecks:
    - DETERMINISTIC_TOOL_SELECTED
  apps:
    - name: demo-agent
      type: agent
      kubernetesWorkloadName: demo-agent
      baseUrl:
        host: demo-agent:8082
        scheme: http
      httpRequestSchema:
        promptFieldJsonPath: '{.conversation}'
    - name: demo-mcp
      type: mcp_server
      kubernetesWorkloadName: demo-mcp
      baseUrl:
        host: demo-mcp:3000
        scheme: http
```

```bash
kubectl apply -f demo-mas.yaml

# Wait for registration
sleep 10

# Check status
kubectl get mas demo-mas -n demo-mas
# NAME       PHASE    APPS READY   REALM        AGE
# demo-mas   Active   2            demo-realm   10s
```

### Step 5: Verify everything works

```bash
# Check all pods
kubectl get pods -n demo-mas
# NAME                         READY   STATUS    RESTARTS   AGE
# demo-agent-xxxxx             2/2     Running   0          2m
# demo-mcp-xxxxx               2/2     Running   0          2m

# Check MAS status
kubectl get mas demo-mas -n demo-mas -o jsonpath='{.status}' | jq
# {
#   "appsReady": 2,
#   "phase": "Active",
#   "message": "Registered 2 apps",
#   "lastSyncTime": "..."
# }

# Check operator logs
kubectl logs -n casa-control-plane-dev deployment/casa-operator -c operator --tail=20
# Should show successful sync
```

## Troubleshooting

### MAS Shows "Failed" Status

**Check operator logs:**
```bash
kubectl logs -n casa-control-plane-dev deployment/casa-operator -c operator --tail=50
```

**Common issues:**
- App baseUrl not reachable from auth-service
- Auth-service timeout (apps not responding)
- Keycloak connection issues

### Apps Not Registered (appsReady < expected)

**Check auth-service logs:**
```bash
kubectl logs -n casa-control-plane-dev deployment/casa-auth-service -c auth-service --tail=50
```

**Common issues:**
- App baseUrl invalid (wrong service name or port)
- App not ready (still starting up)
- Database errors

### Agent Can't Get LLM Key

**Check secret exists:**
```bash
kubectl get secret llm-credentials -n my-namespace -o yaml
```

**Check pod environment:**
```bash
kubectl exec -n my-namespace deployment/my-agent -- env | grep API_KEY
```

### Service Name Resolution Fails

**Test DNS resolution:**
```bash
kubectl run -n my-namespace test-dns --image=busybox:1.28 --rm -it --restart=Never -- nslookup my-agent
```

**Common issues:**
- Service and pod in different namespaces
- Service name typo in baseUrl
- Service not created yet

## Clean Up

To remove everything:

```bash
# Delete MAS (operator will clean up Keycloak realm)
kubectl delete mas demo-mas -n demo-mas

# Delete applications
kubectl delete deployment demo-agent demo-mcp -n demo-mas
kubectl delete service demo-agent demo-mcp -n demo-mas

# Delete secrets
kubectl delete secret openai-key -n demo-mas

# Delete namespace (optional)
kubectl delete namespace demo-mas
```

## Summary Checklist

- [ ] Control plane deployed (auth-service, operator, Keycloak, postgres)
- [ ] LLM API keys available (for agents)
- [ ] Agent Docker image built and pushed
- [ ] MCP server Docker image built and pushed (if applicable)
- [ ] Namespace created
- [ ] Secrets created (LLM keys, database credentials)
- [ ] Agent deployment + service created
- [ ] MCP server deployment + service created (if applicable)
- [ ] All pods showing 2/2 Ready
- [ ] MultiAgentSystem CRD created
- [ ] MAS status shows `phase: Active`
- [ ] MAS status shows correct `appsReady` count
- [ ] Keycloak realm created with app clients

## Next Steps

After successful deployment:
1. Test agent functionality (make requests)
2. Monitor operator logs for any reconciliation issues
3. Set up observability (metrics, traces)
4. Configure resource limits based on load
5. Enable autoscaling if needed

For more details, see:
- [CRD_OPERATOR.md](./CRD_OPERATOR.md) - Complete operator documentation
- [examples/](../../demo/) - More example configurations
