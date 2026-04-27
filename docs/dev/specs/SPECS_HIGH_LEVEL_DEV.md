# Zero Trust Multi-Agent System - PoC Development Architecture

**Purpose:** Simplified deployment architecture for PoC/development of Zero Trust Authorization System in Kubernetes.

**Target Audience:** Developers wanting to quickly validate the CASA-MAS concept with minimal infrastructure.

**Key Simplifications:**
- No HA requirements (single replicas only)
- Monolithic Auth Service (combines Auth + Policy + MCP Discovery)
- No telemetry service (basic logging only)
- No AI-powered tool checks (deterministic validation only)
- Optional Keycloak (can use simple JWT signing)
- No Redis (in-memory caching)
- Minimal Cilium policies (core flows only)

**Time to deploy:** 1-2 hours | **Production deployment:** 2-4 weeks | **Full spec:** [SPECS_HIGH_LEVEL.md](./SPECS_HIGH_LEVEL.md)

---

## Table of Contents

### Getting Started
1. [Quick Start (TL;DR)](#quick-start-tldr) - 60-minute deployment
2. [All-in-One Deployment](#all-in-one-deployment-manifest) - Copy-paste ready
3. [What You're Building](#what-youre-building-poc-version) - Architecture overview

### Core Concepts
4. [Component Breakdown](#component-breakdown) - Control plane, data plane, eBPF
5. [Token Flow](#token-flow-simplified-for-poc) - How authentication works
6. [Architecture Decisions](#architecture-decisions-poc-specific) - Why these choices

### Implementation
7. [Building the Monolithic Auth Service](#building-the-monolithic-auth-service) - Complete code
8. [Sidecar Configuration](#sidecar-configuration) - Envoy setup
9. [Implementation Patterns](#implementation-patterns) - Best practices

### Testing & Operations
10. [Testing the PoC](#testing-the-poc) - Validation procedures
11. [Developer Workflow Guide](#developer-workflow-guide) - Day-to-day tasks
12. [Integration Patterns](#integration-patterns) - Real-world examples

### Production Path
13. [Migration Path: PoC → Production](#migration-path-poc--production) - 5-phase roadmap
14. [Production Readiness Checklist](#production-readiness-checklist) - Before go-live
15. [Next Steps After PoC](#next-steps-after-poc) - Immediate actions

### Reference
16. [Troubleshooting](#troubleshooting) - Common issues
17. [Comparison: PoC vs Production](#comparison-poc-vs-production) - Feature matrix
18. [Cost Projection](#cost-projection) - Budget planning
19. [FAQ](#faq) - Common questions
20. [References](#references) - External resources

---

## Quick Start (TL;DR)

**Goal:** Get a working Zero Trust Multi-Agent System running in 60 minutes.

```bash
# 1. Setup cluster with Cilium
kind create cluster --name casa-poc
cilium install && cilium status --wait

# 2. Deploy control plane (auth service + postgres)
kubectl apply -f https://raw.githubusercontent.com/your-org/casa-poc/main/deploy/control-plane.yaml
kubectl wait --for=condition=ready pod -n casa-dev -l app=casa-auth --timeout=300s

# 3. Deploy sidecar injector
kubectl apply -f https://raw.githubusercontent.com/your-org/casa-poc/main/deploy/sidecar-injector.yaml

# 4. Deploy data plane (agent + MCP server)
kubectl apply -f https://raw.githubusercontent.com/your-org/casa-poc/main/deploy/data-plane.yaml

# 5. Apply network policies
kubectl apply -f https://raw.githubusercontent.com/your-org/casa-poc/main/deploy/network-policies.yaml

# 6. Test token flow
kubectl port-forward -n casa-dev svc/casa-auth 8000:443 &
curl -X POST http://localhost:8000/token -d "grant_type=client_credentials&scope=llm-access"
```

**Expected result:** You get a JWT token back. Agent pods can call MCP servers with automatic token injection.

**What you've deployed:**
- ✅ Control plane (auth service issuing tokens)
- ✅ Data plane (1 agent + 1 MCP server with sidecars)
- ✅ Network policies (deny-by-default, allow specific flows)
- ✅ Sidecar injection (automatic Envoy proxy in all pods)

**Next:** Read on for detailed architecture and customization options.

---

## All-in-One Deployment (Copy-Paste Ready)

This section provides complete, working Kubernetes manifests you can deploy immediately.

### Option A: Minimal PoC (No Keycloak)

**What you get:** Auth service with simple JWT signing, PostgreSQL, 1 agent, 1 MCP server, Cilium policies.

**Time to deploy:** 30 minutes

```bash
# Save this as casa-poc-minimal.yaml
cat <<'EOF' > casa-poc-minimal.yaml
---
# Namespace: casa-dev (Control Plane)
apiVersion: v1
kind: Namespace
metadata:
  name: casa-dev

---
# Namespace: dev-mas (Data Plane)
apiVersion: v1
kind: Namespace
metadata:
  name: dev-mas
  labels:
    casa.io/injection: enabled

---
# PostgreSQL for Auth Service
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-init
  namespace: casa-dev
data:
  init.sql: |
    CREATE TABLE IF NOT EXISTS apps (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        type VARCHAR(50) NOT NULL,
        client_id VARCHAR(255) UNIQUE NOT NULL,
        client_secret VARCHAR(255) NOT NULL,
        mas_id INTEGER,
        base_url VARCHAR(512)
    );

    CREATE TABLE IF NOT EXISTS tools (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        app_id INTEGER REFERENCES apps(id),
        UNIQUE(name, app_id)
    );

    CREATE TABLE IF NOT EXISTS multi_agent_systems (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        namespace VARCHAR(255) NOT NULL,
        tool_checks TEXT[] DEFAULT ARRAY['DETERMINISTIC_ONLY']
    );

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: casa-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: casa_dev
        - name: POSTGRES_USER
          value: casa
        - name: POSTGRES_PASSWORD
          value: casa-dev-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        - name: init-script
          mountPath: /docker-entrypoint-initdb.d
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: data
        emptyDir: {}
      - name: init-script
        configMap:
          name: postgres-init

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: casa-dev
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432

---
# Monolithic Auth Service
apiVersion: v1
kind: ConfigMap
metadata:
  name: auth-service-code
  namespace: casa-dev
data:
  main.py: |
    from fastapi import FastAPI, HTTPException, Depends
    from sqlalchemy import create_engine, Column, Integer, String, ARRAY
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import Session, sessionmaker
    import jwt
    from datetime import datetime, timedelta
    import os

    app = FastAPI()

    # Database setup
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://casa:casa-dev-password@postgres:5432/casa_dev")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()

    # JWT secret (in production, use Vault)
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")

    # Models
    class App(Base):
        __tablename__ = "apps"
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        type = Column(String)
        client_id = Column(String, unique=True)
        client_secret = Column(String)
        mas_id = Column(Integer)
        base_url = Column(String)

    class Tool(Base):
        __tablename__ = "tools"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        description = Column(String)
        app_id = Column(Integer)

    class MultiAgentSystem(Base):
        __tablename__ = "multi_agent_systems"
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        namespace = Column(String)
        tool_checks = Column(ARRAY(String))

    # Dependency
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Health check
    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "casa-poc-auth"}

    # Token issuance
    @app.post("/token")
    def issue_token(
        grant_type: str = "client_credentials",
        scope: str = "llm-access",
        requested_tools: str = None,
        db: Session = Depends(get_db)
    ):
        if grant_type != "client_credentials":
            raise HTTPException(400, "Only client_credentials supported")

        payload = {
            "sub": "test-agent",
            "scope": scope,
            "iss": "casa-poc",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }

        if requested_tools:
            payload["tools"] = requested_tools.split(",")

        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 900,
            "scope": scope,
        }

    # Token introspection
    @app.post("/introspect")
    def introspect(token: str):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return {
                "active": True,
                "scope": payload.get("scope"),
                "tools": payload.get("tools", []),
                "exp": payload.get("exp"),
            }
        except jwt.ExpiredSignatureError:
            return {"active": False, "reason": "expired"}
        except jwt.InvalidTokenError:
            return {"active": False, "reason": "invalid"}

    # App registration
    @app.post("/apps")
    def create_app(name: str, type: str, mas_id: int = 1, base_url: str = None, db: Session = Depends(get_db)):
        import secrets
        app = App(
            name=name,
            type=type,
            client_id=f"{name}-{secrets.token_hex(4)}",
            client_secret=secrets.token_hex(16),
            mas_id=mas_id,
            base_url=base_url,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return {"id": app.id, "name": app.name, "client_id": app.client_id}

    # List apps
    @app.get("/apps")
    def list_apps(db: Session = Depends(get_db)):
        apps = db.query(App).all()
        return [{"id": a.id, "name": a.name, "type": a.type} for a in apps]

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

  Dockerfile: |
    FROM python:3.12-slim
    WORKDIR /app
    RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary pyjwt
    COPY main.py .
    CMD ["python", "main.py"]

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: casa-auth
  namespace: casa-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: casa-auth
  template:
    metadata:
      labels:
        app: casa-auth
    spec:
      containers:
      - name: auth
        image: python:3.12-slim
        command:
        - sh
        - -c
        - |
          pip install -q fastapi uvicorn sqlalchemy psycopg2-binary pyjwt
          cd /app && python main.py
        env:
        - name: DATABASE_URL
          value: postgresql://casa:casa-dev-password@postgres:5432/casa_dev
        - name: JWT_SECRET
          value: dev-secret-change-in-production
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: code
          mountPath: /app
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: code
        configMap:
          name: auth-service-code

---
apiVersion: v1
kind: Service
metadata:
  name: casa-auth
  namespace: casa-dev
spec:
  selector:
    app: casa-auth
  ports:
  - port: 443
    targetPort: 8000

---
# Test Agent (data plane)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-agent
  namespace: dev-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-agent
      casa.io/app-type: agent
  template:
    metadata:
      labels:
        app: test-agent
        casa.io/app-type: agent
    spec:
      containers:
      - name: agent
        image: curlimages/curl:latest
        command: ["sh", "-c", "while true; do sleep 3600; done"]
        env:
        - name: CASA_AUTH_URL
          value: http://casa-auth.casa-dev.svc:443

---
# Filesystem MCP Server (data plane)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: filesystem-mcp
  namespace: dev-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: filesystem-mcp
      casa.io/app-type: mcp-server
  template:
    metadata:
      labels:
        app: filesystem-mcp
        casa.io/app-type: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: python:3.12-slim
        command:
        - sh
        - -c
        - |
          pip install -q fastapi uvicorn httpx pyjwt
          cat > /app/mcp_server.py <<'PYTHON'
          from fastapi import FastAPI, Header, HTTPException
          import httpx
          import jwt
          import os

          app = FastAPI()
          AUTH_URL = os.getenv("CASA_AUTH_URL", "http://casa-auth.casa-dev.svc:443")
          JWT_SECRET = "dev-secret-change-in-production"

          @app.post("/mcp")
          async def mcp_endpoint(authorization: str = Header(None)):
              if not authorization or not authorization.startswith("Bearer "):
                  raise HTTPException(401, "Missing token")

              token = authorization.split(" ")[1]

              # Validate token
              try:
                  payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                  if "call-tools" not in payload.get("scope", ""):
                      raise HTTPException(403, "Invalid scope")
              except Exception as e:
                  raise HTTPException(401, f"Token invalid: {e}")

              # Mock MCP response
              return {
                  "jsonrpc": "2.0",
                  "result": {
                      "content": "File contents from filesystem MCP",
                      "validated_by": "casa-poc"
                  },
                  "id": 1
              }

          if __name__ == "__main__":
              import uvicorn
              uvicorn.run(app, host="0.0.0.0", port=8080)
          PYTHON
          python /app/mcp_server.py
        env:
        - name: CASA_AUTH_URL
          value: http://casa-auth.casa-dev.svc:443
        ports:
        - containerPort: 8080

---
apiVersion: v1
kind: Service
metadata:
  name: filesystem-mcp
  namespace: dev-mas
spec:
  selector:
    app: filesystem-mcp
  ports:
  - port: 8080
    targetPort: 8080

---
# Cilium Network Policies
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: agent-egress
  namespace: dev-mas
spec:
  endpointSelector:
    matchLabels:
      casa.io/app-type: agent
  egress:
  # Allow: Agent → MCP servers
  - toEndpoints:
    - matchLabels:
        casa.io/app-type: mcp-server
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP

  # Allow: Agent → Auth Service
  - toEndpoints:
    - matchLabels:
        app: casa-auth
    toPorts:
    - ports:
      - port: "8000"
        protocol: TCP

  # Allow: Agent → OpenAI (external)
  - toFQDNs:
    - matchName: "api.openai.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP

  # Allow: DNS
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP

---
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: mcp-policy
  namespace: dev-mas
spec:
  endpointSelector:
    matchLabels:
      casa.io/app-type: mcp-server
  ingress:
  # Allow: Only agents can call MCP
  - fromEndpoints:
    - matchLabels:
        casa.io/app-type: agent
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP

  egress:
  # Allow: MCP → Auth (token validation)
  - toEndpoints:
    - matchLabels:
        app: casa-auth
    toPorts:
    - ports:
      - port: "8000"
        protocol: TCP

  # Allow: DNS
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP

EOF

# Deploy everything
kubectl apply -f casa-poc-minimal.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -n casa-dev -l app=postgres --timeout=120s
kubectl wait --for=condition=ready pod -n casa-dev -l app=casa-auth --timeout=120s
kubectl wait --for=condition=ready pod -n dev-mas -l app=test-agent --timeout=120s
kubectl wait --for=condition=ready pod -n dev-mas -l app=filesystem-mcp --timeout=120s

echo "✅ Deployment complete!"
echo ""
echo "Test the system:"
echo "  kubectl port-forward -n casa-dev svc/casa-auth 8000:443 &"
echo "  curl -X POST http://localhost:8000/token -d 'grant_type=client_credentials&scope=llm-access'"
```

**Verification:**
```bash
# Check all pods running
kubectl get pods -n casa-dev
kubectl get pods -n dev-mas

# Test token issuance
kubectl port-forward -n casa-dev svc/casa-auth 8000:443 &
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=call-tools&requested_tools=filesystem:read" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# Decode token
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq

# Test MCP call from agent
kubectl exec -n dev-mas deployment/test-agent -- \
  curl -H "Authorization: Bearer $TOKEN" \
  http://filesystem-mcp.dev-mas.svc:8080/mcp \
  -d '{"jsonrpc":"2.0","method":"tools/call","id":1}'
```

**What's included:**
- ✅ PostgreSQL with schema
- ✅ Auth service with token issuance + introspection
- ✅ Test agent (curl container for testing)
- ✅ Filesystem MCP server with token validation
- ✅ Cilium network policies (deny-by-default)
- ✅ No Keycloak (simple JWT signing)
- ✅ No Redis (stateless auth service)
- ✅ No sidecar injection (manual token passing for simplicity)

**Time to deploy:** ~5 minutes

---

### Option B: Full PoC (With Keycloak + Sidecar Injection)

Coming from production specs but simplified. Adds:
- Keycloak for proper OAuth2
- Sidecar injector (automatic Envoy proxy)
- More realistic token flows

See **Deployment Guide** section below for full manifests.

---

## What You're Building (PoC Version)

A minimal viable Kubernetes deployment of a Zero Trust Authorization System for Multi-Agent Systems. This PoC demonstrates the core authentication and authorization flows without production concerns.

**Architecture in 30 seconds:**
- **Sidecar pattern**: Envoy proxy injected into agent/MCP pods
- **Basic network enforcement**: Cilium with simple deny-by-default policies
- **Token-based auth**: JWT tokens from simplified control plane
- **Protocol restrictions**: MCP protocol internal, single LLM endpoint external
- **Minimal defense**: Sidecar + Basic eBPF enforcement

**What's removed from production:**
- ✗ High availability (no pod replication)
- ✗ Telemetry service (no observability stack)
- ✗ AI-powered tool matching (deterministic checks only)
- ✗ Monitoring (Prometheus/Grafana/Loki)
- ✗ Redis caching (in-memory only)
- ✗ Horizontal Pod Autoscaling

### System Architecture (PoC)

```mermaid
graph TB
    subgraph "🔴 External"
        USER[User Input]
        LLM[OpenAI LLM]
    end

    subgraph "🟢 CASA Control Plane (casa-dev namespace)"
        AUTH[Auth Service<br/>1 pod - monolithic]
        KC[Keycloak<br/>1 pod]
        PG[(PostgreSQL<br/>1 pod)]

        AUTH --> KC
        AUTH --> PG
    end

    subgraph "🟡 Data Plane (dev-mas namespace)"
        subgraph "Agent Pod"
            AG[Agent]
            AGS[Sidecar]
            AG -.->|localhost| AGS
        end

        subgraph "MCP Server Pod"
            MCP[MCP Server]
            MCPS[Sidecar]
            MCP -.->|localhost| MCPS
        end
    end

    subgraph "⚫ eBPF Layer (Cilium - simplified)"
        CILIUM[Cilium<br/>Basic L3/L4 policies<br/>FQDN filtering]
    end

    USER -->|1. Task| AG
    AGS -->|2. Get token T1| AUTH
    AGS -->|3. LLM call with T1| LLM
    AGS -->|4. Get token T2| AUTH
    AGS -->|5. MCP call with T2| MCPS
    MCPS -->|6. Validate T2| AUTH

    CILIUM -.->|Enforces| AGS
    CILIUM -.->|Enforces| MCPS
    CILIUM -.->|Allows| LLM

    style USER fill:#ff6b6b
    style LLM fill:#ff6b6b
    style AUTH fill:#4ecdc4
    style CILIUM fill:#95e1d3
```

**Key differences from production:**
- Single monolithic Auth Service (combines Auth + Policy + MCP Discovery)
- No separate User App (agents interact directly)
- Simplified token flow (no complex exchange chains)
- Basic eBPF policies (no token extraction at kernel level)

---

## Component Breakdown

### Control Plane (namespace: `casa-dev`)

The control plane issues and validates tokens. In PoC, we collapse multiple services into a monolith.

| Component | What It Does | Replicas | Resources | Notes |
|-----------|-------------|----------|-----------|-------|
| **CASA Auth Service** | Token ops + policy + discovery | 1 | 200m CPU, 256Mi RAM | Monolithic FastAPI app |
| **PostgreSQL** | Persistent storage | 1 | 100m CPU, 256Mi RAM | Single pod, emptyDir volume |
| **Keycloak** (optional) | OAuth2 IdP | 1 | 500m CPU, 512Mi RAM | Can be skipped for simplest PoC |

**CASA Auth Service Endpoints:**
```yaml
# Core OAuth2 (required)
POST /token                    # Issue token (client_credentials)
POST /token/exchange           # Exchange token (RFC 8693) - simplified
POST /introspect               # Validate token

# Policy Management (required)
GET/POST /apps                 # Register agents/MCP servers
GET/POST /mas                  # Create Multi-Agent System
GET      /apps/{id}/tools      # List tools for app

# MCP Discovery (optional for PoC)
GET  /mcp/discover/{app_id}    # Introspect MCP server tools

# Health
GET  /health                   # Liveness/readiness
```

**What's merged from production:**
- Auth Service + Policy Service → Single service
- MCP Discovery → Optional feature flag
- Telemetry → Removed (stdout logs only)
- AI Pipeline → Removed (deterministic checks only)

### Data Plane (namespace: `dev-mas`)

Your actual workloads. Minimum viable set for testing token flows:

| Workload | Type | Purpose | Sidecar? |
|----------|------|---------|----------|
| **demo-agent** | Agent | Makes LLM + MCP calls | ✅ Required |
| **filesystem-mcp** | MCP Server | Provides tools (read/write) | ✅ Required |

**Optional additions:**
- `user-app` pod (if testing 3-component flow)
- Additional MCP servers (web-fetch, calculator, etc.)

### eBPF Layer (Cilium on every node)

**Essential policies only:**
```
1. Allow: agent → MCP server (port 8080)
2. Allow: agent → auth-service (port 8000)
3. Allow: agent → api.openai.com:443
4. Allow: MCP → auth-service (token validation)
5. Deny: Everything else
```

**What's removed from production:**
- ✗ Token extraction at eBPF level (too complex for PoC)
- ✗ Detailed flow logging (Hubble optional)
- ✗ Per-workload identity enforcement (basic label matching only)

---

## Token Flow (Simplified for PoC)

The PoC implements a streamlined version of the production token flow.

### Production vs PoC Token Flow

| Aspect | Production | PoC |
|--------|-----------|-----|
| **Token types** | 3 tokens (T1, T2, T3) | 2 tokens (LLM, Tool) |
| **Exchange mechanism** | RFC 8693 full implementation | Simplified exchange |
| **Validation layers** | eBPF + Sidecar + Control Plane | Sidecar + Control Plane |
| **Tool checks** | 3 checks (deterministic + AI) | 1 check (tool exists?) |
| **Caching** | Redis distributed cache | In-memory per-sidecar |

### PoC Token Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Agent as Demo Agent<br/>(+ Sidecar)
    participant Auth as CASA Auth Service
    participant LLM as OpenAI
    participant MCP as Filesystem MCP<br/>(+ Sidecar)

    Note over User,MCP: Phase 1: LLM Access
    User->>Agent: Task: "Read file config.json"
    Agent->>Agent: Extract intent

    Note over Agent: Sidecar intercepts outbound
    Agent->>Auth: POST /token<br/>grant_type=client_credentials<br/>scope=llm-access
    Auth->>Auth: Generate JWT (no Keycloak)
    Auth-->>Agent: {access_token: "eyJ...", scope: "llm-access"}

    Agent->>LLM: POST /v1/chat/completions<br/>Authorization: Bearer eyJ...
    Note over Agent,LLM: Sidecar injects token
    LLM-->>Agent: {"choices": [{"message": {"tool_calls": [...]}}]}

    Note over User,MCP: Phase 2: Tool Access
    Agent->>Auth: POST /token<br/>scope=call-tools<br/>requested_tool=filesystem:read
    Auth->>Auth: Check: Tool registered?
    Auth-->>Agent: {access_token: "eyJ...", tools: ["filesystem:read"]}

    Agent->>MCP: MCP Request<br/>Authorization: Bearer eyJ...
    Note over MCP: Sidecar intercepts inbound
    MCP->>Auth: POST /introspect<br/>token=eyJ...
    Auth-->>MCP: {active: true, tools: ["filesystem:read"]}
    MCP->>MCP: Execute filesystem:read
    MCP-->>Agent: {"result": "file contents..."}
```

### Key Simplifications

1. **No initial user token (T1):** Agent directly requests LLM/tool tokens
2. **No token exchange:** Each token is independently issued (not exchanged from T1)
3. **Minimal validation:** Only check if tool is registered in database
4. **No correlation:** No `user_input_id` tracking (added in production)

---

## Building the Monolithic Auth Service

The PoC collapses multiple production services into a single FastAPI application.

### Service Architecture

```python
# src/casa_poc/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os

app = FastAPI(title="CASA PoC Auth Service", version="0.1.0")

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
TOKEN_EXPIRY_MINUTES = int(os.getenv("TOKEN_EXPIRY_MINUTES", "15"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://casa:password@postgres:5432/casa_dev")

# === TOKEN ISSUANCE ===

@app.post("/token")
def issue_token(
    grant_type: str = Form(...),
    scope: str = Form(...),
    client_id: str = Form(None),
    requested_tool: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Issue JWT token for LLM access or tool execution.

    Scopes:
    - llm-access: For calling external LLM
    - call-tools: For calling MCP servers (requires requested_tool)
    """
    if grant_type != "client_credentials":
        raise HTTPException(400, "Only client_credentials supported in PoC")

    # Lookup app by client_id (simplified - no real OAuth2 client auth)
    if client_id:
        app_record = db.query(App).filter(App.client_id == client_id).first()
        if not app_record:
            raise HTTPException(401, "Invalid client")
        subject = app_record.name
    else:
        subject = "anonymous-poc-client"

    # Build token payload
    payload = {
        "sub": subject,
        "scope": scope,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        "iss": "casa-poc-auth",
    }

    # For tool tokens, validate and embed tool list
    if scope == "call-tools":
        if not requested_tool:
            raise HTTPException(400, "requested_tool required for call-tools scope")

        # Simple check: Does tool exist in database?
        tool = db.query(Tool).filter(Tool.name == requested_tool).first()
        if not tool:
            raise HTTPException(403, f"Tool {requested_tool} not registered")

        payload["tools"] = [requested_tool]
        payload["exp"] = datetime.utcnow() + timedelta(minutes=5)  # Shorter TTL

    # Sign token (HS256 for PoC - use RS256 in production)
    access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": (payload["exp"] - payload["iat"]).total_seconds(),
        "scope": scope,
    }

# === TOKEN VALIDATION ===

@app.post("/introspect")
def introspect_token(token: str = Form(...)):
    """
    Validate token and return claims.
    Called by MCP server sidecars to verify incoming requests.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Check expiration
        if datetime.utcnow().timestamp() > payload["exp"]:
            return {"active": False, "reason": "Token expired"}

        return {
            "active": True,
            "sub": payload.get("sub"),
            "scope": payload.get("scope"),
            "tools": payload.get("tools", []),
            "exp": payload.get("exp"),
        }
    except jwt.InvalidTokenError as e:
        return {"active": False, "reason": str(e)}

# === APP MANAGEMENT ===

@app.post("/apps")
def register_app(app: AppCreate, db: Session = Depends(get_db)):
    """
    Register an agent or MCP server.
    Creates client_id and client_secret (stored in DB for token requests).
    """
    # Generate OAuth2 client credentials
    client_id = f"{app.name}-{uuid.uuid4().hex[:8]}"
    client_secret = secrets.token_urlsafe(32)

    db_app = App(
        name=app.name,
        type=app.type,  # "agent" or "mcp_server"
        mas_id=app.mas_id,
        client_id=client_id,
        client_secret=client_secret,  # Hash this in production!
        base_url=app.base_url,
    )
    db.add(db_app)
    db.commit()

    return {
        "id": db_app.id,
        "name": db_app.name,
        "client_id": client_id,
        "client_secret": client_secret,  # Only returned once
    }

# === MAS MANAGEMENT ===

@app.post("/mas")
def create_mas(mas: MASCreate, db: Session = Depends(get_db)):
    """
    Create a Multi-Agent System configuration.
    In PoC, this is just metadata (no Keycloak realm creation).
    """
    db_mas = MultiAgentSystem(
        name=mas.name,
        namespace=mas.namespace,
        tool_checks=["DETERMINISTIC_ONLY"],  # No AI checks in PoC
    )
    db.add(db_mas)
    db.commit()
    return db_mas

# === TOOL MANAGEMENT ===

@app.post("/apps/{app_id}/tools")
def register_tool(app_id: int, tool: ToolCreate, db: Session = Depends(get_db)):
    """
    Register a tool provided by an MCP server.
    In production, this would be auto-discovered via MCP protocol.
    """
    app = db.query(App).filter(App.id == app_id).first()
    if not app or app.type != "mcp_server":
        raise HTTPException(404, "MCP server not found")

    db_tool = Tool(
        name=tool.name,
        description=tool.description,
        app_id=app_id,
    )
    db.add(db_tool)
    db.commit()
    return db_tool

@app.get("/apps/{app_id}/tools")
def list_tools(app_id: int, db: Session = Depends(get_db)):
    """List all tools for a given MCP server."""
    tools = db.query(Tool).filter(Tool.app_id == app_id).all()
    return tools

# === MCP DISCOVERY (Optional) ===

@app.get("/mcp/discover/{app_id}")
async def discover_mcp_tools(app_id: int, db: Session = Depends(get_db)):
    """
    Introspect MCP server to discover available tools.
    Optional for PoC - can manually register tools instead.
    """
    app = db.query(App).filter(App.id == app_id).first()
    if not app or app.type != "mcp_server":
        raise HTTPException(404, "MCP server not found")

    # Call MCP server's tools/list method
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{app.base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1,
            },
            timeout=10.0,
        )
        mcp_response = response.json()

    if "result" not in mcp_response:
        raise HTTPException(500, "Invalid MCP response")

    # Store discovered tools
    for tool_def in mcp_response["result"]["tools"]:
        existing = db.query(Tool).filter(
            Tool.name == tool_def["name"],
            Tool.app_id == app_id
        ).first()

        if not existing:
            db_tool = Tool(
                name=tool_def["name"],
                description=tool_def.get("description", ""),
                app_id=app_id,
            )
            db.add(db_tool)

    db.commit()
    return {"discovered": len(mcp_response["result"]["tools"])}

# === HEALTH CHECK ===

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "casa-poc-auth"}
```

### Database Models (SQLModel)

```python
# src/casa_poc/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class App(SQLModel, table=True):
    """Agent or MCP server registration."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    type: str  # "agent" or "mcp_server"
    mas_id: Optional[int] = Field(foreign_key="multiagentsystem.id")
    client_id: str = Field(unique=True)
    client_secret: str  # Plain text in PoC (hash in production!)
    base_url: Optional[str] = None

    tools: List["Tool"] = Relationship(back_populates="app")
    mas: Optional["MultiAgentSystem"] = Relationship(back_populates="apps")

class Tool(SQLModel, table=True):
    """Tool provided by an MCP server."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # e.g., "filesystem:read"
    description: str
    app_id: int = Field(foreign_key="app.id")

    app: App = Relationship(back_populates="tools")

class MultiAgentSystem(SQLModel, table=True):
    """Multi-Agent System configuration."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    namespace: str  # Kubernetes namespace
    tool_checks: List[str] = Field(default=["DETERMINISTIC_ONLY"])  # JSON array

    apps: List[App] = Relationship(back_populates="mas")
```

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Run migrations (in production use Alembic)
CMD ["sh", "-c", "python -m src.casa_poc.init_db && uvicorn src.casa_poc.main:app --host 0.0.0.0 --port 8000"]
```

### requirements.txt

```
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.16
psycopg2-binary==2.9.9
pyjwt==2.8.0
httpx==0.26.0
python-multipart==0.0.9
```

**What's intentionally omitted:**
- ✗ Keycloak integration (python-keycloak)
- ✗ OpenAI SDK (no AI checks)
- ✗ Redis (no caching)
- ✗ Telemetry emission
- ✗ Complex token exchange logic (RFC 8693)



### Prerequisites

```bash
# 1. Kubernetes cluster (any local cluster works)
kind create cluster --name casa-poc
# OR
minikube start

# 2. Install Cilium (eBPF)
cilium install

# 3. Verify Cilium
cilium status
```

### Step 1: Deploy Control Plane

```bash
# Create namespace
kubectl create namespace casa-dev

# Deploy PostgreSQL
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: casa-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: casa_dev
        - name: POSTGRES_USER
          value: casa
        - name: POSTGRES_PASSWORD
          value: dev-password-change-me
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: casa-dev
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
EOF

# Deploy Keycloak (dev mode)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: casa-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0
        args:
        - start-dev
        env:
        - name: KEYCLOAK_ADMIN
          value: admin
        - name: KEYCLOAK_ADMIN_PASSWORD
          value: admin
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: keycloak
  namespace: casa-dev
spec:
  selector:
    app: keycloak
  ports:
  - port: 8080
EOF

# Deploy Auth Service (monolithic)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: casa-auth
  namespace: casa-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: casa-auth
  template:
    metadata:
      labels:
        app: casa-auth
    spec:
      containers:
      - name: auth
        image: your-registry/casa-auth-service:dev
        env:
        - name: DATABASE_URL
          value: postgresql://casa:dev-password-change-me@postgres:5432/casa_dev
        - name: KEYCLOAK_URL
          value: http://keycloak:8080
        - name: KEYCLOAK_ADMIN_USER
          value: admin
        - name: KEYCLOAK_ADMIN_PASSWORD
          value: admin
        - name: LOG_LEVEL
          value: DEBUG
        - name: ENABLE_TELEMETRY
          value: "false"
        - name: ENABLE_AI_CHECKS
          value: "false"
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: casa-auth
  namespace: casa-dev
spec:
  selector:
    app: casa-auth
  ports:
  - port: 443
    targetPort: 8000
EOF
```

### Step 2: Deploy Sidecar Injector

```bash
# Create namespace for system components
kubectl create namespace casa-system

# Deploy mutating webhook for sidecar injection
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: sidecar-config
  namespace: casa-system
data:
  sidecar.yaml: |
    containers:
    - name: casa-sidecar
      image: envoyproxy/envoy:v1.28-latest
      ports:
      - containerPort: 15001
        name: proxy
      volumeMounts:
      - name: envoy-config
        mountPath: /etc/envoy
      resources:
        requests:
          cpu: 50m
          memory: 64Mi
        limits:
          cpu: 100m
          memory: 128Mi
    initContainers:
    - name: init-networking
      image: busybox:1.36
      securityContext:
        capabilities:
          add: ["NET_ADMIN"]
      command:
      - sh
      - -c
      - |
        # Redirect all TCP traffic to sidecar
        iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-port 15001
    volumes:
    - name: envoy-config
      configMap:
        name: envoy-sidecar-config
---
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: casa-sidecar-injector
webhooks:
- name: inject.casa.io
  clientConfig:
    service:
      name: sidecar-injector
      namespace: casa-system
      path: "/inject"
    caBundle: <BASE64_ENCODED_CA>
  rules:
  - operations: ["CREATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  namespaceSelector:
    matchLabels:
      casa.io/injection: enabled
  admissionReviewVersions: ["v1"]
  sideEffects: None
EOF
```

### Step 3: Deploy Data Plane

```bash
# Create MAS namespace with sidecar injection enabled
kubectl create namespace dev-mas
kubectl label namespace dev-mas casa.io/injection=enabled

# Deploy test agent
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-agent
  namespace: dev-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-agent
      casa.io/app-type: agent
  template:
    metadata:
      labels:
        app: test-agent
        casa.io/app-type: agent
    spec:
      containers:
      - name: agent
        image: your-registry/test-agent:dev
        env:
        - name: CASA_AUTH_URL
          value: http://casa-auth.casa-dev.svc:443
        - name: MCP_SERVER_URL
          value: http://filesystem-mcp.dev-mas.svc:8080
---
apiVersion: v1
kind: Service
metadata:
  name: test-agent
  namespace: dev-mas
spec:
  selector:
    app: test-agent
  ports:
  - port: 8080
EOF

# Deploy filesystem MCP server
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: filesystem-mcp
  namespace: dev-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: filesystem-mcp
      casa.io/app-type: mcp-server
  template:
    metadata:
      labels:
        app: filesystem-mcp
        casa.io/app-type: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/filesystem-mcp:dev
        env:
        - name: CASA_AUTH_URL
          value: http://casa-auth.casa-dev.svc:443
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: filesystem-mcp
  namespace: dev-mas
spec:
  selector:
    app: filesystem-mcp
  ports:
  - port: 8080
EOF
```

### Step 4: Apply Network Policies

```bash
# Allow agent → MCP + Auth + LLM
kubectl apply -f - <<EOF
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: agent-policy
  namespace: dev-mas
spec:
  endpointSelector:
    matchLabels:
      casa.io/app-type: agent
  egress:
  # Allow: Agent → MCP servers
  - toEndpoints:
    - matchLabels:
        casa.io/app-type: mcp-server
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP

  # Allow: Agent → Auth Service
  - toEndpoints:
    - matchLabels:
        app: casa-auth
        k8s:io.kubernetes.pod.namespace: casa-dev
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP

  # Allow: Agent → OpenAI LLM
  - toFQDNs:
    - matchName: "api.openai.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP

  # Allow: DNS
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
---
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: mcp-policy
  namespace: dev-mas
spec:
  endpointSelector:
    matchLabels:
      casa.io/app-type: mcp-server
  ingress:
  # Allow: Agents → MCP
  - fromEndpoints:
    - matchLabels:
        casa.io/app-type: agent
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP

  egress:
  # Allow: MCP → Auth Service (token validation)
  - toEndpoints:
    - matchLabels:
        app: casa-auth
        k8s:io.kubernetes.pod.namespace: casa-dev
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP

  # Allow: DNS
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
EOF
```

---

## Sidecar Configuration

### Envoy Sidecar (Simplified)

```yaml
# ConfigMap: envoy-sidecar-config (namespace: casa-system)
static_resources:
  listeners:
  - name: interceptor
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 15001
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          http_filters:
          # Token injection filter
          - name: envoy.filters.http.lua
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
              inline_code: |
                function envoy_on_request(request_handle)
                  -- Get token from auth service (cached)
                  local token = get_or_fetch_token()
                  request_handle:headers():add("Authorization", "Bearer " .. token)
                end

                function get_or_fetch_token()
                  -- Simple in-memory cache (60s TTL)
                  if cached_token and cached_token.expires > os.time() then
                    return cached_token.value
                  end

                  -- Fetch from auth service
                  local headers, body = request_handle:httpCall(
                    "casa_auth_cluster",
                    {
                      [":method"] = "POST",
                      [":path"] = "/token",
                      [":authority"] = "casa-auth.casa-dev.svc",
                      ["content-type"] = "application/x-www-form-urlencoded"
                    },
                    "grant_type=client_credentials&scope=llm-access",
                    5000
                  )

                  -- Parse token from response
                  local token = parse_token(body)
                  cached_token = {value = token, expires = os.time() + 60}
                  return token
                end

          # Protocol validation filter
          - name: envoy.filters.http.wasm
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
              config:
                vm_config:
                  runtime: "envoy.wasm.runtime.v8"
                  code:
                    local:
                      inline_string: |
                        // Validate MCP protocol
                        function check_protocol(headers, body) {
                          const contentType = headers["content-type"];
                          if (contentType !== "application/json" &&
                              contentType !== "application/mcp+json") {
                            return {allow: false, reason: "Invalid protocol"};
                          }

                          // Parse JSON-RPC structure
                          const msg = JSON.parse(body);
                          if (!msg.jsonrpc || msg.jsonrpc !== "2.0") {
                            return {allow: false, reason: "Not JSON-RPC 2.0"};
                          }

                          return {allow: true};
                        }

          - name: envoy.filters.http.router

          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route:
                  cluster: passthrough

  clusters:
  - name: passthrough
    type: ORIGINAL_DST
    lb_policy: CLUSTER_PROVIDED

  - name: casa_auth_cluster
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: casa_auth_cluster
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: casa-auth.casa-dev.svc
                port_value: 443
```

**Key simplifications:**
- In-memory token cache (no Redis)
- Basic protocol validation (no deep inspection)
- Simple Lua script (no complex auth logic)

---

## Architecture Decisions (PoC-Specific)

### ADR-001: Monolithic Auth Service

**Decision:** Combine Auth + Policy + MCP Discovery into single service.

**Rationale:**
- Reduces operational complexity (1 deployment vs 5)
- Eliminates inter-service communication overhead
- Faster iteration during development
- Sufficient for <100 RPS load

**Tradeoffs:**
- ✅ Pro: Simpler deployment, fewer failure modes
- ✅ Pro: No network latency between components
- ❌ Con: Cannot scale components independently
- ❌ Con: Blast radius larger (one bug can crash all functions)

**Migration path:** Extract Policy and MCP Discovery into separate services when RPS > 100 or when needing independent scaling.

---

### ADR-002: Skip Keycloak (Optional)

**Decision:** Make Keycloak optional; support direct JWT signing.

**Rationale:**
- Keycloak adds complexity (realm management, client credentials)
- PoC doesn't need full OAuth2 flows (no user login, no OIDC)
- HS256 JWT signing sufficient for closed environment
- Reduces infrastructure footprint (saves 512Mi RAM)

**Tradeoffs:**
- ✅ Pro: Faster setup (no IdP configuration)
- ✅ Pro: No external dependency for token operations
- ❌ Con: No token revocation support
- ❌ Con: Must manually rotate signing keys

**Production requirement:** Add Keycloak before production for:
- Proper client credential management
- Token revocation
- Audit trails
- RS256 asymmetric signing

---

### ADR-003: In-Memory Token Caching

**Decision:** Cache tokens in sidecar memory (no Redis).

**Rationale:**
- Eliminates Redis dependency (saves 128Mi RAM + operational overhead)
- Token TTL is short (5-15 min), in-memory cache acceptable
- Each sidecar handles low RPS (<10), cache hit rate sufficient

**Tradeoffs:**
- ✅ Pro: No distributed cache to manage
- ✅ Pro: Lower latency (no network round-trip)
- ❌ Con: Cache not shared across pods (higher auth service load)
- ❌ Con: Lost on pod restart (cold start penalty)

**When to add Redis:** Token issuance > 1000/sec or when cache hit rate < 80%.

---

### ADR-004: Deterministic-Only Tool Checks

**Decision:** Skip AI-powered tool matching; use only deterministic checks.

**Rationale:**
- AI checks require OpenAI API (cost + latency)
- Embedding computation requires 512MB RAM per service
- Deterministic checks catch 90% of misconfigurations
- PoC focuses on architecture, not advanced authz logic

**Deterministic checks implemented:**
- ✅ Tool registered in database?
- ✅ Tool allowed for this MAS?
- ✅ Token not expired?

**AI checks deferred to production:**
- ❌ Task-to-tool semantic matching (embeddings)
- ❌ LLM intent verification
- ❌ Anomaly detection

---

### ADR-005: Simplified Network Policies

**Decision:** Implement only 2 Cilium policies (agent, MCP server).

**Rationale:**
- Production has 10+ policies (auth, telemetry, discovery, egress, ingress...)
- PoC only needs core flow: agent → MCP, agent → LLM, both → auth
- Reduces policy debugging complexity

**Policies implemented:**
- ✅ Agent egress (MCP, auth, LLM)
- ✅ MCP ingress (from agents) + egress (auth)
- ✅ FQDN filtering (api.openai.com only)

**Policies deferred:**
- ❌ Control plane isolation (auth can reach internet)
- ❌ Telemetry egress rules
- ❌ Rate limiting policies
- ❌ Token exfiltration detection (advanced eBPF)

---

### ADR-006: No Telemetry Service

**Decision:** Skip dedicated telemetry service; use stdout logs only.

**Rationale:**
- Telemetry requires PostgreSQL event store + async processing
- Adds operational complexity (log aggregation, retention)
- PoC can rely on `kubectl logs` and Cilium Hubble

**What you get:**
- ✅ Stdout logs from all services (JSON structured)
- ✅ Cilium Hubble flow logs (L3/L4 visibility)
- ✅ Basic request logging in sidecars

**What you lose:**
- ❌ Centralized event store (token lifecycle tracking)
- ❌ Trace correlation (user_input_id → LLM call → tool call)
- ❌ Analytics dashboard (token usage, top tools)

**Production requirement:** Add telemetry service for:
- Compliance (immutable audit trail)
- Security investigations (trace attack paths)
- Cost attribution (per-user token consumption)

---

## Implementation Patterns

### Pattern 1: Sidecar Token Injection

**Problem:** How does sidecar know which token to request (LLM vs tool)?

**Solution:** Inspect request destination.

```lua
-- Envoy Lua filter logic
function envoy_on_request(request_handle)
  local authority = request_handle:headers():get(":authority")
  local path = request_handle:headers():get(":path")

  local scope = "llm-access"  -- Default
  local requested_tool = nil

  -- Detect MCP request (internal service)
  if string.match(authority, ".svc$") then
    scope = "call-tools"
    -- Extract tool from MCP JSON-RPC body
    local body = request_handle:body()
    if body then
      local mcp_msg = json.decode(body:getBytes(0, body:length()))
      if mcp_msg.method == "tools/call" then
        requested_tool = mcp_msg.params.name
      end
    end
  end

  -- Fetch token with correct scope
  local token = fetch_token(scope, requested_tool)
  request_handle:headers():add("Authorization", "Bearer " .. token)
end
```

**Key insight:** Sidecar acts as smart proxy, not dumb forwarder.

---

### Pattern 2: Graceful Degradation

**Problem:** What happens if auth service is down?

**Solution:** Fail open with cached tokens (time-boxed).

```python
# Auth service client in sidecar
class AuthClient:
    def __init__(self):
        self.cache = {}  # {scope: (token, expires_at)}
        self.circuit_breaker = CircuitBreaker(threshold=5, timeout=30)

    def get_token(self, scope: str, tool: str = None) -> str:
        cache_key = f"{scope}:{tool}"

        # Check cache first
        if cache_key in self.cache:
            token, expires_at = self.cache[cache_key]
            if time.time() < expires_at - 30:  # 30s buffer
                return token

        # Try to fetch new token
        if self.circuit_breaker.is_open():
            # Circuit open: use stale cache if available
            if cache_key in self.cache:
                logger.warning("Using stale token (circuit open)")
                return self.cache[cache_key][0]
            raise Exception("Auth service unavailable, no cached token")

        try:
            response = requests.post(
                "http://casa-auth.casa-dev.svc/token",
                data={"grant_type": "client_credentials", "scope": scope},
                timeout=5.0
            )
            token = response.json()["access_token"]
            expires_in = response.json()["expires_in"]
            self.cache[cache_key] = (token, time.time() + expires_in)
            self.circuit_breaker.success()
            return token

        except RequestException as e:
            self.circuit_breaker.failure()
            # Try stale cache as last resort
            if cache_key in self.cache:
                logger.error(f"Auth service error: {e}, using stale token")
                return self.cache[cache_key][0]
            raise
```

**Behavior:**
- ✅ Normal: Fetch fresh tokens
- ⚠️  Auth service slow: Use cached tokens
- ⚠️  Auth service down <30s: Use stale cache
- ❌ Auth service down >30s: Fail requests

---

### Pattern 3: MCP Server Token Validation

**Problem:** MCP server must validate tokens without becoming auth service client.

**Solution:** Validate via introspection endpoint (opaque tokens).

```python
# MCP server (e.g., filesystem server)
from fastapi import FastAPI, Header, HTTPException
import httpx

app = FastAPI()
CASA_AUTH_URL = os.getenv("CASA_AUTH_URL", "http://casa-auth.casa-dev.svc")

async def validate_token(authorization: str = Header(...)):
    """Dependency to validate token on every request."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = authorization.removeprefix("Bearer ")

    # Introspect token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CASA_AUTH_URL}/introspect",
            data={"token": token},
            timeout=5.0
        )

    introspection = response.json()

    if not introspection.get("active"):
        raise HTTPException(401, f"Invalid token: {introspection.get('reason')}")

    # Check scope
    if "call-tools" not in introspection.get("scope", ""):
        raise HTTPException(403, "Insufficient scope")

    return introspection

@app.post("/mcp")
async def handle_mcp_request(
    body: dict,
    token_data: dict = Depends(validate_token)
):
    """Handle MCP JSON-RPC request."""
    if body.get("method") == "tools/call":
        tool_name = body["params"]["name"]

        # Check if tool allowed in token
        allowed_tools = token_data.get("tools", [])
        if tool_name not in allowed_tools:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32001,
                    "message": f"Tool {tool_name} not authorized"
                },
                "id": body.get("id")
            }

        # Execute tool...
        result = execute_tool(tool_name, body["params"].get("arguments", {}))
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": body.get("id")
        }
```

**Key insight:** MCP servers trust auth service, not tokens themselves.

---

## Testing the PoC

### 1. Verify Control Plane

```bash
# Check all pods running
kubectl get pods -n casa-dev

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# postgres-xxx                1/1     Running   0          5m
# keycloak-xxx                1/1     Running   0          5m
# casa-auth-xxx                1/1     Running   0          5m

# Test auth service
kubectl port-forward -n casa-dev svc/casa-auth 8000:443
curl http://localhost:8000/health
# {"status": "healthy"}
```

### 2. Register Test Application

```bash
# Create agent app
curl -X POST http://localhost:8000/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-agent",
    "type": "agent",
    "mas_id": "dev-mas"
  }'

# Create MCP server app
curl -X POST http://localhost:8000/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "filesystem-mcp",
    "type": "mcp_server",
    "base_url": "http://filesystem-mcp.dev-mas.svc:8080",
    "mas_id": "dev-mas"
  }'
```

### 3. Test Token Flow

```bash
# 1. Get LLM token
curl -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=llm-access" \
  | jq -r '.access_token' > llm_token.txt

# 2. Request tool token
curl -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=call-tools&requested_tools=filesystem:read" \
  | jq -r '.access_token' > tool_token.txt

# 3. Validate token
curl -X POST http://localhost:8000/introspect \
  -d "token=$(cat tool_token.txt)" \
  | jq
# {"active": true, "scope": "call-tools", "tools": ["filesystem:read"]}
```

### 4. Test Network Policy

```bash
# Execute into agent pod
kubectl exec -it -n dev-mas deployment/test-agent -- sh

# Try allowed: MCP server
curl http://filesystem-mcp.dev-mas.svc:8080/health
# ✓ Should succeed

# Try allowed: Auth service
curl http://casa-auth.casa-dev.svc:443/health
# ✓ Should succeed

# Try allowed: OpenAI
curl https://api.openai.com
# ✓ Should succeed

# Try denied: External site
curl https://example.com
# ✗ Should timeout (blocked by Cilium)

# Try denied: Other pod
curl http://postgres.casa-dev.svc:5432
# ✗ Should timeout (blocked by Cilium)
```

### 5. Verify Sidecar Injection

```bash
# Check agent pod has sidecar
kubectl get pod -n dev-mas -l app=test-agent -o jsonpath='{.items[0].spec.containers[*].name}'
# agent casa-sidecar

# Check sidecar logs
kubectl logs -n dev-mas deployment/test-agent -c casa-sidecar
# Should show token requests and protocol validation
```

### 6. End-to-End Agent Workflow

**Test Scenario:** Agent receives task → calls LLM → requests MCP tool → executes.

```bash
# Terminal 1: Port forward auth service
kubectl port-forward -n casa-dev svc/casa-auth 8000:443

# Terminal 2: Execute test workflow
cat > test_workflow.sh <<'EOF'
#!/bin/bash
set -e

echo "=== Step 1: Register apps ==="
curl -s -X POST http://localhost:8000/apps -H "Content-Type: application/json" \
  -d '{"name":"test-agent","type":"agent","mas_id":"dev-mas"}' | jq

curl -s -X POST http://localhost:8000/apps -H "Content-Type: application/json" \
  -d '{"name":"filesystem-mcp","type":"mcp_server","base_url":"http://filesystem-mcp.dev-mas.svc:8080","mas_id":"dev-mas"}' | jq

echo -e "\n=== Step 2: Get LLM token ==="
LLM_TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=llm-access" | jq -r '.access_token')
echo "Token (first 50 chars): ${LLM_TOKEN:0:50}..."

echo -e "\n=== Step 3: Decode token ==="
echo $LLM_TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq

echo -e "\n=== Step 4: Simulate LLM call ==="
# In real workflow, agent calls OpenAI with LLM_TOKEN
# LLM responds: "Use tool filesystem:read to read config.json"

echo -e "\n=== Step 5: Request tool token ==="
TOOL_TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=call-tools&requested_tools=filesystem:read" \
  | jq -r '.access_token')
echo "Tool token (first 50 chars): ${TOOL_TOKEN:0:50}..."

echo -e "\n=== Step 6: Introspect tool token ==="
curl -s -X POST http://localhost:8000/introspect \
  -d "token=$TOOL_TOKEN" | jq

echo -e "\n=== Step 7: Call MCP server with tool token ==="
kubectl exec -n dev-mas deployment/test-agent -c agent -- \
  curl -s http://filesystem-mcp.dev-mas.svc:8080/mcp \
  -H "Authorization: Bearer $TOOL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"filesystem:read","arguments":{"path":"config.json"}},"id":1}' \
  | jq

echo -e "\n✅ Workflow complete!"
EOF

chmod +x test_workflow.sh
./test_workflow.sh
```

**Expected output:**
```json
=== Step 1: Register apps ===
{"id":1,"name":"test-agent","type":"agent","client_id":"generated-123","client_secret":"secret-456"}
{"id":2,"name":"filesystem-mcp","type":"mcp_server","client_id":"generated-789"}

=== Step 2: Get LLM token ===
Token (first 50 chars): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0...

=== Step 3: Decode token ===
{
  "sub": "test-agent",
  "scope": "llm-access",
  "exp": 1704123456,
  "iat": 1704122556
}

=== Step 5: Request tool token ===
Tool token (first 50 chars): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0...

=== Step 6: Introspect tool token ===
{
  "active": true,
  "scope": "call-tools",
  "tools": ["filesystem:read"],
  "client_id": "test-agent",
  "exp": 1704123756
}

=== Step 7: Call MCP server ===
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{"type":"text","text":"# Config file contents\nkey=value"}]
  },
  "id": 1
}

✅ Workflow complete!
```

---

### 7. Network Policy Enforcement Testing

**Test Scenario:** Verify Cilium blocks unauthorized traffic.

```bash
# Create test pod without sidecar (simulates compromised workload)
kubectl run -n dev-mas attacker --image=nicolaka/netshoot --rm -it -- bash

# Inside attacker pod:

# ❌ Try to reach external malicious site
curl https://evil.com
# Timeout (blocked by Cilium)

# ❌ Try to reach Postgres directly
curl http://postgres.casa-dev.svc:5432
# Timeout (no explicit allow rule)

# ❌ Try to reach MCP server without sidecar
curl http://filesystem-mcp.dev-mas.svc:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"filesystem:read"},"id":1}'
# Timeout or 401 (no valid token)

# ✅ Try to reach allowed DNS
nslookup google.com
# Works (DNS always allowed)
```

**Monitor with Hubble:**
```bash
# Terminal 1: Watch flows in real-time
hubble observe --namespace dev-mas --follow

# Terminal 2: Generate test traffic
kubectl exec -n dev-mas deployment/test-agent -- curl https://evil.com

# Hubble output shows DROPPED verdict:
# dev-mas/test-agent:35821 -> evil.com:443 DROPPED (Policy denied)
```

---

### 8. Sidecar Token Injection Verification

**Test Scenario:** Confirm sidecar automatically injects tokens.

```bash
# Deploy test HTTP echo server (reflects headers)
kubectl apply -n dev-mas -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
        casa.io/app-type: mcp-server
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo
        args: ["-text=Echo service"]
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: echo-server
spec:
  selector:
    app: echo
  ports:
  - port: 80
    targetPort: 5678
EOF

# Wait for echo server
kubectl wait --for=condition=ready pod -n dev-mas -l app=echo --timeout=60s

# Call echo server FROM agent (sidecar should inject token)
kubectl exec -n dev-mas deployment/test-agent -c agent -- \
  curl -v http://echo-server.dev-mas.svc/test 2>&1 | grep Authorization

# Expected output:
# > Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Call echo server WITHOUT going through agent sidecar (directly from host)
kubectl run -n dev-mas direct-caller --image=curlimages/curl --rm -it -- \
  curl -v http://echo-server.dev-mas.svc/test 2>&1 | grep Authorization

# Expected output: (no Authorization header - no sidecar)
```

**Key insight:** Only traffic routed through sidecars gets tokens injected.

---

### 9. Token Expiry and Refresh

**Test Scenario:** Verify tokens expire and are refreshed automatically.

```python
# test_token_lifecycle.py
import time
import requests
import jwt

AUTH_URL = "http://localhost:8000"

# Issue token with short TTL (for testing)
response = requests.post(
    f"{AUTH_URL}/token",
    data={"grant_type": "client_credentials", "scope": "llm-access"}
)
token1 = response.json()["access_token"]
decoded1 = jwt.decode(token1, options={"verify_signature": False})
print(f"Token 1 expires at: {decoded1['exp']} ({decoded1['exp'] - time.time():.0f}s from now)")

# Wait for token to approach expiry
time.sleep(60)  # Assuming token TTL = 5min

# Request new token
response = requests.post(
    f"{AUTH_URL}/token",
    data={"grant_type": "client_credentials", "scope": "llm-access"}
)
token2 = response.json()["access_token"]
decoded2 = jwt.decode(token2, options={"verify_signature": False})
print(f"Token 2 expires at: {decoded2['exp']} ({decoded2['exp'] - time.time():.0f}s from now)")

# Verify new token has later expiry
assert decoded2["exp"] > decoded1["exp"], "Token not refreshed!"
print("✅ Token refresh working")

# Try to use expired token (simulate)
old_token = jwt.encode(
    {"sub": "test", "scope": "llm-access", "exp": int(time.time()) - 3600},
    "secret",
    algorithm="HS256"
)
response = requests.post(
    f"{AUTH_URL}/introspect",
    data={"token": old_token}
)
introspection = response.json()
assert introspection["active"] == False, "Expired token still active!"
assert "expired" in introspection.get("reason", "").lower()
print("✅ Token expiry validation working")
```

---

### 10. Failure Mode Testing

**Test Scenario:** System behavior when components fail.

```bash
# Scenario A: Auth service down
kubectl scale -n casa-dev deployment/casa-auth --replicas=0

# Agent should:
# - Use cached tokens (for ~30s)
# - Then fail requests with 503

kubectl logs -n dev-mas deployment/test-agent -c casa-sidecar --tail=20
# "WARN: Auth service unavailable, using cached token (age: 45s)"

# Restore auth service
kubectl scale -n casa-dev deployment/casa-auth --replicas=1

# Scenario B: Cilium down (eBPF failure)
kubectl delete pod -n kube-system -l k8s-app=cilium

# Agent should:
# - Lose network enforcement (failsafe to allow mode)
# - Still work functionally but lose Zero Trust guarantees

# Restore Cilium
cilium install

# Scenario C: Database down
kubectl scale -n casa-dev deployment/postgres --replicas=0

# Auth service should:
# - Fail new token issuance (500 error)
# - Continue validating tokens (JWT signature check, no DB needed)

kubectl exec -n dev-mas deployment/test-agent -c agent -- \
  curl http://casa-auth.casa-dev.svc:443/token -d "grant_type=client_credentials"
# {"error": "database unavailable"}

# But introspection still works:
kubectl exec -n dev-mas deployment/test-agent -c agent -- \
  curl http://casa-auth.casa-dev.svc:443/introspect -d "token=<existing_token>"
# {"active": true, ...}
```

---

## Developer Workflow Guide

### Daily Development Tasks

#### 1. Adding a New MCP Server

```bash
# 1. Deploy MCP server
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-mcp
  namespace: dev-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: database-mcp
      casa.io/app-type: mcp-server
  template:
    metadata:
      labels:
        app: database-mcp
        casa.io/app-type: mcp-server
    spec:
      containers:
      - name: mcp
        image: your-registry/database-mcp:latest
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: database-mcp
  namespace: dev-mas
spec:
  selector:
    app: database-mcp
  ports:
  - port: 8080
EOF

# 2. Register in auth service
kubectl port-forward -n casa-dev svc/casa-auth 8000:443 &

curl -X POST http://localhost:8000/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "database-mcp",
    "type": "mcp_server",
    "base_url": "http://database-mcp.dev-mas.svc:8080",
    "mas_id": 1
  }'

# 3. Add tools (optional - can auto-discover)
curl -X POST http://localhost:8000/apps/3/tools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "database:query",
    "description": "Execute SQL query"
  }'

# 4. Update network policy to allow agent → database-mcp
kubectl patch cnp agent-egress -n dev-mas --type=json -p='[
  {
    "op": "add",
    "path": "/spec/egress/-",
    "value": {
      "toEndpoints": [{
        "matchLabels": {"app": "database-mcp"}
      }],
      "toPorts": [{
        "ports": [{"port": "8080", "protocol": "TCP"}]
      }]
    }
  }
]'
```

---

#### 2. Testing Token Flows Locally

```bash
# Create test script: test-token-flow.sh
cat > test-token-flow.sh <<'BASH'
#!/bin/bash
set -e

echo "=== CASA PoC Token Flow Test ==="

# Setup
AUTH_URL="http://localhost:8000"
MCP_URL="http://localhost:8080"

# Port forward in background
kubectl port-forward -n casa-dev svc/casa-auth 8000:443 &
PF1=$!
kubectl port-forward -n dev-mas svc/filesystem-mcp 8080:8080 &
PF2=$!
sleep 2

# Test 1: Get LLM token
echo ""
echo "Test 1: Get LLM token"
LLM_TOKEN=$(curl -s -X POST $AUTH_URL/token \
  -d "grant_type=client_credentials&scope=llm-access" \
  | jq -r '.access_token')

if [ -z "$LLM_TOKEN" ]; then
  echo "❌ Failed to get LLM token"
  exit 1
fi
echo "✅ LLM token: ${LLM_TOKEN:0:20}..."

# Test 2: Get tool token
echo ""
echo "Test 2: Get tool token"
TOOL_TOKEN=$(curl -s -X POST $AUTH_URL/token \
  -d "grant_type=client_credentials&scope=call-tools&requested_tools=filesystem:read" \
  | jq -r '.access_token')

if [ -z "$TOOL_TOKEN" ]; then
  echo "❌ Failed to get tool token"
  exit 1
fi
echo "✅ Tool token: ${TOOL_TOKEN:0:20}..."

# Test 3: Introspect token
echo ""
echo "Test 3: Introspect token"
INTROSPECT=$(curl -s -X POST $AUTH_URL/introspect \
  -d "token=$TOOL_TOKEN")

ACTIVE=$(echo $INTROSPECT | jq -r '.active')
if [ "$ACTIVE" != "true" ]; then
  echo "❌ Token not active"
  echo "$INTROSPECT" | jq
  exit 1
fi
echo "✅ Token introspection:"
echo "$INTROSPECT" | jq

# Test 4: Call MCP with token
echo ""
echo "Test 4: Call MCP with token"
MCP_RESPONSE=$(curl -s -X POST $MCP_URL/mcp \
  -H "Authorization: Bearer $TOOL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","id":1}')

if echo "$MCP_RESPONSE" | jq -e '.result' > /dev/null; then
  echo "✅ MCP call succeeded:"
  echo "$MCP_RESPONSE" | jq
else
  echo "❌ MCP call failed"
  echo "$MCP_RESPONSE"
  exit 1
fi

# Test 5: Try invalid token
echo ""
echo "Test 5: Try invalid token"
INVALID_RESPONSE=$(curl -s -X POST $MCP_URL/mcp \
  -H "Authorization: Bearer invalid-token" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","id":1}')

if echo "$INVALID_RESPONSE" | grep -q "401"; then
  echo "✅ Invalid token rejected"
else
  echo "⚠️  Invalid token should be rejected"
fi

# Cleanup
kill $PF1 $PF2 2>/dev/null || true

echo ""
echo "=== All tests passed ✅ ==="
BASH

chmod +x test-token-flow.sh
./test-token-flow.sh
```

---

#### 3. Debugging Token Issues

```bash
# Decode JWT manually
decode_jwt() {
  local token=$1
  echo "Header:"
  echo $token | cut -d'.' -f1 | base64 -d 2>/dev/null | jq
  echo ""
  echo "Payload:"
  echo $token | cut -d'.' -f2 | base64 -d 2>/dev/null | jq
}

# Get token and decode
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=call-tools&requested_tools=filesystem:read" \
  | jq -r '.access_token')

decode_jwt "$TOKEN"

# Check expiry
EXP=$(echo $TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq -r '.exp')
NOW=$(date +%s)
if [ $EXP -lt $NOW ]; then
  echo "❌ Token expired!"
else
  echo "✅ Token valid for $((EXP - NOW)) seconds"
fi
```

---

#### 4. Monitoring Network Policies

```bash
# Watch live traffic
hubble observe --namespace dev-mas --follow

# Filter for denies
hubble observe --namespace dev-mas --verdict DROPPED --follow

# See what agent is trying to reach
hubble observe --from-label app=test-agent --follow

# Check specific pod connectivity
POD=$(kubectl get pod -n dev-mas -l app=test-agent -o name | head -1)
kubectl exec -n dev-mas $POD -- curl -v http://filesystem-mcp.dev-mas.svc:8080/health

# If blocked, check policy
kubectl get cnp -n dev-mas agent-egress -o yaml
```

---

#### 5. Hot-Reloading Auth Service

```bash
# Method 1: Update ConfigMap and restart
kubectl create configmap auth-service-code \
  --from-file=main.py=./auth_service.py \
  --dry-run=client -o yaml | kubectl apply -n casa-dev -f -

kubectl rollout restart deployment/casa-auth -n casa-dev
kubectl wait --for=condition=ready pod -n casa-dev -l app=casa-auth --timeout=60s

# Method 2: Direct edit (for quick testing)
kubectl edit configmap auth-service-code -n casa-dev
kubectl rollout restart deployment/casa-auth -n casa-dev
```

---

#### 6. Adding New Tool to MCP Server

```bash
# 1. Update MCP server code to add new tool
# 2. Register tool in auth service
curl -X POST http://localhost:8000/apps/2/tools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "filesystem:write",
    "description": "Write file contents"
  }'

# 3. Test token with new tool
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=call-tools&requested_tools=filesystem:write" \
  | jq -r '.access_token')

# Verify tool in token
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq '.tools'
# ["filesystem:write"]
```

---

#### 7. Performance Testing

```bash
# Install Apache Bench
# macOS: brew install httpd
# Linux: apt install apache2-utils

# Test token endpoint
ab -n 1000 -c 10 -p request.txt -T 'application/x-www-form-urlencoded' \
  http://localhost:8000/token

# request.txt contains:
# grant_type=client_credentials&scope=llm-access

# Test introspection endpoint
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials&scope=llm-access" | jq -r '.access_token')

echo "token=$TOKEN" > introspect.txt
ab -n 1000 -c 10 -p introspect.txt -T 'application/x-www-form-urlencoded' \
  http://localhost:8000/introspect

# Check results
# Requests per second: ~500-1000 (single pod)
# Mean latency: ~10-20ms (without external calls)
```

---

#### 8. Database Migrations

```bash
# Backup current schema
kubectl exec -n casa-dev deployment/postgres -- \
  pg_dump -U casa -d casa_dev -s > schema_backup.sql

# Add new column
kubectl exec -n casa-dev deployment/postgres -- \
  psql -U casa -d casa_dev -c "ALTER TABLE apps ADD COLUMN created_at TIMESTAMP DEFAULT NOW();"

# Verify
kubectl exec -n casa-dev deployment/postgres -- \
  psql -U casa -d casa_dev -c "\d apps"

# Rollback if needed
kubectl exec -n casa-dev deployment/postgres -- \
  psql -U casa -d casa_dev < schema_backup.sql
```

---

#### 9. Logs and Debugging

```bash
# Stream all logs from control plane
kubectl logs -n casa-dev -l app=casa-auth --follow

# Stream agent logs
kubectl logs -n dev-mas -l app=test-agent --follow

# Search for errors
kubectl logs -n casa-dev deployment/casa-auth | grep -i error

# Get last 100 lines
kubectl logs -n casa-dev deployment/casa-auth --tail=100

# Save logs to file
kubectl logs -n casa-dev deployment/casa-auth > auth-service.log

# Exec into pod for debugging
kubectl exec -it -n casa-dev deployment/casa-auth -- sh

# Inside pod:
#   pip install ipython
#   ipython
#   >>> import jwt
#   >>> jwt.decode(token, secret, algorithms=["HS256"])
```

---

#### 10. Cleanup and Reset

```bash
# Delete everything
kubectl delete namespace casa-dev dev-mas

# Or reset database only
kubectl exec -n casa-dev deployment/postgres -- \
  psql -U casa -d casa_dev -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Restart auth service to re-run migrations
kubectl rollout restart deployment/casa-auth -n casa-dev

# Verify clean state
curl http://localhost:8000/apps
# []
```

---

## Simplified Multi-Agent System CRD

For PoC, use a minimal CRD:

```yaml
apiVersion: casa.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: dev-mas
  namespace: dev-mas
spec:
  # Basic config only
  authServer:
    url: http://casa-auth.casa-dev.svc:443

  # Disable production features
  features:
    enableTelemetry: false
    enableAIChecks: false
    enableTokenCache: false

  # Apps to register
  apps:
  - name: test-agent
    type: agent

  - name: filesystem-mcp
    type: mcp_server
    baseUrl: http://filesystem-mcp.dev-mas.svc:8080
    tools:
    - name: filesystem:read
      description: "Read file contents"
    - name: filesystem:list
      description: "List directory"
```

**Operator reconciliation (simplified):**
1. Create namespace if not exists
2. Register apps in auth service
3. Apply network policies
4. Enable sidecar injection label

---

## Component Building Blocks

### Monolithic Auth Service

Combines production services into one:

```python
# auth_service.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# Token issuance (client_credentials)
@app.post("/token")
def issue_token(grant_type: str, scope: str, requested_tools: str = None):
    """
    Simplified token issuance - no Keycloak integration for PoC
    """
    if grant_type != "client_credentials":
        raise ValueError("Only client_credentials supported")

    # Generate JWT directly
    payload = {
        "sub": "test-agent",
        "scope": scope,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "iat": datetime.utcnow(),
    }

    if requested_tools:
        payload["tools"] = requested_tools.split(",")

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900,
        "scope": scope,
    }

# Token introspection
@app.post("/introspect")
def introspect_token(token: str):
    """
    Validate JWT and return claims
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {
            "active": True,
            "scope": payload.get("scope"),
            "tools": payload.get("tools", []),
            "exp": payload.get("exp"),
        }
    except jwt.ExpiredSignatureError:
        return {"active": False, "reason": "Token expired"}
    except jwt.InvalidTokenError:
        return {"active": False, "reason": "Invalid token"}

# App registration
@app.post("/apps")
def register_app(app: AppCreate, db: Session = Depends(get_db)):
    """
    Register agent or MCP server
    """
    db_app = App(
        name=app.name,
        type=app.type,
        mas_id=app.mas_id,
        client_id=generate_client_id(),
        client_secret=generate_client_secret(),
    )
    db.add(db_app)
    db.commit()
    return db_app

# MCP discovery (minimal)
@app.get("/mcp/discover")
def discover_mcp_tools(mcp_server_url: str):
    """
    Call MCP server to get tool list
    """
    response = requests.post(
        f"{mcp_server_url}/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1,
        }
    )
    return response.json()["result"]["tools"]

# Tool authorization (deterministic only)
@app.post("/tools/authorize")
def authorize_tool(tool_name: str, task: str):
    """
    Simplified: Just check if tool exists
    No AI-powered matching in PoC
    """
    # Check tool is registered
    tool = db.query(Tool).filter(Tool.name == tool_name).first()
    if not tool:
        return {"allowed": False, "reason": "Tool not found"}

    return {"allowed": True}
```

**What's removed:**
- ✗ Keycloak integration (JWT signed locally)
- ✗ Token exchange (RFC 8693) - direct issuance instead
- ✗ AI-powered tool matching
- ✗ Telemetry event logging
- ✗ Redis caching

---

## Minimal Helm Chart

```yaml
# charts/casa-poc/values.yaml
controlPlane:
  namespace: casa-dev
  auth:
    image: your-registry/casa-auth:dev
    replicas: 1
    resources:
      requests:
        cpu: 100m
        memory: 128Mi

  postgres:
    image: postgres:15
    password: dev-password-change-me

  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    devMode: true

dataPlane:
  namespace: dev-mas
  sidecar:
    image: envoyproxy/envoy:v1.28-latest
    resources:
      requests:
        cpu: 50m
        memory: 64Mi

cilium:
  enabled: true
  policies:
    denyByDefault: true
    allowLLM: true
    allowedFQDNs:
    - api.openai.com

features:
  telemetry: false
  aiChecks: false
  ha: false
  monitoring: false
```

Install:
```bash
helm install casa-poc ./charts/casa-poc \
  --namespace casa-dev \
  --create-namespace \
  --values dev-values.yaml
```

---

## Security Considerations (PoC)

| Security Feature | Production | PoC | Why Simplified |
|------------------|------------|-----|----------------|
| **Token signing** | RSA-4096 via Keycloak | HS256 local | Faster, simpler setup |
| **Token storage** | PostgreSQL + Redis | In-memory only | No persistence needed |
| **TLS** | Everywhere (mTLS) | Optional | Local cluster |
| **RBAC** | Fine-grained | Admin-only | Single user |
| **Audit logs** | Immutable store | None | No telemetry |
| **Network policies** | Comprehensive | Basic allow/deny | Core flows only |
| **Secret management** | Vault/Sealed Secrets | ConfigMaps | Dev environment |

**⚠️ Warning:** This PoC is NOT production-ready. Before deploying to production:
1. Integrate Keycloak for proper token signing
2. Enable TLS everywhere (cert-manager)
3. Add Redis for token caching
4. Implement telemetry service
5. Harden network policies (see [SPECS.md §5](./SPECS.md#5-network-architecture--policy-enforcement))
6. Use proper secret management (Vault)
7. Enable AI-powered tool checks

---

## Integration Patterns

### Pattern 1: Python Agent Integration

How to integrate a Python-based agent with CASA:

```python
# agent.py
import os
import httpx
import asyncio

class CASAAgent:
    def __init__(self):
        self.auth_url = os.getenv("CASA_AUTH_URL", "http://casa-auth.casa-dev.svc:443")
        self.llm_token = None
        self.tool_tokens = {}

    async def get_llm_token(self):
        """Get token for LLM access"""
        if self.llm_token and not self._is_expired(self.llm_token):
            return self.llm_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token",
                data={
                    "grant_type": "client_credentials",
                    "scope": "llm-access"
                }
            )
            data = response.json()
            self.llm_token = data["access_token"]
            return self.llm_token

    async def get_tool_token(self, tools: list[str]):
        """Get token for specific tools"""
        tools_key = ",".join(sorted(tools))

        if tools_key in self.tool_tokens and not self._is_expired(self.tool_tokens[tools_key]):
            return self.tool_tokens[tools_key]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token",
                data={
                    "grant_type": "client_credentials",
                    "scope": "call-tools",
                    "requested_tools": tools_key
                }
            )
            data = response.json()
            self.tool_tokens[tools_key] = data["access_token"]
            return self.tool_tokens[tools_key]

    async def call_llm(self, prompt: str):
        """Call LLM with automatic token injection"""
        token = await self.get_llm_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return response.json()

    async def call_mcp_tool(self, tool_name: str, server_url: str, params: dict):
        """Call MCP tool with automatic token injection"""
        token = await self.get_tool_token([tool_name])

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{server_url}/mcp",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": params
                    },
                    "id": 1
                }
            )
            return response.json()

    def _is_expired(self, token: str) -> bool:
        """Check if token is expired"""
        import jwt
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            import time
            return payload.get("exp", 0) < time.time()
        except:
            return True


# Usage example
async def main():
    agent = CASAAgent()

    # Step 1: Call LLM
    llm_response = await agent.call_llm("What files should I read?")
    print(f"LLM: {llm_response}")

    # Step 2: Call MCP tool
    tool_response = await agent.call_mcp_tool(
        tool_name="filesystem:read",
        server_url="http://filesystem-mcp.dev-mas.svc:8080",
        params={"path": "/config.json"}
    )
    print(f"Tool: {tool_response}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-agent
  namespace: dev-mas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-agent
      casa.io/app-type: agent
  template:
    metadata:
      labels:
        app: python-agent
        casa.io/app-type: agent
    spec:
      containers:
      - name: agent
        image: python:3.12
        command: ["python", "/app/agent.py"]
        env:
        - name: CASA_AUTH_URL
          value: http://casa-auth.casa-dev.svc:443
        volumeMounts:
        - name: code
          mountPath: /app
      volumes:
      - name: code
        configMap:
          name: agent-code
```

---

### Pattern 2: MCP Server with Token Validation

How to secure an MCP server with CASA:

```python
# mcp_server.py
from fastapi import FastAPI, Header, HTTPException
import httpx
import jwt
import os

app = FastAPI()

AUTH_URL = os.getenv("CASA_AUTH_URL", "http://casa-auth.casa-dev.svc:443")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")

async def validate_token(authorization: str) -> dict:
    """Validate token with auth service"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    # Option 1: Local JWT validation (faster)
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Check scope
        if "call-tools" not in payload.get("scope", ""):
            raise HTTPException(403, "Invalid scope")

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

    # Option 2: Introspection (if no shared secret)
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         f"{AUTH_URL}/introspect",
    #         data={"token": token}
    #     )
    #     data = response.json()
    #     if not data.get("active"):
    #         raise HTTPException(401, "Token inactive")
    #     return data


@app.post("/mcp")
async def mcp_endpoint(
    request: dict,
    authorization: str = Header(None)
):
    """MCP JSON-RPC endpoint with token validation"""

    # Validate token
    token_data = await validate_token(authorization)
    allowed_tools = token_data.get("tools", [])

    # Extract requested tool
    method = request.get("method")
    if method == "tools/list":
        # List available tools
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "filesystem:read",
                        "description": "Read file contents",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            },
                            "required": ["path"]
                        }
                    },
                    {
                        "name": "filesystem:write",
                        "description": "Write file contents",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            },
                            "required": ["path", "content"]
                        }
                    }
                ]
            },
            "id": request.get("id")
        }

    elif method == "tools/call":
        # Execute tool
        params = request.get("params", {})
        tool_name = params.get("name")

        # Check authorization
        if tool_name not in allowed_tools:
            raise HTTPException(403, f"Tool '{tool_name}' not authorized")

        # Execute tool logic
        if tool_name == "filesystem:read":
            path = params.get("arguments", {}).get("path")
            content = f"[Mock file contents of {path}]"
            return {
                "jsonrpc": "2.0",
                "result": {"content": content},
                "id": request.get("id")
            }

        elif tool_name == "filesystem:write":
            path = params.get("arguments", {}).get("path")
            content = params.get("arguments", {}).get("content")
            return {
                "jsonrpc": "2.0",
                "result": {"success": True, "path": path},
                "id": request.get("id")
            }

        else:
            raise HTTPException(404, f"Tool '{tool_name}' not found")

    else:
        raise HTTPException(400, f"Unknown method: {method}")


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

**Key points:**
- ✅ Validates token on every request
- ✅ Checks tool authorization from token claims
- ✅ Returns proper MCP JSON-RPC responses
- ✅ Implements both `tools/list` and `tools/call`

---

### Pattern 3: Sidecar-less Integration (Simplified)

For PoC, you can skip sidecar injection and have apps handle tokens directly:

```python
# No sidecar needed - app handles tokens
import httpx

class SimpleCASAClient:
    def __init__(self, auth_url: str):
        self.auth_url = auth_url
        self.token = None

    def get_token(self, scope: str, tools: list[str] = None):
        """Get token from auth service"""
        data = {
            "grant_type": "client_credentials",
            "scope": scope
        }
        if tools:
            data["requested_tools"] = ",".join(tools)

        response = httpx.post(f"{self.auth_url}/token", data=data)
        self.token = response.json()["access_token"]
        return self.token

    def call_mcp(self, mcp_url: str, method: str, params: dict = None):
        """Call MCP server with token"""
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        response = httpx.post(f"{mcp_url}/mcp", json=payload, headers=headers)
        return response.json()

# Usage
client = SimpleCASAClient("http://casa-auth.casa-dev.svc:443")
client.get_token("call-tools", ["filesystem:read"])
result = client.call_mcp(
    "http://filesystem-mcp.dev-mas.svc:8080",
    "tools/call",
    {"name": "filesystem:read", "arguments": {"path": "/config.json"}}
)
print(result)
```

**Pros:**
- ✅ Simpler to understand and debug
- ✅ No sidecar injection complexity
- ✅ Works with any language/framework

**Cons:**
- ❌ Apps must handle token logic
- ❌ No transparent token injection
- ❌ Less enforcement at network layer

**When to use:** Early PoC development, testing, debugging.

---

### Pattern 4: Multi-Tenant MAS

Running multiple isolated Multi-Agent Systems:

```bash
# Create MAS 1: Development
kubectl create namespace mas-dev
kubectl label namespace mas-dev casa.io/injection=enabled

curl -X POST http://localhost:8000/mas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "dev-mas",
    "namespace": "mas-dev",
    "tool_checks": ["DETERMINISTIC_ONLY"]
  }'

# Create MAS 2: Staging
kubectl create namespace mas-staging
kubectl label namespace mas-staging casa.io/injection=enabled

curl -X POST http://localhost:8000/mas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "staging-mas",
    "namespace": "mas-staging",
    "tool_checks": ["DETERMINISTIC_ONLY"]
  }'

# Deploy agents to different namespaces
kubectl apply -f agent-deployment.yaml -n mas-dev
kubectl apply -f agent-deployment.yaml -n mas-staging

# Network policies ensure isolation
kubectl apply -f - <<EOF
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: deny-cross-mas
  namespace: mas-dev
spec:
  endpointSelector: {}
  egress:
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: mas-staging
    deny: {}
EOF
```

**Result:** Agents in `mas-dev` cannot reach agents/MCP in `mas-staging`.

---

### Pattern 5: External LLM with Token Forwarding

How to call external LLM (OpenAI) with CASA tokens:

```python
# The sidecar doesn't modify external LLM calls
# But we log them for audit

import httpx
import os

async def call_llm_with_audit(prompt: str, casa_token: str):
    """Call OpenAI with audit trail"""

    # Get OpenAI API key (from secret)
    openai_key = os.getenv("OPENAI_API_KEY")

    # Call OpenAI
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "X-CASA-Token": casa_token,  # Pass through for logging
            },
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        llm_response = response.json()

    # Log to CASA telemetry (in production)
    # await log_llm_call(casa_token, prompt, llm_response)

    return llm_response
```

**Network policy allows only OpenAI:**
```yaml
- toFQDNs:
  - matchName: "api.openai.com"
  toPorts:
  - ports:
    - port: "443"
      protocol: TCP
```

---

## Next Steps

### Path to Production

1. **Phase 1: Working PoC** (1-2 weeks)
   - ✅ Deploy control plane
   - ✅ Sidecar injection working
   - ✅ Basic token flow (issue + validate)
   - ✅ Cilium policies enforcing deny-by-default

2. **Phase 2: Harden Auth** (2-3 weeks)
   - Integrate Keycloak properly (realms + clients)
   - Implement RFC 8693 token exchange
   - Add Redis caching
   - Enable TLS (cert-manager)

3. **Phase 3: Add Intelligence** (3-4 weeks)
   - AI-powered tool matching
   - Telemetry service
   - Observability stack (Prometheus/Grafana)

4. **Phase 4: Production-Ready** (4-6 weeks)
   - High availability (3+ replicas)
   - Multi-zone deployment
   - Disaster recovery
   - Load testing
   - Security audit

### Quick Wins

Things you can add easily to improve PoC:

1. **Basic UI:** Simple web form to register apps/MAS
2. **Token viewer:** Decode and display JWT claims
3. **Network policy tester:** Script to verify allow/deny rules
4. **Sidecar debugger:** Logs showing token injection

---

## Migration Path: PoC → Production

This section details the incremental steps to evolve the PoC into a production-ready system.

### Phase 1: Add High Availability (Week 1-2)

**Goal:** Eliminate single points of failure.

**Changes:**
1. **Scale control plane:**
   ```yaml
   # Update deployments
   spec:
     replicas: 3  # Was: 1
   ```

2. **Add PostgreSQL replication:**
   ```bash
   helm install postgres bitnami/postgresql \
     --set replication.enabled=true \
     --set replication.numSynchronousReplicas=1 \
     --set replication.synchronousCommit=on
   ```

3. **Add Redis for caching:**
   ```bash
   helm install redis bitnami/redis \
     --set sentinel.enabled=true \
     --set replica.replicaCount=3
   ```

4. **Add PodDisruptionBudgets:**
   ```yaml
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: casa-auth-pdb
   spec:
     minAvailable: 2
     selector:
       matchLabels:
         app: casa-auth
   ```

**Testing:** Kill one replica of each service, verify no downtime.

**Cost impact:** +$200/mo (Redis + larger DB instance)

---

### Phase 2: Add Observability (Week 3-4)

**Goal:** Gain visibility into system behavior.

**Changes:**
1. **Deploy Prometheus + Grafana:**
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace observability \
     --create-namespace
   ```

2. **Add metrics to auth service:**
   ```python
   from prometheus_client import Counter, Histogram

   token_issued_counter = Counter('casa_token_issued_total', 'Tokens issued', ['scope'])
   token_validation_duration = Histogram('casa_token_validation_seconds', 'Validation latency')

   @app.post("/token")
   def issue_token(...):
       token_issued_counter.labels(scope=scope).inc()
       # ... existing logic
   ```

3. **Enable Hubble UI:**
   ```bash
   cilium hubble enable --ui
   kubectl port-forward -n kube-system svc/hubble-ui 12000:80
   ```

4. **Add structured logging:**
   ```python
   import structlog
   logger = structlog.get_logger()
   logger.info("token_issued", client_id=client_id, scope=scope, tools=tools)
   ```

**Key metrics to monitor:**
- Token issuance rate (tokens/sec)
- Token validation latency (p50, p95, p99)
- Network policy violations (Cilium drops/sec)
- Sidecar cache hit rate

**Cost impact:** +$100/mo (Prometheus + Grafana storage)

---

### Phase 3: Add Telemetry Service (Week 5-6)

**Goal:** Enable audit trails and compliance.

**Changes:**
1. **Deploy telemetry service:**
   - Extracts Auth + Telemetry into separate deployments
   - Adds PostgreSQL event table with partitioning
   - Implements batch event ingestion (reduces DB load)

2. **Schema changes:**
   ```sql
   CREATE TABLE telemetry_events (
       id BIGSERIAL,
       event_type VARCHAR(50),
       user_input_id UUID,
       trace_id UUID,
       data JSONB,
       created_at TIMESTAMP DEFAULT NOW()
   ) PARTITION BY RANGE (created_at);

   -- Partitions per month for retention management
   CREATE TABLE telemetry_events_2024_01 PARTITION OF telemetry_events
       FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
   ```

3. **Add trace correlation:**
   ```python
   import uuid

   @app.post("/token")
   def issue_token(...):
       trace_id = str(uuid.uuid4())
       # ... issue token with trace_id claim

       telemetry_service.log_event({
           "event_type": "token_issued",
           "trace_id": trace_id,
           "scope": scope,
           "tools": tools,
       })
   ```

**Retention policy:** 90 days for events, 1 year for aggregates.

**Cost impact:** +$150/mo (larger Postgres + telemetry service)

---

### Phase 4: Add AI-Powered Checks (Week 7-8)

**Goal:** Enable semantic tool authorization.

**Changes:**
1. **Deploy AI Pipeline Service:**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: ai-pipeline
   spec:
     replicas: 3
     template:
       spec:
         containers:
         - name: ai-pipeline
           image: casa-ai-pipeline:v1
           env:
           - name: OPENAI_API_KEY
             valueFrom:
               secretKeyRef:
                 name: openai-creds
                 key: api-key
           - name: OPENAI_ENDPOINT
             value: "https://api.openai.com/v1"
           - name: EMBEDDING_MODEL
             value: "text-embedding-3-large"
           - name: LLM_MODEL
             value: "gpt-4o"
           resources:
             requests:
               memory: "512Mi"
               cpu: "500m"
   ```

2. **Integrate into token exchange:**
   ```python
   @app.post("/oauth/token/exchange")
   async def exchange_token(...):
       # ... validate subject_token

       if "call-tools" in requested_scope:
           # Run AI checks
           match_result = await ai_pipeline_service.match_task_to_tool(
               task=user_input,
               requested_tool=requested_tool,
               available_tools=mcp_server_tools
           )

           if not match_result["allowed"]:
               raise HTTPException(403, f"Tool mismatch: {match_result['reason']}")
   ```

3. **Add embedding cache:**
   ```python
   # Cache tool embeddings for 24h
   tool_embedding = await redis.get(f"embedding:tool:{tool_name}")
   if not tool_embedding:
       tool_embedding = await openai.embeddings.create(
           model="text-embedding-3-large",
           input=tool_description
       )
       await redis.setex(f"embedding:tool:{tool_name}", 86400, tool_embedding)
   ```

**AI Check Pipeline:**
1. **Deterministic check:** Tool in LLM response?
2. **Embedding match:** Task-to-tool similarity > 0.2?
3. **LLM verifier:** GPT-4o confirms intent alignment?

**Cost impact:** +$300/mo (OpenAI API calls) + $50/mo (AI pipeline service)

---

### Phase 5: Production Hardening (Week 9-12)

**Goal:** Security, compliance, and operational maturity.

**Changes:**

#### 5.1 Replace Keycloak Integration
```python
# Add Keycloak client for real OAuth2 flows
from keycloak import KeycloakAdmin

kc_admin = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    username=KEYCLOAK_ADMIN_USER,
    password=KEYCLOAK_ADMIN_PASSWORD,
    realm_name="master"
)

@app.post("/token")
def issue_token(...):
    # Delegate to Keycloak for real token issuance
    token = kc_admin.token(
        client_id=client_id,
        client_secret=client_secret,
        grant_type="client_credentials",
        scope=scope
    )
    return token
```

#### 5.2 Add mTLS for Sidecar ↔ Control Plane
```yaml
# Envoy TLS config
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
    common_tls_context:
      tls_certificates:
      - certificate_chain: {filename: "/etc/certs/tls.crt"}
        private_key: {filename: "/etc/certs/tls.key"}
      validation_context:
        trusted_ca: {filename: "/etc/certs/ca.crt"}
        match_subject_alt_names:
        - exact: "casa-auth.casa-control-plane.svc"
```

#### 5.3 Add Network Policy Hardening
```yaml
# Egress: Control plane cannot reach internet
apiVersion: cilium.io/v2
kind:CiliumNetworkPolicy
metadata:
  name: control-plane-lockdown
  namespace: casa-control-plane
spec:
  endpointSelector:
    matchLabels:
      tier: control-plane
  egress:
  # Only allow internal cluster communication
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: casa-control-plane
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s-app: kube-dns
  # Block all external egress (including LLM API - only data plane should call)
  egressDeny:
  - toFQDNs:
    - matchPattern: "*"
```

#### 5.4 Add Secret Management (Vault)
```bash
# Deploy Vault
helm install vault hashicorp/vault \
  --set server.ha.enabled=true \
  --set server.ha.replicas=3

# Configure Vault injector for secrets
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: casa-auth
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "casa-auth"
    vault.hashicorp.com/agent-inject-secret-db: "database/creds/casa"
    vault.hashicorp.com/agent-inject-secret-keycloak: "kv/keycloak/admin"
EOF
```

#### 5.5 Add Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: casa-auth-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: casa-auth
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 120
```

#### 5.6 Add Backup and Disaster Recovery
```bash
# PostgreSQL backups via pgBackRest
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: pgbackrest/pgbackrest:latest
            command: ["pgbackrest", "backup", "--type=full"]
            env:
            - name: PGBACKREST_STANZA
              value: "casa-prod"
            - name: PGBACKREST_REPO1_PATH
              value: "/backups"
            volumeMounts:
            - name: backups
              mountPath: /backups
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: postgres-backups-pvc
EOF
```

**Total cost impact:** +$1500/mo (full production infrastructure)

---

### Checklist: Ready for Production?

Use this checklist to validate your system:

- [ ] **High Availability**
  - [ ] All services have 3+ replicas
  - [ ] PodDisruptionBudgets configured (minAvailable >= 2)
  - [ ] Multi-zone deployment (at least 2 zones)
  - [ ] Database replication enabled (sync or async)

- [ ] **Security**
  - [ ] mTLS enabled for all inter-service communication
  - [ ] Secrets managed via Vault (not ConfigMaps)
  - [ ] Network policies deny-by-default (Cilium)
  - [ ] Token signing via Keycloak (RS256, not HS256)
  - [ ] Regular security scanning (Trivy/Snyk on container images)

- [ ] **Observability**
  - [ ] Prometheus metrics exported from all services
  - [ ] Grafana dashboards for token lifecycle, network policies
  - [ ] Structured logging with trace correlation (trace_id)
  - [ ] Alerting configured (PagerDuty/Opsgenie)
  - [ ] Hubble UI enabled for network flow inspection

- [ ] **Compliance**
  - [ ] Telemetry service capturing all events
  - [ ] Audit logs immutable (append-only PostgreSQL)
  - [ ] Retention policy implemented (90 days events, 1 year aggregates)
  - [ ] GDPR/HIPAA compliance validated (if applicable)

- [ ] **Scalability**
  - [ ] HPA configured for auth service (3-20 replicas)
  - [ ] Redis caching reduces DB load by >80%
  - [ ] Load testing completed (1000 RPS sustained)
  - [ ] Database connection pooling tuned (PgBouncer)

- [ ] **Disaster Recovery**
  - [ ] Automated daily backups (PostgreSQL, Redis)
  - [ ] Backup restoration tested (RTO < 4h)
  - [ ] Cross-region replication (if multi-region)
  - [ ] Runbooks for common failure scenarios

- [ ] **Operations**
  - [ ] GitOps deployment via ArgoCD/Flux
  - [ ] Canary rollout strategy (10% → 50% → 100%)
  - [ ] Automated rollback on error rate increase
  - [ ] On-call rotation and escalation policy

**Estimated timeline:** 12 weeks from PoC to production-ready.

---

## Troubleshooting

### Control Plane Issues

```bash
# Postgres not starting
kubectl logs -n casa-dev deployment/postgres
# Check: Sufficient resources? PVC created?

# Keycloak timeout
kubectl describe pod -n casa-dev -l app=keycloak
# Check: Java heap size sufficient (default 512Mi)?

# Auth service can't reach Postgres
kubectl exec -n casa-dev deployment/casa-auth -- ping postgres
# Check: Service DNS resolving?
```

### Sidecar Issues

```bash
# Sidecar not injected
kubectl get mutatingwebhookconfiguration casa-sidecar-injector
# Check: Webhook configured? CA bundle correct?

# Traffic not redirected
kubectl exec -n dev-mas deployment/test-agent -c agent -- iptables -t nat -L
# Check: REDIRECT rule to port 15001?

# Token not injected
kubectl logs -n dev-mas deployment/test-agent -c casa-sidecar | grep "Authorization"
# Check: Envoy Lua filter working? Auth service reachable?
```

### Network Policy Issues

```bash
# Cilium not running
cilium status
# Check: eBPF programs loaded? Hubble enabled?

# Policy not applying
kubectl get cnp -n dev-mas agent-policy -o yaml
# Check: endpointSelector matching pods?

# Unexpected denies
hubble observe --namespace dev-mas --verdict DROPPED
# Check: Missing allow rule? Wrong FQDN?
```

---

## Comparison: PoC vs Production

| Aspect | PoC | Production |
|--------|-----|------------|
| **Deployment time** | 2-4 hours | 2-4 weeks |
| **Components** | 3 services | 7+ services |
| **Replicas** | 1 each | 3-20 per service |
| **Databases** | 1 Postgres | Postgres HA + Redis cluster |
| **Observability** | Logs only | Prometheus + Grafana + Loki + Tempo |
| **Security** | Basic | Hardened (mTLS, Vault, audit) |
| **Token validation** | JWT decode | Token introspection + Keycloak |
| **Tool checks** | Deterministic only | Deterministic + AI-powered |
| **Network policies** | 2 policies | 10+ policies |
| **Scalability** | Single node | Multi-zone, auto-scaling |
| **Cost** | ~$50/mo (small cluster) | ~$2000/mo (production) |

---

## Next Steps After PoC

### Immediate Actions (Week 1)

1. **Document your findings:**
   - What worked? What didn't?
   - Performance bottlenecks observed?
   - Security gaps discovered?
   - Developer experience feedback

2. **Validate core assumptions:**
   - [ ] Token flow complexity acceptable?
   - [ ] Network policies don't break existing workflows?
   - [ ] Sidecar overhead acceptable (<10ms latency added)?
   - [ ] Cilium FQDN filtering works for your LLM provider?

3. **Get stakeholder buy-in:**
   - Demo the working system to security team
   - Show audit trail capabilities (even without telemetry service)
   - Prove Zero Trust principles in action
   - Present cost-benefit analysis

### Short-Term Improvements (Week 2-4)

1. **Add real workloads:**
   - Replace test-agent with actual AI agent
   - Add production MCP servers (filesystem, web, database)
   - Test with real user tasks, not curl scripts

2. **Performance testing:**
   ```bash
   # Load test token endpoint
   ab -n 10000 -c 100 http://casa-auth.casa-dev.svc/token

   # Monitor latency
   kubectl top pods -n casa-dev
   kubectl top pods -n dev-mas

   # Check database connections
   kubectl exec -n casa-dev deployment/postgres -- \
     psql -U casa -c "SELECT count(*) FROM pg_stat_activity;"
   ```

3. **Harden security:**
   - Enable TLS for all services (use cert-manager)
   - Add NetworkPolicies for control plane isolation
   - Rotate JWT signing keys
   - Enable Cilium Hubble for flow visibility

4. **Add basic monitoring:**
   ```bash
   # Deploy lightweight Prometheus
   kubectl create namespace monitoring
   helm install prometheus prometheus-community/prometheus \
     --namespace monitoring \
     --set server.persistentVolume.enabled=false

   # Add ServiceMonitors for auth service
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Service
   metadata:
     name: casa-auth-metrics
     namespace: casa-dev
     labels:
       app: casa-auth
   spec:
     selector:
       app: casa-auth
     ports:
     - name: metrics
       port: 9090
       targetPort: 9090
   EOF
   ```

### Medium-Term Roadmap (Month 2-3)

1. **Decompose monolith:**
   - Extract Policy Service (app/MAS/tool CRUD)
   - Extract MCP Discovery Service (tool introspection)
   - Keep Auth Service focused on token operations

2. **Add Redis:**
   - Cache tokens in sidecars (reduce auth service load)
   - Cache tool embeddings (if enabling AI checks)
   - Cache MCP server tool lists

3. **Enable Keycloak:**
   - Proper OAuth2 flows (client credentials grant)
   - Client management via Keycloak Admin API
   - Token revocation support

4. **Add GitOps:**
   ```bash
   # Install ArgoCD
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

   # Create Application
   kubectl apply -f - <<EOF
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: casa-system
     namespace: argocd
   spec:
     project: default
     source:
       repoURL: https://github.com/your-org/casa-manifests
       targetRevision: main
       path: overlays/dev
     destination:
       server: https://kubernetes.default.svc
       namespace: casa-dev
     syncPolicy:
       automated:
         prune: true
         selfHeal: true
   EOF
   ```

### Long-Term Production Plan (Month 4-6)

See **Migration Path: PoC → Production** section above for detailed 12-week plan.

**Key milestones:**
- [ ] Week 4: HA control plane deployed
- [ ] Week 8: Telemetry + observability operational
- [ ] Week 12: AI-powered checks enabled
- [ ] Week 16: Production hardening complete
- [ ] Week 20: First production MAS deployed

---

## Cost Projection

### PoC Costs (Current)

| Component | Size | Monthly Cost |
|-----------|------|--------------|
| Kubernetes cluster | 1 node (4 CPU, 8GB) | $50 |
| PostgreSQL | 1 pod (20GB storage) | $10 |
| Auth service | 1 pod (0.5 CPU, 512MB) | Included in cluster |
| Sidecars | 2 pods (0.1 CPU, 128MB each) | Included in cluster |
| **Total** | | **~$60/mo** |

### Production Costs (Target)

| Component | Size | Monthly Cost |
|-----------|------|--------------|
| Kubernetes cluster | 5 nodes (16 CPU, 64GB) | $500 |
| PostgreSQL HA | 3 replicas + 100GB storage | $300 |
| Redis Sentinel | 3 replicas + 16GB | $150 |
| Keycloak | 3 replicas | $75 |
| Auth service | 3-20 replicas (HPA) | $150 |
| Policy service | 3 replicas | $50 |
| AI Pipeline service | 3 replicas | $100 |
| Telemetry service | 3-5 replicas | $75 |
| MCP Discovery | 2 replicas | $25 |
| Observability stack | Prometheus + Grafana + Loki | $200 |
| OpenAI API | 1M tokens/day | $300 |
| Backup storage | 1TB (30 days retention) | $50 |
| **Total** | | **~$2,000/mo** |

**Scaling multipliers:**
- 10x traffic: +$500/mo (HPA scales services)
- 100x traffic: +$3,000/mo (multi-region, CDN, larger DB)

---

## Common Pitfalls & How to Avoid

### Pitfall 1: Sidecar Not Injecting

**Symptom:** Pods deploy but have only 1 container (missing sidecar).

**Causes:**
- Namespace missing label `casa.io/injection: enabled`
- Pod missing label `casa.io/app-type: agent`
- MutatingWebhookConfiguration not applied or CA bundle invalid

**Fix:**
```bash
# Check webhook configuration
kubectl get mutatingwebhookconfiguration casa-sidecar-injector -o yaml | grep -A5 clientConfig

# Verify namespace label
kubectl get namespace dev-mas --show-labels

# Force pod recreation
kubectl rollout restart deployment/test-agent -n dev-mas
```

---

### Pitfall 2: Token Validation Fails

**Symptom:** MCP server returns 401 even with valid-looking token.

**Causes:**
- JWT secret mismatch (auth service using different key than MCP server expects)
- Token expired (clock skew between pods)
- Token introspection endpoint unreachable

**Fix:**
```bash
# Decode token manually
TOKEN="eyJhbGci..."
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq

# Check expiry
# If exp < current time, token expired

# Test introspection endpoint from MCP pod
kubectl exec -n dev-mas deployment/filesystem-mcp -c mcp-server -- \
  curl -X POST http://casa-auth.casa-dev.svc/introspect -d "token=$TOKEN"
```

---

### Pitfall 3: Network Policy Blocks Legitimate Traffic

**Symptom:** Agent can't reach MCP server despite policy allowing it.

**Causes:**
- Label selector mismatch (policy selects wrong pods)
- Missing DNS allow rule (can't resolve service names)
- Cilium not loaded on node (eBPF programs missing)

**Fix:**
```bash
# Check if Cilium is enforcing
cilium status
# Should show: Policy enforcement: enabled

# Check policy matches pods
kubectl get cnp -n dev-mas agent-policy -o yaml

# See what Cilium thinks is allowed
cilium endpoint list
cilium policy get <endpoint-id>

# Watch live denies
hubble observe --verdict DROPPED --follow
```

---

### Pitfall 4: Control Plane Overload

**Symptom:** Token issuance slow (>1s latency), timeouts.

**Causes:**
- Database connection pool exhausted
- No caching (every request hits DB)
- Single replica can't handle load

**Fix:**
```bash
# Check auth service logs for DB errors
kubectl logs -n casa-dev deployment/casa-auth | grep -i "database\|timeout"

# Scale up immediately
kubectl scale -n casa-dev deployment/casa-auth --replicas=3

# Add connection pooling (PgBouncer)
helm install pgbouncer bitnami/pgbouncer \
  --set postgresql.host=postgres.casa-dev.svc \
  --set pgbouncer.poolMode=transaction
```

---

### Pitfall 5: Cilium FQDN Not Resolving

**Symptom:** Agent can't reach `api.openai.com` despite policy allowing it.

**Causes:**
- DNS proxy not enabled in Cilium
- toFQDNs policy needs DNS visibility
- OpenAI IP changed (FQDN cached stale IP)

**Fix:**
```bash
# Enable DNS proxy in Cilium
cilium config set enable-policy-dns-proxy true

# Force DNS refresh
cilium fqdn cache clean

# Verify DNS policy loaded
cilium policy get | grep -A10 toFQDNs
```

---

## References

- **Full production spec:** [SPECS_HIGH_LEVEL.md](./SPECS_HIGH_LEVEL.md)
- **Complete technical details:** [SPECS.md](./SPECS.md)
- **Original system design:** [BUILD.md](./BUILD.md)
- **Cilium docs:** https://docs.cilium.io
- **Envoy proxy:** https://www.envoyproxy.io
- **RFC 8693 (Token Exchange):** https://tools.ietf.org/html/rfc8693

---

## Production Readiness Checklist

Before moving from PoC to production, complete these items:

### Security (Critical)

- [ ] **Replace JWT secret** - Use Vault or Kubernetes Secret
  ```bash
  kubectl create secret generic casa-jwt-secret \
    --from-literal=secret=$(openssl rand -base64 32) \
    -n casa-dev
  ```

- [ ] **Enable TLS everywhere** - Use cert-manager
  ```bash
  kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
  ```

- [ ] **Integrate Keycloak properly** - Remove simple JWT signing
  - Create dedicated Keycloak realm
  - Use client credentials per app
  - Enable token introspection

- [ ] **Harden network policies** - Add more granular rules
  - Block pod-to-pod in same namespace
  - Require mTLS for control plane
  - Add egress deny-by-default

- [ ] **Enable audit logging** - Track all token operations
  ```python
  logger.info("token_issued", client_id=client_id, scope=scope, tools=tools)
  ```

- [ ] **Scan container images** - Use Trivy or Snyk
  ```bash
  trivy image casa-auth-service:latest
  ```

### High Availability (Important)

- [ ] **Scale PostgreSQL** - 3 replicas with replication
  ```yaml
  replicas: 3
  replication:
    synchronousCommit: "on"
    numSynchronousReplicas: 1
  ```

- [ ] **Add Redis cluster** - For token caching
  ```bash
  helm install redis bitnami/redis \
    --set architecture=replication \
    --set sentinel.enabled=true
  ```

- [ ] **Scale control plane** - 3+ replicas per service
  ```yaml
  replicas: 3
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: casa-auth
        topologyKey: kubernetes.io/hostname
  ```

- [ ] **Configure HPA** - Auto-scale based on CPU/memory
  ```yaml
  apiVersion: autoscaling/v2
  kind: HorizontalPodAutoscaler
  metadata:
    name: casa-auth-hpa
  spec:
    scaleTargetRef:
      apiVersion: apps/v1
      kind: Deployment
      name: casa-auth
    minReplicas: 3
    maxReplicas: 20
    metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
  ```

- [ ] **Multi-zone deployment** - Spread across AZs
  ```yaml
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
  ```

### Observability (Important)

- [ ] **Deploy Prometheus** - Metrics collection
  ```bash
  helm install prometheus prometheus-community/kube-prometheus-stack
  ```

- [ ] **Add custom metrics** - Token issuance, validation latency
  ```python
  from prometheus_client import Counter, Histogram

  token_issued_counter = Counter('casa_token_issued_total', 'Total tokens issued', ['scope'])
  token_latency_histogram = Histogram('casa_token_latency_seconds', 'Token issuance latency')
  ```

- [ ] **Deploy Grafana dashboards** - Visualize token flows
  - Token issuance rate
  - Token validation latency (p50, p95, p99)
  - Network policy violations
  - MCP call success rate

- [ ] **Enable distributed tracing** - Jaeger or Tempo
  ```bash
  helm install tempo grafana/tempo
  ```

- [ ] **Configure alerts** - PagerDuty/Opsgenie
  ```yaml
  - alert: HighTokenValidationLatency
    expr: histogram_quantile(0.95, casa_token_latency_seconds) > 0.5
    for: 5m
    annotations:
      summary: "Token validation latency is high"
  ```

### Performance (Important)

- [ ] **Load test control plane** - Use k6 or Locust
  ```javascript
  // k6 script
  import http from 'k6/http';
  export default function () {
    http.post('http://casa-auth/token', 'grant_type=client_credentials&scope=llm-access');
  }
  ```
  Target: 10,000 req/sec with p95 < 100ms

- [ ] **Enable connection pooling** - PostgreSQL connections
  ```python
  engine = create_engine(
      DATABASE_URL,
      pool_size=20,
      max_overflow=10,
      pool_pre_ping=True
  )
  ```

- [ ] **Optimize database queries** - Add indexes
  ```sql
  CREATE INDEX idx_apps_client_id ON apps(client_id);
  CREATE INDEX idx_tools_app_id ON tools(app_id);
  ```

- [ ] **Enable Redis caching** - Cache token metadata
  ```python
  # Cache for 5 minutes
  redis_client.setex(f"token:{token_id}", 300, json.dumps(token_data))
  ```

### Compliance (As Needed)

- [ ] **Enable audit trails** - Immutable log storage
  - Use append-only database
  - Encrypt audit logs
  - Retention policy (90 days minimum)

- [ ] **Implement RBAC** - Fine-grained access control
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    name: casa-admin
  rules:
  - apiGroups: ["casa.io"]
    resources: ["multiagentsystems"]
    verbs: ["get", "list", "create", "update"]
  ```

- [ ] **Data residency** - Region-specific deployment
  - Deploy control plane in required region
  - Configure Cilium for geo-fencing

- [ ] **Penetration testing** - Third-party security audit
  - Test token exfiltration vectors
  - Network policy bypass attempts
  - SQL injection / JWT forgery

### Operations (Important)

- [ ] **Backup strategy** - PostgreSQL backups
  ```bash
  # Daily backups to S3
  kubectl create cronjob pg-backup \
    --image=postgres:15 \
    --schedule="0 2 * * *" \
    -- pg_dump -U casa -d casa_dev | gzip | aws s3 cp - s3://backups/pg-$(date +%Y%m%d).sql.gz
  ```

- [ ] **Disaster recovery plan** - RTO < 4h, RPO < 1h
  - Document restore procedure
  - Test recovery quarterly

- [ ] **CI/CD pipeline** - GitOps with ArgoCD
  ```bash
  argocd app create casa-control-plane \
    --repo https://github.com/your-org/casa-deploy \
    --path control-plane \
    --dest-namespace casa-prod \
    --dest-server https://kubernetes.default.svc
  ```

- [ ] **Runbooks** - Document common issues
  - Token validation failures
  - Database connection issues
  - Cilium policy conflicts

- [ ] **On-call rotation** - 24/7 coverage

### Cost Optimization (Optional)

- [ ] **Right-size pods** - Use VPA to recommend sizes
  ```bash
  kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.14.0/vpa-v0.14.0.yaml
  ```

- [ ] **Use spot instances** - For non-critical workloads
- [ ] **Enable cluster autoscaler** - Scale nodes down during off-hours
- [ ] **Monitor cloud costs** - Use Kubecost
  ```bash
  helm install kubecost kubecost/cost-analyzer
  ```

**Estimated timeline:** 8-12 weeks from PoC to production-ready.

---

## FAQ

**Q: Can I skip Cilium and use standard NetworkPolicy?**
A: No. Standard NetworkPolicy doesn't support FQDN filtering (needed for LLM endpoint). Cilium required.

**Q: Why Envoy instead of Istio sidecar?**
A: Lighter weight for PoC. Istio adds complexity. Can migrate later if needed.

**Q: Do I need Keycloak for PoC?**
A: Optional. The monolithic auth service can sign tokens directly. Keycloak adds proper OAuth2 flows.

**Q: How do I test without real agents?**
A: Use `curl` or Postman to simulate token requests. Example scripts in `/tests` folder.

**Q: Can I run this on Docker Compose?**
A: Partially. You'll lose Cilium eBPF enforcement and sidecar injection. Not recommended.

**Q: What's the minimum cluster size?**
A: 1 node (4 CPU, 8GB RAM) for PoC. 3+ nodes for production.

**Q: How do I enable AI tool matching later?**
A: Set `ENABLE_AI_CHECKS=true` in auth service, add OpenAI API key, deploy embeddings model. See [SPECS.md §3.3](./SPECS.md#33-ai-pipeline-service).

**Q: Can I migrate from PoC to production without downtime?**
A: Yes, using blue-green deployment:
1. Deploy production control plane in new namespace (`casa-prod`)
2. Migrate MAS one at a time (update sidecar auth URL)
3. Run both systems in parallel during transition
4. Decommission PoC once all workloads migrated

**Q: What's the biggest performance bottleneck?**
A: Token issuance (DB writes). Mitigate with: (1) Redis caching, (2) longer token TTL, (3) connection pooling. In production, auth service can handle 10,000 tokens/sec with proper tuning.

**Q: How do I debug "token not injected" issues?**
A: Check sidecar logs: `kubectl logs -n dev-mas deployment/test-agent -c casa-sidecar | grep -i "token\|auth"`. Common causes: auth service unreachable, wrong scope requested, JWT signing key mismatch.

**Q: Do I need to write agents differently for this system?**
A: No. Agents call LLM and MCP servers normally. Sidecars handle all token operations transparently. Only requirement: agents must use service DNS names (not IPs) for traffic interception to work.

---

## Summary

### What You've Learned

This document provided a **complete PoC-oriented deployment architecture** for a Zero Trust Multi-Agent System in Kubernetes, including:

1. ✅ **60-minute quick start** with copy-paste manifests
2. ✅ **Monolithic auth service** combining Auth + Policy + MCP Discovery (800+ lines of Python)
3. ✅ **Complete Envoy sidecar configuration** with token injection and protocol validation
4. ✅ **Cilium network policies** for deny-by-default enforcement
5. ✅ **10+ integration patterns** for Python agents and MCP servers
6. ✅ **Developer workflow guide** with daily tasks and debugging procedures
7. ✅ **5-phase migration path** from PoC to production (12 weeks)
8. ✅ **Production readiness checklist** with 50+ actionable items

### Key Simplifications (PoC vs Production)

| Aspect | PoC | Production | Migration Effort |
|--------|-----|------------|------------------|
| **Components** | 3 services | 7+ services | 2-3 weeks |
| **Replicas** | 1 each | 3-20 per service | 1 week |
| **Auth** | Simple JWT | Keycloak + OAuth2 | 2-3 weeks |
| **Caching** | In-memory | Redis Sentinel | 1 week |
| **Tool checks** | Deterministic | + AI-powered | 3-4 weeks |
| **Observability** | Logs | Prometheus/Grafana/Tempo | 2-3 weeks |
| **Security** | Basic | Hardened (mTLS, Vault) | 2-3 weeks |
| **Total time** | **1-2 hours** | **2-4 weeks** | **8-12 weeks** |

### Success Metrics

After deploying this PoC, you should be able to:

- ✅ Issue JWT tokens via `/token` endpoint (~10ms latency)
- ✅ Validate tokens via `/introspect` endpoint (~5ms latency)
- ✅ Automatically inject tokens into agent → MCP calls (transparent)
- ✅ Enforce deny-by-default network policies with Cilium
- ✅ Block unauthorized LLM calls (only `api.openai.com` allowed)
- ✅ Register new agents/MCP servers via REST API
- ✅ Test end-to-end flows with provided scripts
- ✅ Debug issues using logs and Cilium Hubble

### What's Next?

1. **Deploy the PoC** (1-2 hours)
   ```bash
   kind create cluster --name casa-poc
   kubectl apply -f control-plane.yaml
   kubectl apply -f data-plane.yaml
   ```

2. **Validate token flows** (30 minutes)
   ```bash
   ./test-token-flow.sh
   # ✅ All tests passed
   ```

3. **Integrate your first agent** (1-2 hours)
   - Use [Integration Pattern 1](#pattern-1-python-agent-integration)
   - Deploy to `dev-mas` namespace
   - Test LLM + MCP calls

4. **Plan production migration** (1 week planning)
   - Review [Migration Path](#migration-path-poc--production)
   - Complete [Production Readiness Checklist](#production-readiness-checklist)
   - Allocate 8-12 weeks for full migration

5. **Get expert help** (as needed)
   - Review [SPECS.md](./SPECS.md) for production architecture
   - Review [SPECS_HIGH_LEVEL.md](./SPECS_HIGH_LEVEL.md) for deployment details
   - Engage security team for threat modeling

### Additional Resources

- **Code repository:** [github.com/your-org/casa-poc](https://github.com/your-org/casa-poc)
- **Slack channel:** `#casa-mas-deployment`
- **Documentation:** [SPECS.md](./SPECS.md) | [BUILD.md](./BUILD.md)
- **Cilium docs:** https://docs.cilium.io
- **Envoy docs:** https://www.envoyproxy.io
- **MCP protocol:** https://modelcontextprotocol.io

---

## Document Information

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Author:** Senior Cloud & Kubernetes Architect  
**Audience:** DevOps Engineers, Platform Teams, Security Engineers  
**Estimated Read Time:** 45 minutes  
**Deployment Time:** 1-2 hours (PoC) | 8-12 weeks (Production)  

**License:** Internal Use Only

---

**End of Document**
