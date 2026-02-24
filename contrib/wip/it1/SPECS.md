# Zero Trust Multi-Agent System (ZTA-MAS) - Kubernetes Deployment Specification

## Executive Summary

This document defines a production-ready Kubernetes architecture for deploying a Zero Trust Authorization System for Multi-Agent Systems (MAS). The design transforms a monolithic authorization server into a cloud-native, sidecar-based architecture with eBPF-powered network enforcement.

**Key Architectural Decisions:**
- **Sidecar-per-workload**: Every MCP server, User App, and Agent gets a Zero Trust sidecar proxy
- **eBPF L3/L4 enforcement**: Cilium enforces deny-by-default networking with identity-aware policies
- **Control plane separation**: ZTA control plane manages token issuance, validation, and policy distribution
- **Protocol restrictions**: Only MCP (internal) and A2A (agent-to-agent) protocols allowed internally; single OpenAI-compatible LLM endpoint externally
- **Token-aware enforcement**: eBPF captures and validates JWT tokens at network layer where feasible

**Design Philosophy:**
- **Defense in depth**: Multiple enforcement layers (eBPF, sidecar, application)
- **Zero Trust by default**: Deny all, allow explicitly
- **Observable by design**: Every flow, token, and decision is logged
- **Operationally simple**: Standard Kubernetes patterns (Helm, CRDs, Operators)

---

## Table of Contents

1. [Requirements from BUILD.md](#1-requirements-from-buildmd)
2. [Architecture Overview](#2-architecture-overview)
3. [Component Decomposition](#3-component-decomposition)
4. [Sidecar vs eBPF Responsibility Model](#4-sidecar-vs-ebpf-responsibility-model)
5. [Network Architecture & Policy Enforcement](#5-network-architecture--policy-enforcement)
6. [Deployment Architecture](#6-deployment-architecture)
7. [Packaging Strategy](#7-packaging-strategy)
8. [Security & Threat Model](#8-security--threat-model)
9. [Operational Model](#9-operational-model)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Requirements from BUILD.md

### 1.1 Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | OAuth2-compliant token issuance (client credentials, token exchange RFC 8693) | BUILD.md §2.1 |
| FR-2 | Dynamic tool authorization using deterministic + AI-powered matching | BUILD.md §2.1 |
| FR-3 | Multi-Agent System (MAS) lifecycle management with per-system policies | BUILD.md §2.1 |
| FR-4 | MCP server discovery and tool introspection | BUILD.md §2.1 |
| FR-5 | Real-time telemetry collection (token events, LLM calls, tool invocations) | BUILD.md §2.1 |
| FR-6 | Token introspection and validation for MCP servers | BUILD.md §2.1 |
| FR-7 | LLM call tracing and user input correlation | BUILD.md §2.1 |
| FR-8 | Tool check pipeline (DeterministicToolSelected, LLMSelectedTools, AIToolIntent) | BUILD.md §6 |
| FR-9 | Task-to-tool matching (embeddings, LLM verifier, hybrid) | BUILD.md §7 |
| FR-10 | Administrative UI for apps, MAS, and system monitoring | BUILD.md §2.3 |

### 1.2 Non-Functional Requirements

| ID | Requirement | Constraint |
|----|-------------|------------|
| NFR-1 | All agent↔MCP communication via MCP protocol only | TASK CONSTRAINT |
| NFR-2 | Agent↔Agent communication via A2A protocol only | TASK CONSTRAINT |
| NFR-3 | Single external LLM endpoint (OpenAI-compatible API) | TASK CONSTRAINT |
| NFR-4 | Deny-by-default network policy | TASK CONSTRAINT |
| NFR-5 | Mandatory sidecars for all MAS components | TASK CONSTRAINT |
| NFR-6 | eBPF-based L3/L4 enforcement via Cilium | TASK CONSTRAINT |
| NFR-7 | Token capture and validation at network layer | TASK CONSTRAINT |
| NFR-8 | High availability (no single point of failure) | Production requirement |
| NFR-9 | Auditability (all decisions logged) | BUILD.md §2.1 |
| NFR-10 | Kubernetes-native packaging (Helm/Operator) | TASK CONSTRAINT |

### 1.3 Security Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| SR-1 | Token exfiltration prevention | Protect user credentials from compromised agents |
| SR-2 | LLM misuse prevention | Prevent agents from bypassing tool checks via direct LLM access |
| SR-3 | Lateral movement prevention | Compromised pod cannot reach other workloads |
| SR-4 | Tool intent validation | AI-powered check that requested tools match user's task |
| SR-5 | Audit trail immutability | Telemetry events cannot be deleted or modified |

---

## 2. Architecture Overview

### 2.1 High-Level Component Diagram

```mermaid
graph TB
    subgraph "Control Plane Namespace"
        ZTA[ZTA Control Plane<br/>StatefulSet]
        KC[Keycloak IdP<br/>StatefulSet]
        PG[(PostgreSQL<br/>StatefulSet)]
        UI[ZTA Explorer UI<br/>Deployment]

        ZTA --> KC
        ZTA --> PG
        UI --> ZTA
    end

    subgraph "MAS Namespace: production-mas"
        subgraph "User App Pod"
            UA[User App<br/>Container]
            UAS[ZTA Sidecar<br/>Proxy]
            UA -.-> UAS
        end

        subgraph "Agent Pod"
            AG[Agent<br/>Container]
            AGS[ZTA Sidecar<br/>Proxy]
            AG -.-> AGS
        end

        subgraph "MCP Server Pod"
            MCP[MCP Server<br/>Container]
            MCPS[ZTA Sidecar<br/>Proxy]
            MCP -.-> MCPS
        end

        UAS -->|MCP Protocol| MCPS
        AGS -->|A2A Protocol| AGS
        AGS -->|MCP Protocol| MCPS
    end

    subgraph "External"
        LLM[OpenAI-Compatible<br/>LLM Endpoint]
    end

    subgraph "Cilium eBPF Layer"
        EBPF[Network Policy Enforcement<br/>+ Token Validation<br/>+ Flow Logging]
    end

    UAS -.->|Token Request| ZTA
    AGS -.->|Token Exchange| ZTA
    MCPS -.->|Token Introspection| ZTA

    AGS -->|Allowed Egress| LLM

    EBPF -.->|Enforces All Traffic| UA
    EBPF -.->|Enforces All Traffic| AG
    EBPF -.->|Enforces All Traffic| MCP
    EBPF -.->|Logs to| ZTA

    style EBPF fill:#ff6b6b
    style ZTA fill:#4ecdc4
    style KC fill:#ffe66d
    style LLM fill:#95e1d3
```

### 2.2 Trust Boundary Diagram

```mermaid
graph LR
    subgraph "Untrusted Zone"
        U[User Input]
        LLM[External LLM]
    end

    subgraph "Trust Boundary 1: Ingress"
        ING[Ingress Controller]
        UAS[User App Sidecar]
    end

    subgraph "Trust Boundary 2: MAS Workloads"
        UA[User App]
        AG[Agent]
        AGS[Agent Sidecar]
        MCP[MCP Server]
        MCPS[MCP Sidecar]
    end

    subgraph "Trust Boundary 3: Control Plane"
        ZTA[ZTA Server]
        KC[Keycloak]
        PG[(Database)]
    end

    U -->|HTTPS| ING
    ING -->|TLS| UAS
    UAS -.->|AuthN/Z| ZTA
    UA -->|Localhost| UAS

    AGS -->|TLS + Token| LLM
    AGS -.->|Token Exchange| ZTA

    AG -->|Localhost| AGS
    MCP -->|Localhost| MCPS

    MCPS -.->|Token Introspect| ZTA
    ZTA --> KC
    ZTA --> PG

    style U fill:#ff6b6b
    style LLM fill:#ff6b6b
    style ZTA fill:#95e1d3
    style KC fill:#95e1d3
    style PG fill:#95e1d3
```

### 2.3 Data Flow Sequence: Token Acquisition to Tool Execution

```mermaid
sequenceDiagram
    participant User
    participant UserApp
    participant UASidecar as UserApp Sidecar
    participant eBPF as Cilium eBPF
    participant ZTA as ZTA Control Plane
    participant Agent
    participant AgentSidecar as Agent Sidecar
    participant LLM as External LLM
    participant MCPSidecar as MCP Sidecar
    participant MCP as MCP Server

    User->>UserApp: Submit task/prompt
    UserApp->>UASidecar: Request token (client_credentials)
    UASidecar->>eBPF: Egress to ZTA
    eBPF->>eBPF: Check CiliumNetworkPolicy (allow ZTA)
    eBPF->>ZTA: Forward request
    ZTA->>ZTA: Store user input, generate token
    ZTA-->>UASidecar: Return token (T1) with user_input_id

    UserApp->>Agent: Invoke agent with T1
    Agent->>AgentSidecar: Request LLM token exchange (T1 → T2)
    AgentSidecar->>eBPF: Egress to ZTA
    eBPF->>ZTA: Forward exchange request
    ZTA->>ZTA: Validate T1, issue LLM-scoped token (T2)
    ZTA-->>AgentSidecar: Return T2 (scope: llm-access)

    Agent->>AgentSidecar: Call LLM with T2
    AgentSidecar->>eBPF: Egress to LLM
    eBPF->>eBPF: Extract JWT from header<br/>Validate scope=llm-access
    eBPF->>LLM: Forward if valid (deny otherwise)
    LLM-->>AgentSidecar: LLM response (tool selections)
    AgentSidecar->>ZTA: Log LLM trace (tools selected)

    Agent->>AgentSidecar: Request MCP token exchange (T1 → T3)
    AgentSidecar->>ZTA: Exchange for tool "filesystem:read"
    ZTA->>ZTA: Run tool checks:<br/>1. Tool in LLM selection?<br/>2. Intent matches user task?<br/>3. Embeddings match?
    ZTA-->>AgentSidecar: Return T3 (scope: call-tools, tools=[filesystem:read])

    Agent->>AgentSidecar: Call MCP tool with T3
    AgentSidecar->>eBPF: Egress to MCP
    eBPF->>eBPF: Extract JWT, validate scope=call-tools
    eBPF->>MCPSidecar: Forward (protocol=MCP only)
    MCPSidecar->>MCPSidecar: Extract token from MCP auth header
    MCPSidecar->>ZTA: Introspect token T3
    ZTA-->>MCPSidecar: Token valid, tools=[filesystem:read]
    MCPSidecar->>MCP: Forward MCP request
    MCP-->>MCPSidecar: Tool result
    MCPSidecar-->>Agent: Return result
```

---

## 3. Component Decomposition

### 3.1 Decomposition Justification

The monolithic ZTA server must be split to achieve:
1. **Scalability**: Token issuance, introspection, and AI pipelines have different scaling characteristics
2. **Fault isolation**: AI pipeline failures shouldn't crash token validation
3. **Security**: Introspection logic should run closer to workloads (sidecar) to reduce network trust
4. **Observability**: Dedicated telemetry service can handle high-volume event streams

### 3.2 Proposed Component Architecture

```mermaid
graph TB
    subgraph "Control Plane Components"
        AUTH[Auth Service<br/>Token Issuance & Exchange]
        POLICY[Policy Service<br/>MAS/Tool/Scope Management]
        PIPE[AI Pipeline Service<br/>Embeddings & LLM Verifier]
        TELEM[Telemetry Service<br/>Event Collection & Storage]
        DISC[MCP Discovery Service<br/>Tool Introspection]
    end

    subgraph "Data Plane Components"
        SIDECAR[ZTA Sidecar Proxy<br/>Token Caching & Validation]
    end

    subgraph "Infrastructure"
        KC[Keycloak IdP]
        PG[(PostgreSQL)]
        REDIS[(Redis Cache)]
    end

    AUTH --> KC
    AUTH --> PG
    AUTH --> POLICY
    AUTH --> PIPE
    AUTH --> TELEM

    POLICY --> PG
    PIPE --> PG
    PIPE -->|OpenAI API| EXT[External LLM]
    TELEM --> PG
    DISC -->|MCP Protocol| MCP_EXT[MCP Servers]

    SIDECAR -->|Token Ops| AUTH
    SIDECAR -->|Introspect| AUTH
    SIDECAR --> REDIS
    SIDECAR -->|Events| TELEM

    style AUTH fill:#4ecdc4
    style SIDECAR fill:#ff6b6b
    style PIPE fill:#ffe66d
```

### 3.3 Component Definitions

#### 3.3.1 Auth Service (Control Plane)

**Responsibilities:**
- OAuth2 token generation (client credentials flow)
- Token exchange (RFC 8693) with tool check orchestration
- Token introspection endpoint
- User input storage and correlation
- Integration with Keycloak for token cryptography

**APIs:**
- `POST /oauth/token` - Generate initial token with user input
- `POST /oauth/token/exchange` - Exchange token for delegated/scoped token
- `POST /oauth/introspect` - Validate token and return claims

**Scaling:**
- Horizontal: Stateless, can scale to N replicas
- Bottleneck: Keycloak token generation (external call)

**Dependencies:**
- Keycloak (IdP)
- PostgreSQL (user input, apps, MAS)
- Policy Service (app metadata)
- AI Pipeline Service (tool matching)
- Telemetry Service (event emission)

**Container Image:** `zta-auth-service:v1`

---

#### 3.3.2 Policy Service (Control Plane)

**Responsibilities:**
- CRUD operations for Apps, MAS, Tools, Scopes
- Tool check flag management per MAS
- Authorization server (Keycloak realm) lifecycle
- Serve app/MAS metadata to Auth Service

**APIs:**
- `GET/POST/PUT/DELETE /apps` - Application management
- `GET/POST/PUT/DELETE /mas` - Multi-Agent System management
- `GET/POST/PUT/DELETE /scopes` - Scope management
- `GET /apps/{id}/tools` - List tools for an app
- `GET /mas/{id}/policy` - Get enabled tool checks

**Scaling:**
- Horizontal: Stateless reads, writes via database locking
- Cache: Redis for app/MAS metadata (TTL 5min)

**Dependencies:**
- PostgreSQL (primary data store)
- Redis (read cache)

**Container Image:** `zta-policy-service:v1`

---

#### 3.3.3 AI Pipeline Service (Control Plane)

**Responsibilities:**
- Task-to-tool matching (embeddings, LLM verifier, hybrid)
- Embedding generation and caching
- LLM-based tool intent verification
- Threshold tuning and evaluation

**APIs:**
- `POST /pipelines/task-tool-match` - Match task to requested tool
  ```json
  {
    "task": "Read the config file",
    "requested_tool": "filesystem:read",
    "available_tools": ["filesystem:read", "filesystem:write", "web:fetch"]
  }
  ```
- `POST /pipelines/embeddings` - Generate embeddings for tool descriptions

**Scaling:**
- Horizontal: Stateless, can scale independently
- Resource: CPU/memory-intensive (embedding computation)
- Rate limiting: Protect against OpenAI API quota exhaustion

**Dependencies:**
- OpenAI API (embeddings: text-embedding-3-large, LLM: gpt-4o)
- Redis (embedding cache, TTL 24h)

**Configuration:**
- `MATCHER_TYPE`: `embeddings` | `llm_verifier` | `hybrid`
- `EMBEDDINGS_THRESHOLD`: 0.0-1.0 (default 0.2)
- `LLM_TEMPERATURE`: 0.0 (deterministic)

**Container Image:** `zta-ai-pipeline-service:v1`

---

#### 3.3.4 Telemetry Service (Control Plane)

**Responsibilities:**
- High-volume event ingestion (token issued, exchanged, LLM calls, MCP calls)
- Event validation and enrichment
- Persistent storage to PostgreSQL
- Event query API for traces and analytics

**APIs:**
- `POST /telemetry/events` - Ingest batch of events
- `GET /telemetry/traces/{user_input_id}` - Get full trace for a user input
- `GET /telemetry/llm-calls/{app_id}` - Get LLM call history

**Scaling:**
- Horizontal: Stateless, partitioned by event type or user_input_id
- Async: Events buffered in Redis queue, batch written to PostgreSQL
- Performance: 10k events/sec target throughput

**Dependencies:**
- PostgreSQL (event store)
- Redis (event queue)

**Container Image:** `zta-telemetry-service:v1`

---

#### 3.3.5 MCP Discovery Service (Control Plane)

**Responsibilities:**
- Asynchronous MCP tool discovery via HTTP streaming
- Tool schema parsing and storage
- Background refresh of tool metadata (every 5min)
- Health checks for MCP servers

**APIs:**
- `GET /discovery/mcp/{app_id}/tools` - Get cached tools for MCP server
- `POST /discovery/mcp/{app_id}/refresh` - Force tool refresh

**Scaling:**
- Horizontal: Each replica can discover different MCP servers
- Async: Uses asyncio for concurrent MCP connections

**Dependencies:**
- MCP Protocol client library
- PostgreSQL (tool metadata)

**Container Image:** `zta-mcp-discovery-service:v1`

---

#### 3.3.6 ZTA Sidecar Proxy (Data Plane)

**Responsibilities:**
- L7 HTTP/HTTPS proxy for application container
- Token injection into outbound requests
- Token introspection caching (TTL 30s)
- Protocol enforcement (MCP, A2A)
- Request/response logging
- Fail-closed: Deny traffic if ZTA control plane unreachable

**Features:**
- **Token Caching**: Cache introspection results to reduce control plane load
- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breaker**: Stop calling control plane if error rate > 50%
- **Metrics**: Prometheus endpoint for request rates, latencies, cache hit ratio

**Configuration (Annotations/Env Vars):**
- `ZTA_CONTROL_PLANE_URL`: URL of Auth Service
- `ZTA_TELEMETRY_URL`: URL of Telemetry Service
- `ZTA_APP_ID`: Application ID from Policy Service
- `ZTA_ALLOWED_PROTOCOLS`: `mcp,a2a` (enforced at L7)
- `ZTA_FAIL_OPEN`: `false` (fail-closed by default)

**Injection Method:**
- Mutating webhook adds sidecar to pods with label `zta.io/enabled=true`
- Init container copies iptables rules to redirect app traffic to sidecar

**Container Image:** `zta-sidecar-proxy:v1`

**Ports:**
- `15001` - Inbound proxy (from other sidecars)
- `15002` - Outbound proxy (to other sidecars/control plane)
- `15003` - Admin/metrics endpoint

---

### 3.4 Component Interaction Matrix

| Component | Auth | Policy | AI Pipeline | Telemetry | Discovery | Sidecar | Keycloak | PostgreSQL | Redis |
|-----------|------|--------|-------------|-----------|-----------|---------|----------|------------|-------|
| Auth Service | - | Read | Sync Call | Async Push | Read | Serve | Sync Call | Read/Write | - |
| Policy Service | - | - | - | - | - | Serve | Read | Read/Write | Read/Write |
| AI Pipeline | - | - | - | - | - | Serve | - | - | Read/Write |
| Telemetry | - | - | - | - | - | Serve | - | Write | Read/Write |
| Discovery | - | Read | - | - | - | - | - | Read/Write | - |
| Sidecar | Sync Call | - | - | Async Push | - | - | - | - | Read |

**Legend:**
- **Sync Call**: Blocking RPC/HTTP request
- **Async Push**: Fire-and-forget event
- **Serve**: Responds to requests
- **Read**: Query data
- **Write**: Persist data

---

## 4. Sidecar vs eBPF Responsibility Model

### 4.1 Enforcement Layer Responsibility Table

| Capability | Sidecar (L7) | eBPF (L3/L4) | Control Plane | Justification |
|------------|--------------|--------------|---------------|---------------|
| **Network Policy Enforcement** |
| Deny-by-default | ❌ | ✅ | ❌ | eBPF blocks at kernel level (pre-userspace) |
| Allow-list per pod | ❌ | ✅ | ❌ | CiliumNetworkPolicy defines allowed endpoints |
| Protocol filtering (MCP/A2A) | ✅ | ⚠️ | ❌ | Sidecar inspects L7, eBPF sees L4 (TCP) |
| Rate limiting | ✅ | ⚠️ | ❌ | Sidecar (per-request), eBPF (per-connection) |
| **Token Operations** |
| Token acquisition | ✅ | ❌ | ✅ | Sidecar requests from control plane |
| Token injection | ✅ | ❌ | ❌ | Sidecar adds Authorization header |
| Token extraction | ✅ | ✅ | ❌ | Both extract for logging/validation |
| Token validation (JWT decode) | ✅ | ⚠️ | ✅ | Sidecar fully validates, eBPF checks signature only |
| Token caching | ✅ | ❌ | ❌ | Sidecar caches introspection results |
| **Observability** |
| Flow logging | ❌ | ✅ | ❌ | eBPF via Hubble (Cilium observability) |
| Request logging | ✅ | ❌ | ✅ | Sidecar logs L7 details, sent to telemetry |
| Token in logs | ✅ | ✅ | ✅ | All three log token metadata (not secrets) |
| Distributed tracing | ✅ | ❌ | ✅ | Sidecar propagates trace context |
| **Security Enforcement** |
| Token scope validation | ✅ | ⚠️ | ✅ | Sidecar checks scopes, eBPF checks presence |
| Tool authorization | ❌ | ❌ | ✅ | Control plane runs tool checks |
| MCP auth header validation | ✅ | ❌ | ✅ | Sidecar extracts, control plane validates |
| LLM endpoint restriction | ❌ | ✅ | ❌ | eBPF enforces single egress FQDN |
| Token exfiltration prevention | ⚠️ | ✅ | ❌ | eBPF blocks unexpected egress |
| **Advanced Features** |
| JWT signature verification | ✅ | ✅ | ✅ | eBPF does fast path, sidecar full validation |
| Token exchange | ✅ | ❌ | ✅ | Sidecar requests, control plane issues |
| mTLS termination | ✅ | ❌ | ❌ | Sidecar handles TLS |

**Legend:**
- ✅ Primary responsibility
- ⚠️ Partial/secondary responsibility
- ❌ Not responsible

### 4.2 eBPF Capabilities with Cilium

#### 4.2.1 L3/L4 Policy Enforcement

**What eBPF Does:**
- Attach to network interfaces (veth pairs)
- Inspect packet headers (IP src/dst, TCP/UDP ports)
- Match against CiliumNetworkPolicy rules
- Drop/forward packets at kernel level (pre-routing)

**Example: Deny-by-default with MCP server allow-list**
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: agent-default-deny
  namespace: production-mas
spec:
  endpointSelector:
    matchLabels:
      app: agent
  egress:
  - toEndpoints:
    - matchLabels:
        app: mcp-server  # Only allow agent → MCP
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
  - toEndpoints:
    - matchLabels:
        app: zta-auth-service  # Allow agent → ZTA
        namespace: zta-control-plane
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
  - toFQDNs:
    - matchName: "api.openai.com"  # Single LLM egress
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
```

#### 4.2.2 JWT Token Extraction and Validation in eBPF

**Feasibility Analysis:**
- eBPF can parse HTTP headers (XDP/TC hooks)
- Extract `Authorization: Bearer <token>` header
- Validate JWT signature using embedded public key (requires BPF map with JWKs)
- Check basic claims (exp, iat) without full decode

**Implementation:**
1. **BPF Map**: Store JWK public keys (updated by control plane)
   ```c
   struct bpf_map_def SEC("maps") jwt_public_keys = {
       .type = BPF_MAP_TYPE_HASH,
       .key_size = sizeof(__u32),  // key_id
       .value_size = 256,          // RSA public key
       .max_entries = 10,
   };
   ```

2. **eBPF Program**: Extract token from HTTP request
   ```c
   SEC("tc/ingress")
   int validate_jwt_token(struct __sk_buff *skb) {
       // Parse HTTP headers
       char *auth_header = extract_http_header(skb, "Authorization");
       if (!auth_header) return TC_ACT_SHOT;  // Drop

       // Extract JWT
       char *token = auth_header + 7;  // Skip "Bearer "

       // Decode JWT header to get key_id
       __u32 key_id = parse_jwt_header(token);

       // Lookup public key
       char *pubkey = bpf_map_lookup_elem(&jwt_public_keys, &key_id);
       if (!pubkey) return TC_ACT_SHOT;

       // Validate signature (RSA or HMAC)
       if (!verify_jwt_signature(token, pubkey)) {
           return TC_ACT_SHOT;  // Invalid signature
       }

       // Check expiration
       __u64 exp = parse_jwt_claim(token, "exp");
       __u64 now = bpf_ktime_get_ns() / 1000000000;
       if (exp < now) return TC_ACT_SHOT;  // Expired

       return TC_ACT_OK;  // Valid token
   }
   ```

**Limitations:**
- eBPF has limited instruction count (1M instructions per program)
- Full JWT decode (base64, JSON parsing) may exceed complexity limit
- RSA signature verification requires crypto helpers (available in kernel 5.10+)

**Recommendation:**
- **Fast path (eBPF)**: Check token presence, signature, expiration
- **Slow path (Sidecar)**: Full JWT decode, scope validation, tool authorization

#### 4.2.3 Token Exchange in eBPF

**Not Feasible:**
- Token exchange requires calling control plane (network I/O from eBPF not allowed)
- eBPF cannot maintain HTTP client connections
- Delegation token generation needs cryptographic operations (Keycloak)

**Verdict:** Token exchange MUST be handled by sidecar or control plane.

#### 4.2.4 Flow Observability with Hubble

**What Hubble Provides:**
- Real-time flow logs (src/dst pod, protocol, ports, verdict)
- L7 visibility (HTTP method, path, status code)
- Network policy verdicts (allowed/denied)
- Service dependency graph

**Integration with ZTA Telemetry:**
- Hubble exports flows to ZTA Telemetry Service
- Flows correlated with token events via pod identity
- Example flow:
  ```json
  {
    "timestamp": "2025-01-15T10:30:00Z",
    "src": {"pod": "agent-abc", "namespace": "production-mas"},
    "dst": {"pod": "mcp-server-xyz", "namespace": "production-mas"},
    "verdict": "FORWARDED",
    "l7": {
      "protocol": "HTTP",
      "method": "POST",
      "path": "/mcp/tools/invoke",
      "headers": {"Authorization": "Bearer eyJ..."}
    },
    "policy": "agent-to-mcp-allow"
  }
  ```

---

## 4.3 Sidecar Implementation Details

### 4.3.1 Sidecar Technology Stack

**Base Technology:** Envoy Proxy v1.29+

**Why Envoy:**
- Battle-tested L7 proxy with HTTP/2, gRPC support
- Mature filter ecosystem for auth, rate limiting, observability
- Dynamic configuration via xDS APIs
- Low latency (P99 < 10ms overhead)
- External auth filter for token operations

**Alternative Considered:** Custom Go proxy
- **Rejected:** Reinventing proxy logic adds risk, Envoy more mature

### 4.3.2 Sidecar Architecture

```mermaid
graph LR
    subgraph "Application Container"
        APP[App Process<br/>:8000]
    end

    subgraph "ZTA Sidecar Container"
        INBOUND[Inbound Listener<br/>:15001]
        OUTBOUND[Outbound Listener<br/>:15002]
        ADMIN[Admin API<br/>:15003]

        INBOUND --> AUTHZ[ext_authz Filter<br/>Token Validation]
        OUTBOUND --> INJECT[Lua Filter<br/>Token Injection]

        AUTHZ --> CACHE[(Local Cache<br/>Redis)]
        INJECT --> CACHE

        AUTHZ -->|Introspect| CTRLPLANE[Control Plane<br/>Auth Service]
        INJECT -->|Exchange| CTRLPLANE
    end

    subgraph "iptables Rules"
        IPT[REDIRECT<br/>App → 15001<br/>Egress → 15002]
    end

    APP -->|Intercepted| IPT
    IPT --> INBOUND
    OUTBOUND --> IPT

    style AUTHZ fill:#4ecdc4
    style INJECT fill:#ffe66d
    style CACHE fill:#95e1d3
```

### 4.3.3 Envoy Configuration Structure

**Static Configuration** (`/etc/envoy/envoy.yaml`):
```yaml
admin:
  address:
    socket_address:
      address: 127.0.0.1
      port_value: 15003

static_resources:
  listeners:
  - name: inbound_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 15001
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: inbound_http
          route_config:
            name: inbound_route
            virtual_hosts:
            - name: inbound_service
              domains: ["*"]
              routes:
              - match:
                  prefix: "/"
                route:
                  cluster: local_application
          http_filters:
          - name: envoy.filters.http.ext_authz
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
              transport_api_version: V3
              grpc_service:
                envoy_grpc:
                  cluster_name: zta_auth_service
              failure_mode_allow: false  # FAIL CLOSED
              with_request_body:
                max_request_bytes: 8192
                allow_partial_message: false
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  - name: outbound_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 15002
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: outbound_http
          route_config:
            name: outbound_route
            virtual_hosts:
            - name: outbound_service
              domains: ["*"]
              routes:
              - match:
                  prefix: "/"
                route:
                  cluster: dynamic_forward_proxy_cluster
          http_filters:
          - name: envoy.filters.http.lua
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
              inline_code: |
                function envoy_on_request(request_handle)
                  -- Inject ZTA token
                  local token = get_cached_token()
                  if token == nil then
                    token = exchange_token(request_handle)
                  end
                  request_handle:headers():add("Authorization", "Bearer " .. token)

                  -- Protocol enforcement
                  local path = request_handle:headers():get(":path")
                  if not is_allowed_protocol(path) then
                    request_handle:respond({[":status"] = "403"}, "Protocol not allowed")
                  end
                end
          - name: envoy.filters.http.router

  clusters:
  - name: local_application
    type: STATIC
    connect_timeout: 1s
    load_assignment:
      cluster_name: local_application
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: 127.0.0.1
                port_value: 8000

  - name: zta_auth_service
    type: STRICT_DNS
    connect_timeout: 5s
    typed_extension_protocol_options:
      envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
        "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
        explicit_http_config:
          http2_protocol_options: {}
    load_assignment:
      cluster_name: zta_auth_service
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: zta-auth-service.zta-control-plane.svc.cluster.local
                port_value: 8443
```

### 4.3.4 MCP/A2A Protocol Enforcement Logic

**Lua Filter Implementation** (`protocol_enforcer.lua`):
```lua
-- Protocol Enforcement Module
local ALLOWED_PROTOCOLS = {
  mcp = {
    methods = {"POST", "GET"},
    path_patterns = {
      "^/mcp/tools/list$",
      "^/mcp/tools/invoke$",
      "^/mcp/resources/list$",
      "^/mcp/resources/read$"
    }
  },
  a2a = {
    methods = {"POST"},
    path_patterns = {
      "^/a2a/delegate$",
      "^/a2a/message$"
    }
  }
}

function is_allowed_protocol(method, path)
  local app_type = os.getenv("ZTA_APP_TYPE")  -- agent, mcp_server, user_app
  local allowed = os.getenv("ZTA_ALLOWED_PROTOCOLS")  -- mcp,a2a

  for protocol in string.gmatch(allowed, "[^,]+") do
    local proto_config = ALLOWED_PROTOCOLS[protocol]
    if proto_config then
      -- Check HTTP method
      local method_allowed = false
      for _, allowed_method in ipairs(proto_config.methods) do
        if method == allowed_method then
          method_allowed = true
          break
        end
      end

      if not method_allowed then
        return false, "HTTP method not allowed for protocol: " .. protocol
      end

      -- Check path pattern
      for _, pattern in ipairs(proto_config.path_patterns) do
        if string.match(path, pattern) then
          return true, nil
        end
      end
    end
  end

  return false, "Path does not match allowed protocol patterns"
end

function envoy_on_request(request_handle)
  local method = request_handle:headers():get(":method")
  local path = request_handle:headers():get(":path")

  local allowed, err = is_allowed_protocol(method, path)
  if not allowed then
    request_handle:logWarn("Protocol violation: " .. err)
    request_handle:respond(
      {[":status"] = "403"},
      string.format([[{"error": "protocol_violation", "message": "%s"}]], err)
    )
    return
  end

  -- Continue with token injection...
end
```

### 4.3.5 Token Acquisition Flow in Sidecar

**Sequence:**
```mermaid
sequenceDiagram
    participant APP as Application
    participant SIDECAR as ZTA Sidecar
    participant CACHE as Local Cache
    participant CTRL as Control Plane

    APP->>SIDECAR: Outbound HTTP Request
    SIDECAR->>SIDECAR: Check protocol (MCP/A2A)

    alt Protocol violation
        SIDECAR->>APP: 403 Forbidden
    end

    SIDECAR->>CACHE: Lookup cached token

    alt Cache hit & valid
        CACHE->>SIDECAR: Return token
    else Cache miss/expired
        SIDECAR->>CTRL: POST /oauth/token/exchange
        Note over SIDECAR,CTRL: Request: {subject_token, requested_resources}
        CTRL->>CTRL: Run tool checks
        CTRL->>SIDECAR: TokenResponse {access_token, expires_in}
        SIDECAR->>CACHE: Store token (TTL: expires_in)
    end

    SIDECAR->>SIDECAR: Inject Authorization header
    SIDECAR->>APP: Forward request with token
```

### 4.3.6 External Auth Service (ext_authz)

**Responsibilities:**
- Validate inbound tokens via control plane introspection
- Cache introspection results (30s TTL)
- Enforce rate limits per token
- Log authorization decisions to telemetry

**Implementation:** Separate Go service (`zta-ext-authz:v1`)

**gRPC Interface:**
```protobuf
service Authorization {
  rpc Check(CheckRequest) returns (CheckResponse);
}

message CheckRequest {
  AttributeContext attributes = 1;
}

message CheckResponse {
  StatusCode status = 1;
  map<string, string> headers = 2;  // Injected headers
  string body = 3;  // Error message if denied
}
```

**Logic:**
```go
func (s *AuthzServer) Check(ctx context.Context, req *CheckRequest) (*CheckResponse, error) {
    token := req.Attributes.Request.Http.Headers["authorization"]
    if token == "" {
        return &CheckResponse{Status: PERMISSION_DENIED}, nil
    }

    // Check cache
    if cached := s.cache.Get(token); cached != nil {
        if cached.Active {
            return &CheckResponse{Status: OK}, nil
        }
        return &CheckResponse{Status: PERMISSION_DENIED}, nil
    }

    // Call control plane introspection
    resp, err := s.ctrlPlaneClient.IntrospectToken(ctx, &IntrospectRequest{Token: token})
    if err != nil || !resp.Active {
        s.cache.Set(token, &CachedResult{Active: false}, 30*time.Second)
        return &CheckResponse{Status: PERMISSION_DENIED}, nil
    }

    // Validate scopes match request
    if !s.validateScopes(resp.Scopes, req.Attributes.Request.Http.Path) {
        return &CheckResponse{Status: PERMISSION_DENIED}, nil
    }

    // Cache and allow
    s.cache.Set(token, &CachedResult{Active: true, Scopes: resp.Scopes}, 30*time.Second)

    // Emit telemetry event
    s.telemetryClient.RecordAuthzDecision(ctx, &AuthzEvent{
        Token: hashToken(token),
        Decision: "ALLOW",
        Path: req.Attributes.Request.Http.Path,
    })

    return &CheckResponse{Status: OK}, nil
}
```

### 4.3.7 Sidecar Injection Mechanism

**MutatingWebhookConfiguration:**
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: zta-sidecar-injector
webhooks:
- name: sidecar.zta.io
  clientConfig:
    service:
      name: zta-injector
      namespace: zta-system
      path: /inject
  rules:
  - operations: ["CREATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  namespaceSelector:
    matchLabels:
      zta.io/injection: enabled
  objectSelector:
    matchExpressions:
    - key: zta.io/inject-sidecar
      operator: NotIn
      values: ["false"]
  admissionReviewVersions: ["v1"]
  sideEffects: None
  failurePolicy: Fail  # Prevent pod creation if injection fails
```

**Injector Logic:**
```go
func (i *Injector) Inject(pod *corev1.Pod) (*corev1.Pod, error) {
    // Skip if already injected
    if pod.Annotations["zta.io/sidecar-injected"] == "true" {
        return pod, nil
    }

    // Extract MAS config from namespace annotation
    masID := pod.Namespace  // Assumes namespace = MAS
    masConfig, err := i.configClient.GetMAS(masID)
    if err != nil {
        return nil, err
    }

    // Determine app type from pod labels
    appType := pod.Labels["zta.io/app-type"]  // agent, mcp_server, user_app
    if appType == "" {
        return nil, errors.New("missing label: zta.io/app-type")
    }

    // Build sidecar container
    sidecar := corev1.Container{
        Name:  "zta-sidecar",
        Image: "zta-sidecar-proxy:v1.0.0",
        Ports: []corev1.ContainerPort{
            {Name: "inbound", ContainerPort: 15001},
            {Name: "outbound", ContainerPort: 15002},
            {Name: "admin", ContainerPort: 15003},
        },
        Env: []corev1.EnvVar{
            {Name: "ZTA_CONTROL_PLANE_URL", Value: "https://zta-auth-service.zta-control-plane.svc:8443"},
            {Name: "ZTA_APP_TYPE", Value: appType},
            {Name: "ZTA_APP_ID", Value: pod.Labels["zta.io/app-id"]},
            {Name: "ZTA_ALLOWED_PROTOCOLS", Value: getAllowedProtocols(appType)},
        },
        VolumeMounts: []corev1.VolumeMount{
            {Name: "envoy-config", MountPath: "/etc/envoy"},
        },
    }

    // Add init container for iptables
    initContainer := corev1.Container{
        Name:  "zta-init",
        Image: "zta-init:v1.0.0",
        SecurityContext: &corev1.SecurityContext{
            Capabilities: &corev1.Capabilities{
                Add: []corev1.Capability{"NET_ADMIN"},
            },
        },
        Command: []string{"/bin/sh", "-c", `
            # Redirect inbound traffic to sidecar
            iptables -t nat -A PREROUTING -p tcp -j REDIRECT --to-port 15001

            # Redirect outbound traffic to sidecar (except sidecar itself)
            iptables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner 1337 -j REDIRECT --to-port 15002
        `},
    }

    // Modify pod spec
    pod.Spec.InitContainers = append(pod.Spec.InitContainers, initContainer)
    pod.Spec.Containers = append(pod.Spec.Containers, sidecar)
    pod.Annotations["zta.io/sidecar-injected"] = "true"

    return pod, nil
}

func getAllowedProtocols(appType string) string {
    switch appType {
    case "agent":
        return "mcp,a2a"  // Agents can use both
    case "mcp_server":
        return "mcp"  // MCP servers only respond to MCP
    case "user_app":
        return "mcp,a2a"  // User apps can use both
    default:
        return ""
    }
}
```

---

## 5. Network Architecture & Policy Enforcement

### 5.1 Cluster Network Topology

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress Namespace"
            ING[Ingress Controller<br/>nginx/Cilium]
        end

        subgraph "zta-control-plane Namespace"
            AUTH[Auth Service]
            POLICY[Policy Service]
            PIPE[AI Pipeline]
            TELEM[Telemetry]
            DISC[Discovery]
            KC[Keycloak]
            PG[(PostgreSQL)]
            REDIS[(Redis)]
        end

        subgraph "production-mas Namespace"
            subgraph "User App Pod"
                UA[User App] --> UAS[Sidecar]
            end
            subgraph "Agent Pod"
                AG[Agent] --> AGS[Sidecar]
            end
            subgraph "MCP Pod"
                MCP[MCP Server] --> MCPS[Sidecar]
            end
        end

        subgraph "dev-mas Namespace"
            DEV[Dev Workloads]
        end
    end

    subgraph "External"
        USER[End Users]
        LLM[OpenAI API]
    end

    USER -->|HTTPS| ING
    ING -->|Allowed| UA

    UAS -->|Auth| AUTH
    AGS -->|Auth| AUTH
    MCPS -->|Auth| AUTH

    AGS -->|HTTPS| LLM

    AUTH --> KC
    AUTH --> PG
    POLICY --> PG
    PIPE --> LLM
    TELEM --> PG

    subgraph "Cilium eBPF"
        NP[Network Policies<br/>Identity-Based]
    end

    NP -.->|Enforces| UA
    NP -.->|Enforces| AG
    NP -.->|Enforces| MCP
    NP -.->|Enforces| AUTH

    style NP fill:#ff6b6b
    style LLM fill:#ffe66d
```

### 5.2 CiliumNetworkPolicy Examples

#### 5.2.1 Default Deny for MAS Namespace

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny-all
  namespace: production-mas
spec:
  endpointSelector: {}  # Match all pods in namespace
  ingress: []  # Deny all ingress
  egress: []   # Deny all egress
```

#### 5.2.2 Allow User App → ZTA Control Plane

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: userapp-to-zta
  namespace: production-mas
spec:
  endpointSelector:
    matchLabels:
      app: user-app
  egress:
  - toEndpoints:
    - matchLabels:
        app: zta-auth-service
        io.kubernetes.pod.namespace: zta-control-plane
    toPorts:
    - ports:
      - port: "8443"
        protocol: TCP
      rules:
        http:
        - method: "POST"
          path: "/oauth/token"
```

#### 5.2.3 Allow Agent → MCP (MCP Protocol Only)

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: agent-to-mcp
  namespace: production-mas
spec:
  endpointSelector:
    matchLabels:
      app: agent
  egress:
  - toEndpoints:
    - matchLabels:
        app: mcp-server
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "POST"
          path: "/mcp/*"  # MCP protocol paths
        - method: "GET"
          path: "/mcp/*"
```

**Note:** L7 protocol filtering (MCP vs HTTP) is enforced by sidecar, not eBPF. eBPF enforces L4 connectivity.

#### 5.2.4 Allow Agent → External LLM (Single Endpoint)

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: agent-to-llm
  namespace: production-mas
spec:
  endpointSelector:
    matchLabels:
      app: agent
  egress:
  - toFQDNs:
    - matchPattern: "*.openai.com"  # Allow OpenAI API
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
  - toFQDNs:
    - matchPattern: "api.anthropic.com"  # BLOCKED (not in policy)
```

**Enforcement:**
- Cilium DNS proxy intercepts DNS queries
- Only allowed FQDNs resolve
- All other egress is dropped

#### 5.2.5 Control Plane Internal Communication

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: control-plane-mesh
  namespace: zta-control-plane
spec:
  endpointSelector:
    matchLabels:
      tier: control-plane
  ingress:
  - fromEndpoints:
    - matchLabels:
        tier: control-plane  # Allow control plane services to talk
  - fromEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: production-mas  # Allow MAS workloads
        zta.io/enabled: "true"
  egress:
  - toEndpoints:
    - matchLabels:
        tier: control-plane
  - toEndpoints:
    - matchLabels:
        app: postgresql
  - toEndpoints:
    - matchLabels:
        app: redis
```

### 5.3 Identity-Aware Policies

**Cilium Security Identities:**
- Each pod gets a numeric identity based on labels
- Example identities:
  - `1234` = `app=agent, namespace=production-mas, zta.io/enabled=true`
  - `5678` = `app=mcp-server, namespace=production-mas, zta.io/enabled=true`
  - `9012` = `app=zta-auth-service, namespace=zta-control-plane`

**Policy Enforcement:**
- eBPF programs match identities, not IP addresses
- Policies survive pod restarts/reschedules
- Identity propagated in packet metadata (no IP dependency)

**Example: Agent can only call MCP if both have ZTA sidecar**
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: agent-to-mcp-zta-only
  namespace: production-mas
spec:
  endpointSelector:
    matchLabels:
      app: agent
      zta.io/enabled: "true"
  egress:
  - toEndpoints:
    - matchLabels:
        app: mcp-server
        zta.io/enabled: "true"  # Both must have sidecar
```

### 5.4 Observability Pipeline

```mermaid
graph LR
    subgraph "Data Sources"
        HUBBLE[Cilium Hubble<br/>Flow Logs]
        SIDECAR[ZTA Sidecars<br/>L7 Logs]
        CTRL[Control Plane<br/>Token Events]
    end

    subgraph "Aggregation"
        TELEM[Telemetry Service]
        PROM[Prometheus]
    end

    subgraph "Storage"
        PG[(PostgreSQL<br/>Events)]
        LOKI[(Loki<br/>Logs)]
    end

    subgraph "Visualization"
        GRAFANA[Grafana<br/>Dashboards]
        HUBBLE_UI[Hubble UI<br/>Service Map]
        ZTA_UI[ZTA Explorer<br/>Traces]
    end

    HUBBLE -->|Flow JSON| TELEM
    SIDECAR -->|Event JSON| TELEM
    CTRL -->|Event JSON| TELEM

    TELEM --> PG
    HUBBLE --> LOKI
    SIDECAR --> LOKI

    HUBBLE --> PROM
    SIDECAR --> PROM
    CTRL --> PROM

    PG --> ZTA_UI
    LOKI --> GRAFANA
    PROM --> GRAFANA
    HUBBLE --> HUBBLE_UI
```

**Metrics Collected:**
- Token issuance rate (per app, per MAS)
- Token exchange latency (p50, p95, p99)
- Tool check results (pass/fail reasons)
- AI pipeline latency (embeddings, LLM calls)
- Network policy verdicts (allowed/denied flows)
- Sidecar cache hit ratio

**Alerts:**
- Token exfiltration attempt (unexpected egress with Authorization header)
- MCP server unreachable (discovery failures)
- AI pipeline degradation (high latency/error rate)
- Unusual tool request patterns (AI anomaly detection)

---

## 5.5 Custom eBPF Programs for Token Inspection

While Cilium provides network policy enforcement, custom eBPF programs can enhance token security.

### 5.5.1 Token Extraction eBPF Program

**Purpose:** Extract JWT tokens from HTTP Authorization headers at kernel level for observability

**Implementation:** BCC/libbpf program attached to `kprobe/tcp_sendmsg`

```c
// token_extractor.bpf.c
#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <linux/tcp.h>

#define MAX_TOKEN_SIZE 2048
#define AUTHORIZATION_HEADER "Authorization: Bearer "

struct token_event {
    u32 src_ip;
    u32 dst_ip;
    u16 src_port;
    u16 dst_port;
    u32 pid;
    char token_hash[32];  // SHA256 hash of token
    u64 timestamp;
};

BPF_PERF_OUTPUT(token_events);
BPF_HASH(seen_tokens, u64, u8);  // Dedup cache

int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg) {
    // Extract socket info
    u16 family = sk->__sk_common.skc_family;
    if (family != AF_INET) return 0;

    u32 src_ip = sk->__sk_common.skc_rcv_saddr;
    u32 dst_ip = sk->__sk_common.skc_daddr;
    u16 src_port = sk->__sk_common.skc_num;
    u16 dst_port = bpf_ntohs(sk->__sk_common.skc_dport);

    // Read message buffer
    char buf[MAX_TOKEN_SIZE];
    bpf_probe_read_user(buf, sizeof(buf), msg->msg_iter.iov->iov_base);

    // Search for Authorization header
    char *auth_pos = strstr(buf, AUTHORIZATION_HEADER);
    if (auth_pos == NULL) return 0;

    // Extract token (JWT: eyJ...)
    char token[MAX_TOKEN_SIZE];
    char *token_start = auth_pos + sizeof(AUTHORIZATION_HEADER) - 1;
    int token_len = 0;
    for (int i = 0; i < MAX_TOKEN_SIZE && token_start[i] != '\r' && token_start[i] != '\n'; i++) {
        token[token_len++] = token_start[i];
    }

    // Hash token (don't log plaintext)
    char token_hash[32];
    bpf_sha256(token, token_len, token_hash);

    // Check dedup cache
    u64 hash_key = *(u64*)token_hash;
    if (seen_tokens.lookup(&hash_key)) return 0;

    // Emit event
    struct token_event event = {
        .src_ip = src_ip,
        .dst_ip = dst_ip,
        .src_port = src_port,
        .dst_port = dst_port,
        .pid = bpf_get_current_pid_tgid() >> 32,
        .timestamp = bpf_ktime_get_ns()
    };
    __builtin_memcpy(event.token_hash, token_hash, 32);
    token_events.perf_submit(ctx, &event, sizeof(event));

    // Cache for dedup
    u8 val = 1;
    seen_tokens.update(&hash_key, &val);

    return 0;
}
```

**Userspace Consumer:**
```python
from bcc import BPF
import hashlib

# Load eBPF program
b = BPF(src_file="token_extractor.bpf.c")
b.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")

def process_token_event(cpu, data, size):
    event = b["token_events"].event(data)

    # Emit to telemetry service
    telemetry_client.record_event({
        "type": "token_observed",
        "src_ip": event.src_ip,
        "dst_ip": event.dst_ip,
        "token_hash": event.token_hash.hex(),
        "timestamp": event.timestamp
    })

    # Check for token exfiltration
    if is_unexpected_destination(event.dst_ip):
        alert_security_team("Token exfiltration attempt", event)

b["token_events"].open_perf_buffer(process_token_event)
while True:
    b.perf_buffer_poll()
```

### 5.5.2 Token Validation eBPF Program (Experimental)

**Warning:** This is experimental. Full JWT validation in eBPF is constrained by:
- eBPF stack size limits (512 bytes)
- No floating point ops (needed for some crypto)
- Limited crypto primitives in kernel

**Feasible:** Fast-path signature validation using eBPF CO-RE

```c
// token_validator.bpf.c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

struct jwt_validation_result {
    u8 valid;
    u32 src_ip;
    u16 src_port;
    char reason[64];
};

BPF_HASH(pubkey_cache, u32, char[256]);  // Cache public keys by issuer
BPF_PERF_OUTPUT(validation_events);

SEC("xdp")
int validate_jwt_signature(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    // Parse Ethernet -> IP -> TCP -> HTTP
    // (omitted for brevity)

    // Extract JWT from Authorization header
    char jwt_header[256];
    char jwt_payload[512];
    char jwt_signature[256];
    parse_jwt(http_body, jwt_header, jwt_payload, jwt_signature);

    // Fast-path: Check signature with cached public key
    u32 issuer_hash = hash_issuer(jwt_payload);
    char *pubkey = pubkey_cache.lookup(&issuer_hash);
    if (pubkey == NULL) {
        // Slow path: Forward to userspace for full validation
        return XDP_PASS;
    }

    // Verify signature (Ed25519 - eBPF supported via libbpf CO-RE)
    int sig_valid = bpf_verify_signature(
        jwt_header, sizeof(jwt_header),
        jwt_payload, sizeof(jwt_payload),
        jwt_signature, sizeof(jwt_signature),
        pubkey, 256,
        BPF_SIG_ED25519
    );

    if (!sig_valid) {
        // Emit event and drop packet
        struct jwt_validation_result result = {
            .valid = 0,
            .src_ip = get_src_ip(ctx),
            .src_port = get_src_port(ctx)
        };
        strncpy(result.reason, "Invalid signature", 64);
        validation_events.perf_submit(ctx, &result, sizeof(result));

        return XDP_DROP;  // Block invalid token at kernel
    }

    return XDP_PASS;  // Allow, sidecar will do full validation
}

char _license[] SEC("license") = "GPL";
```

**Verdict:** Token signature validation in eBPF is feasible for hot-path optimization but NOT a replacement for sidecar validation. Use for:
- Early filtering of obviously invalid tokens (malformed JWT)
- DDoS mitigation (drop invalid tokens before userspace)
- Observability (count signature failures)

**NOT suitable for:**
- Full JWT validation (expiry, claims, scopes)
- Token exchange (requires control plane call)
- Complex business logic

### 5.5.3 LLM Endpoint Enforcement eBPF

**Purpose:** Block any HTTPS traffic to LLM endpoints other than the approved one

**Implementation:** Cilium DNS proxy + eBPF filter on DNS responses

```yaml
# CiliumClusterwideNetworkPolicy for LLM restriction
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: restrict-llm-access
spec:
  endpointSelector:
    matchLabels:
      zta.io/enabled: "true"
  egress:
  - toFQDNs:
    - matchPattern: "api.openai.com"  # ONLY allowed LLM
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
  - toFQDNs:
    - matchPattern: "*.openai.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
  egressDeny:
  - toFQDNs:
    - matchPattern: "api.anthropic.com"  # Explicitly block Claude
    - matchPattern: "api.cohere.ai"
    - matchPattern: "api.together.xyz"
    - matchPattern: "*.huggingface.co"
```

**DNS Proxy Logs:**
```json
{
  "timestamp": "2025-01-15T10:45:00Z",
  "source": {"pod": "agent-abc", "namespace": "production-mas"},
  "query": "api.anthropic.com",
  "verdict": "DENIED",
  "policy": "restrict-llm-access",
  "reason": "FQDN not in allow-list"
}
```

**Alert on Violation:**
```python
# Hubble consumer
def on_dns_deny(event):
    if "anthropic" in event.query or "cohere" in event.query:
        alert({
            "severity": "HIGH",
            "title": "Unauthorized LLM Access Attempt",
            "pod": event.source.pod,
            "attempted_fqdn": event.query,
            "action": "Review agent code for hardcoded LLM endpoints"
        })
```

---

## 6. Deployment Architecture

### 6.1 Pod Architecture with Sidecar

```mermaid
graph TB
    subgraph "Agent Pod"
        subgraph "Containers"
            AGENT[Agent Container<br/>Port: 8000]
            SIDECAR[ZTA Sidecar<br/>Port: 15001/15002]
            INIT[Init Container<br/>iptables setup]
        end

        subgraph "Volumes"
            TOKEN_VOL[Token Cache<br/>emptyDir]
            CONFIG_VOL[Config<br/>ConfigMap]
        end

        subgraph "Network"
            VETH[veth pair to node]
            LO[Loopback]
        end
    end

    INIT -.->|Configure| LO
    AGENT -->|Localhost| SIDECAR
    SIDECAR -->|Egress| VETH
    SIDECAR --> TOKEN_VOL
    SIDECAR --> CONFIG_VOL

    VETH -.->|eBPF Hook| CILIUM[Cilium Agent on Node]
```

**Init Container Responsibilities:**
1. Configure iptables rules to redirect traffic to sidecar
   ```bash
   # Redirect outbound traffic to sidecar
   iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-port 15002

   # Exclude sidecar's own traffic
   iptables -t nat -A OUTPUT -m owner --uid-owner 1337 -j RETURN
   ```

2. Set up network namespaces for isolation

**Sidecar Configuration (ConfigMap):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: zta-sidecar-config
  namespace: production-mas
data:
  config.yaml: |
    app_id: "agent-abc-123"
    control_plane_url: "https://zta-auth-service.zta-control-plane.svc.cluster.local:8443"
    telemetry_url: "https://zta-telemetry-service.zta-control-plane.svc.cluster.local:8443"
    allowed_protocols:
      - mcp
      - a2a
    token_cache_ttl: 30s
    fail_mode: closed
    log_level: info
```

### 6.2 StatefulSet: Control Plane Services

**Auth Service:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
spec:
  serviceName: zta-auth-service
  replicas: 3
  selector:
    matchLabels:
      app: zta-auth-service
  template:
    metadata:
      labels:
        app: zta-auth-service
        tier: control-plane
    spec:
      containers:
      - name: auth-service
        image: zta-auth-service:v1.0.0
        ports:
        - containerPort: 8443
          name: https
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: zta-db-credentials
              key: url
        - name: KEYCLOAK_URL
          value: "http://keycloak.zta-control-plane.svc.cluster.local:8080"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8443
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8443
          initialDelaySeconds: 10
          periodSeconds: 5
```

### 6.3 DaemonSet: Sidecar Injector (Alternative to Webhook)

**Note:** If using a mutating webhook is complex, deploy sidecar injector as DaemonSet that patches pods on the node.

### 6.4 Deployment: MAS Workloads

**Agent Deployment with Sidecar:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-deployment
  namespace: production-mas
  labels:
    app: agent
    zta.io/enabled: "true"
spec:
  replicas: 5
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
        zta.io/enabled: "true"
      annotations:
        zta.io/inject-sidecar: "true"
        zta.io/app-id: "agent-abc-123"
    spec:
      initContainers:
      - name: zta-init
        image: zta-sidecar-proxy:v1.0.0
        command: ["/usr/local/bin/zta-init.sh"]
        securityContext:
          capabilities:
            add: ["NET_ADMIN"]
      containers:
      - name: agent
        image: my-agent:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ZTA_SIDECAR_URL
          value: "http://localhost:15001"
      - name: zta-sidecar
        image: zta-sidecar-proxy:v1.0.0
        ports:
        - containerPort: 15001
          name: inbound
        - containerPort: 15002
          name: outbound
        - containerPort: 15003
          name: metrics
        volumeMounts:
        - name: token-cache
          mountPath: /var/zta/tokens
        - name: config
          mountPath: /etc/zta
      volumes:
      - name: token-cache
        emptyDir: {}
      - name: config
        configMap:
          name: zta-sidecar-config
```

---

## 7. Packaging Strategy

### 7.1 Helm Chart Structure

```
zta-mas-system/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── values-dev.yaml
├── charts/
│   ├── control-plane/
│   │   ├── Chart.yaml
│   │   ├── templates/
│   │   │   ├── auth-service.yaml
│   │   │   ├── policy-service.yaml
│   │   │   ├── ai-pipeline-service.yaml
│   │   │   ├── telemetry-service.yaml
│   │   │   ├── discovery-service.yaml
│   │   │   ├── keycloak.yaml
│   │   │   ├── postgresql.yaml
│   │   │   ├── redis.yaml
│   │   │   ├── services.yaml
│   │   │   ├── ingress.yaml
│   │   │   └── cilium-policies.yaml
│   │   └── values.yaml
│   └── sidecar/
│       ├── Chart.yaml
│       ├── templates/
│       │   ├── mutating-webhook.yaml
│       │   ├── configmap.yaml
│       │   └── cilium-policies.yaml
│       └── values.yaml
├── templates/
│   ├── namespace.yaml
│   └── _helpers.tpl
└── crds/
    ├── multiagentsystem-crd.yaml
    ├── ztapolicy-crd.yaml
    └── mcpserver-crd.yaml
```

### 7.2 Custom Resource Definitions (CRDs)

#### 7.2.1 MultiAgentSystem CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: multiagentsystems.zta.io
spec:
  group: zta.io
  names:
    kind: MultiAgentSystem
    plural: multiagentsystems
    singular: multiagentsystem
    shortNames:
    - mas
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              name:
                type: string
              authorizationServer:
                type: string
                description: "Keycloak realm name"
              enabledToolChecks:
                type: array
                items:
                  type: string
                  enum:
                  - DETERMINISTIC_TOOL_SELECTED
                  - DETERMINISTIC_LLM_SELECTED_TOOLS
                  - AI_POWERED_TOOL_MATCH
              apps:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    type:
                      type: string
                      enum: [agent, client, mcp_server]
                    baseUrl:
                      type: string
          status:
            type: object
            properties:
              phase:
                type: string
                enum: [Pending, Active, Failed]
              appsReady:
                type: integer
              lastSyncTime:
                type: string
                format: date-time
```

**Example MultiAgentSystem Resource:**
```yaml
apiVersion: zta.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: production-mas
  namespace: production-mas
spec:
  name: "Production Multi-Agent System"
  authorizationServer: "production-realm"
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  - DETERMINISTIC_LLM_SELECTED_TOOLS
  - AI_POWERED_TOOL_MATCH
  apps:
  - name: user-app
    type: client
    baseUrl: "http://user-app.production-mas.svc.cluster.local:8000"
  - name: orchestrator-agent
    type: agent
    baseUrl: "http://orchestrator-agent.production-mas.svc.cluster.local:8000"
  - name: filesystem-mcp
    type: mcp_server
    baseUrl: "http://filesystem-mcp.production-mas.svc.cluster.local:8080"
```

#### 7.2.2 ZTAPolicy CRD (Kubernetes-native policy definition)

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: ztapolicies.zta.io
spec:
  group: zta.io
  names:
    kind: ZTAPolicy
    plural: ztapolicies
    singular: ztapolicy
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              targetRef:
                type: object
                properties:
                  kind:
                    type: string
                    enum: [Deployment, StatefulSet, Pod]
                  name:
                    type: string
              allowedProtocols:
                type: array
                items:
                  type: string
                  enum: [mcp, a2a, http]
              allowedEndpoints:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    namespace:
                      type: string
                    port:
                      type: integer
              llmEndpoint:
                type: object
                properties:
                  fqdn:
                    type: string
                  port:
                    type: integer
```

**Example ZTAPolicy:**
```yaml
apiVersion: zta.io/v1alpha1
kind: ZTAPolicy
metadata:
  name: agent-policy
  namespace: production-mas
spec:
  targetRef:
    kind: Deployment
    name: agent-deployment
  allowedProtocols:
  - mcp
  - a2a
  allowedEndpoints:
  - name: filesystem-mcp
    namespace: production-mas
    port: 8080
  - name: zta-auth-service
    namespace: zta-control-plane
    port: 8443
  llmEndpoint:
    fqdn: api.openai.com
    port: 443
```

**Operator Behavior:**
- Watches ZTAPolicy resources
- Generates CiliumNetworkPolicy from spec
- Injects sidecar configuration
- Reconciles on changes

#### 7.2.3 Operator Controller Logic

**Architecture:** Kubernetes Operator using controller-runtime (Kubebuilder)

**Reconciliation Loop for MultiAgentSystem:**

```go
package controllers

import (
    "context"
    ztav1alpha1 "github.com/zta-mas/api/v1alpha1"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
)

type MultiAgentSystemReconciler struct {
    client.Client
    ControlPlaneClient *ztaclient.Client
    KeycloakClient     *keycloak.Client
}

func (r *MultiAgentSystemReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    mas := &ztav1alpha1.MultiAgentSystem{}
    if err := r.Get(ctx, req.NamespacedName, mas); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Phase 1: Create Keycloak Realm
    if mas.Status.Phase != "Active" {
        if err := r.ensureKeycloakRealm(ctx, mas); err != nil {
            mas.Status.Phase = "Failed"
            r.Status().Update(ctx, mas)
            return ctrl.Result{}, err
        }
    }

    // Phase 2: Register Apps in Control Plane
    appsReady := 0
    for _, appSpec := range mas.Spec.Apps {
        app, err := r.ControlPlaneClient.GetApp(ctx, appSpec.Name)
        if err != nil || app == nil {
            // Create app
            clientCreds, err := r.KeycloakClient.CreateClient(ctx, mas.Spec.AuthorizationServer, appSpec.Name)
            if err != nil {
                continue
            }

            _, err = r.ControlPlaneClient.CreateApp(ctx, &CreateAppRequest{
                Name:     appSpec.Name,
                Type:     appSpec.Type,
                BaseUrl:  appSpec.BaseUrl,
                ClientID: clientCreds.ClientID,
                MASId:    mas.Name,
            })
            if err != nil {
                continue
            }
        }
        appsReady++
    }

    // Phase 3: Generate CiliumNetworkPolicies
    if err := r.reconcileNetworkPolicies(ctx, mas); err != nil {
        return ctrl.Result{}, err
    }

    // Phase 4: Update sidecar ConfigMaps
    if err := r.reconcileSidecarConfigs(ctx, mas); err != nil {
        return ctrl.Result{}, err
    }

    // Update status
    mas.Status.Phase = "Active"
    mas.Status.AppsReady = int32(appsReady)
    mas.Status.LastSyncTime = metav1.Now()
    r.Status().Update(ctx, mas)

    return ctrl.Result{RequeueAfter: 60 * time.Second}, nil
}

func (r *MultiAgentSystemReconciler) reconcileNetworkPolicies(ctx context.Context, mas *ztav1alpha1.MultiAgentSystem) error {
    // Generate default-deny policy
    defaultDeny := &ciliumv2.CiliumNetworkPolicy{
        ObjectMeta: metav1.ObjectMeta{
            Name:      "default-deny-all",
            Namespace: mas.Namespace,
            OwnerReferences: []metav1.OwnerReference{
                *metav1.NewControllerRef(mas, ztav1alpha1.GroupVersion.WithKind("MultiAgentSystem")),
            },
        },
        Spec: &ciliumapi.NetworkPolicySpec{
            EndpointSelector: ciliumapi.EndpointSelector{},
            Ingress:          []ciliumapi.IngressRule{},
            Egress:           []ciliumapi.EgressRule{},
        },
    }
    if err := r.Create(ctx, defaultDeny); err != nil && !errors.IsAlreadyExists(err) {
        return err
    }

    // Generate agent→MCP policies
    for _, app := range mas.Spec.Apps {
        if app.Type == "agent" {
            policy := r.generateAgentToMCPPolicy(mas, app)
            if err := r.Create(ctx, policy); err != nil && !errors.IsAlreadyExists(err) {
                return err
            }
        }
    }

    // Generate control plane access policies
    controlPlanePolicy := r.generateControlPlaneAccessPolicy(mas)
    if err := r.Create(ctx, controlPlanePolicy); err != nil && !errors.IsAlreadyExists(err) {
        return err
    }

    return nil
}

func (r *MultiAgentSystemReconciler) generateAgentToMCPPolicy(mas *ztav1alpha1.MultiAgentSystem, agent ztav1alpha1.App) *ciliumv2.CiliumNetworkPolicy {
    mcpServers := []string{}
    for _, app := range mas.Spec.Apps {
        if app.Type == "mcp_server" {
            mcpServers = append(mcpServers, app.Name)
        }
    }

    egressRules := []ciliumapi.EgressRule{}
    for _, mcpServer := range mcpServers {
        egressRules = append(egressRules, ciliumapi.EgressRule{
            ToEndpoints: []ciliumapi.EndpointSelector{
                {
                    MatchLabels: map[string]string{
                        "app":                mcpServer,
                        "zta.io/enabled":     "true",
                    },
                },
            },
            ToPorts: []ciliumapi.PortRule{
                {
                    Ports: []ciliumapi.PortProtocol{
                        {Port: "8080", Protocol: "TCP"},
                    },
                    Rules: &ciliumapi.L7Rules{
                        HTTP: []ciliumapi.PortRuleHTTP{
                            {Method: "POST", Path: "/mcp/*"},
                            {Method: "GET", Path: "/mcp/*"},
                        },
                    },
                },
            },
        })
    }

    return &ciliumv2.CiliumNetworkPolicy{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("%s-to-mcp", agent.Name),
            Namespace: mas.Namespace,
            OwnerReferences: []metav1.OwnerReference{
                *metav1.NewControllerRef(mas, ztav1alpha1.GroupVersion.WithKind("MultiAgentSystem")),
            },
        },
        Spec: &ciliumapi.NetworkPolicySpec{
            EndpointSelector: ciliumapi.EndpointSelector{
                MatchLabels: map[string]string{
                    "app":            agent.Name,
                    "zta.io/enabled": "true",
                },
            },
            Egress: egressRules,
        },
    }
}
```

**Reconciliation Loop for ZTAPolicy:**

```go
type ZTAPolicyReconciler struct {
    client.Client
}

func (r *ZTAPolicyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    policy := &ztav1alpha1.ZTAPolicy{}
    if err := r.Get(ctx, req.NamespacedName, policy); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Generate CiliumNetworkPolicy from ZTAPolicy
    cnp := r.translateToCiliumPolicy(policy)

    // Apply CiliumNetworkPolicy
    if err := r.Create(ctx, cnp); err != nil {
        if errors.IsAlreadyExists(err) {
            if err := r.Update(ctx, cnp); err != nil {
                return ctrl.Result{}, err
            }
        } else {
            return ctrl.Result{}, err
        }
    }

    // Update target deployment with sidecar config
    if err := r.updateTargetDeployment(ctx, policy); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}

func (r *ZTAPolicyReconciler) translateToCiliumPolicy(policy *ztav1alpha1.ZTAPolicy) *ciliumv2.CiliumNetworkPolicy {
    egressRules := []ciliumapi.EgressRule{}

    // Add allowed endpoints
    for _, endpoint := range policy.Spec.AllowedEndpoints {
        egressRules = append(egressRules, ciliumapi.EgressRule{
            ToEndpoints: []ciliumapi.EndpointSelector{
                {
                    MatchLabels: map[string]string{
                        "app": endpoint.Name,
                        "io.kubernetes.pod.namespace": endpoint.Namespace,
                    },
                },
            },
            ToPorts: []ciliumapi.PortRule{
                {
                    Ports: []ciliumapi.PortProtocol{
                        {Port: strconv.Itoa(endpoint.Port), Protocol: "TCP"},
                    },
                },
            },
        })
    }

    // Add LLM endpoint if specified
    if policy.Spec.LLMEndpoint.FQDN != "" {
        egressRules = append(egressRules, ciliumapi.EgressRule{
            ToFQDNs: []ciliumapi.FQDNSelector{
                {MatchPattern: policy.Spec.LLMEndpoint.FQDN},
            },
            ToPorts: []ciliumapi.PortRule{
                {
                    Ports: []ciliumapi.PortProtocol{
                        {Port: strconv.Itoa(policy.Spec.LLMEndpoint.Port), Protocol: "TCP"},
                    },
                },
            },
        })
    }

    return &ciliumv2.CiliumNetworkPolicy{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("%s-generated", policy.Name),
            Namespace: policy.Namespace,
            OwnerReferences: []metav1.OwnerReference{
                *metav1.NewControllerRef(policy, ztav1alpha1.GroupVersion.WithKind("ZTAPolicy")),
            },
        },
        Spec: &ciliumapi.NetworkPolicySpec{
            EndpointSelector: ciliumapi.EndpointSelector{
                MatchLabels: map[string]string{
                    "app": policy.Spec.TargetRef.Name,
                },
            },
            Egress: egressRules,
        },
    }
}
```

**Operator Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zta-operator
  namespace: zta-system
spec:
  replicas: 2  # HA
  selector:
    matchLabels:
      app: zta-operator
  template:
    metadata:
      labels:
        app: zta-operator
    spec:
      serviceAccountName: zta-operator
      containers:
      - name: manager
        image: zta-operator:v1.0.0
        command:
        - /manager
        args:
        - --leader-elect
        - --health-probe-bind-address=:8081
        - --metrics-bind-address=:8080
        env:
        - name: ZTA_CONTROL_PLANE_URL
          value: "https://zta-auth-service.zta-control-plane.svc:8443"
        - name: KEYCLOAK_URL
          value: "http://keycloak.zta-control-plane.svc:8080"
        - name: KEYCLOAK_ADMIN_USER
          valueFrom:
            secretKeyRef:
              name: keycloak-admin
              key: username
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-admin
              key: password
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8081
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8081
```

### 7.3 Helm Values (values.yaml)

```yaml
global:
  environment: production
  clusterDomain: cluster.local
  imageRegistry: ghcr.io/your-org
  imagePullPolicy: IfNotPresent

controlPlane:
  namespace: zta-control-plane

  authService:
    replicas: 3
    image:
      repository: zta-auth-service
      tag: v1.0.0
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 2000m
        memory: 4Gi
    autoscaling:
      enabled: true
      minReplicas: 3
      maxReplicas: 10
      targetCPUUtilizationPercentage: 70

  policyService:
    replicas: 2
    image:
      repository: zta-policy-service
      tag: v1.0.0

  aiPipeline:
    replicas: 3
    image:
      repository: zta-ai-pipeline-service
      tag: v1.0.0
    config:
      matcherType: hybrid
      embeddingsThreshold: 0.2
      openaiApiKey:
        secretName: openai-credentials
        secretKey: api-key

  telemetry:
    replicas: 5
    image:
      repository: zta-telemetry-service
      tag: v1.0.0
    config:
      batchSize: 100
      flushInterval: 5s

  discovery:
    replicas: 2
    image:
      repository: zta-mcp-discovery-service
      tag: v1.0.0

  keycloak:
    enabled: true
    replicas: 2
    database:
      vendor: postgres
      existingSecret: keycloak-db-credentials

  postgresql:
    enabled: true
    primary:
      persistence:
        enabled: true
        size: 100Gi
    auth:
      existingSecret: postgres-credentials

  redis:
    enabled: true
    master:
      persistence:
        enabled: true
        size: 10Gi

sidecar:
  image:
    repository: zta-sidecar-proxy
    tag: v1.0.0
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  config:
    tokenCacheTTL: 30s
    failMode: closed
    logLevel: info

cilium:
  enabled: true
  hubble:
    enabled: true
    relay:
      enabled: true
    ui:
      enabled: true

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
    dashboards:
      zta: true
  loki:
    enabled: true
```

### 7.4 Multi-Environment Configuration

**Production (values-prod.yaml):**
```yaml
global:
  environment: production

controlPlane:
  authService:
    replicas: 5
    resources:
      limits:
        cpu: 4000m
        memory: 8Gi

  aiPipeline:
    replicas: 10
    config:
      matcherType: hybrid

sidecar:
  config:
    failMode: closed
    logLevel: warn
```

**Development (values-dev.yaml):**
```yaml
global:
  environment: development

controlPlane:
  authService:
    replicas: 1

  postgresql:
    primary:
      persistence:
        size: 10Gi

sidecar:
  config:
    failMode: open  # Allow debugging
    logLevel: debug
```

### 7.5 Upgrade and Rollback Model

**Upgrade Strategy (Helm):**
1. **Pre-upgrade hook**: Backup PostgreSQL database
   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: zta-pre-upgrade-backup
     annotations:
       "helm.sh/hook": pre-upgrade
       "helm.sh/hook-weight": "1"
   spec:
     template:
       spec:
         containers:
         - name: backup
           image: postgres:16
           command: ["pg_dump"]
   ```

2. **Upgrade control plane**: Rolling update (RollingUpdate strategy)
   - Max unavailable: 1
   - Max surge: 1

3. **Upgrade sidecars**: Blue-green deployment
   - Deploy new sidecar version alongside old
   - Gradually shift traffic
   - Rollback if error rate increases

4. **Post-upgrade hook**: Run database migrations
   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: zta-post-upgrade-migrate
     annotations:
       "helm.sh/hook": post-upgrade
   ```

**Rollback Procedure:**
```bash
# Rollback Helm release
helm rollback zta-mas-system -n zta-control-plane

# Verify control plane health
kubectl get pods -n zta-control-plane
kubectl logs -n zta-control-plane deployment/zta-auth-service

# Verify sidecar connectivity
kubectl exec -n production-mas deployment/agent-deployment -c zta-sidecar -- curl localhost:15003/health
```

### 7.6 Secrets Management

#### 7.6.1 Secrets Architecture

**Secrets Hierarchy:**
```mermaid
graph TB
    VAULT[HashiCorp Vault<br/>KV v2 + Dynamic Secrets]

    subgraph "External Secrets Operator"
        ESO[ESO Controller]
    end

    subgraph "Kubernetes Secrets"
        DB_SEC[zta-db-credentials]
        KC_SEC[keycloak-admin-creds]
        LLM_SEC[openai-api-key]
        JWT_SEC[jwt-signing-keys]
    end

    subgraph "Control Plane Pods"
        AUTH[Auth Service]
        POLICY[Policy Service]
        AI[AI Pipeline]
    end

    VAULT -->|Sync every 1h| ESO
    ESO -->|Create/Update| DB_SEC
    ESO -->|Create/Update| KC_SEC
    ESO -->|Create/Update| LLM_SEC
    ESO -->|Create/Update| JWT_SEC

    DB_SEC -->|Mount as env| AUTH
    KC_SEC -->|Mount as env| AUTH
    LLM_SEC -->|Mount as file| AI
    JWT_SEC -->|Mount as file| AUTH
```

**Secrets Structure:**
```
secrets/
├── zta-db-credentials              # PostgreSQL connection
│   ├── username
│   ├── password
│   └── url
├── keycloak-db-credentials         # Keycloak database
│   ├── username
│   ├── password
│   └── url
├── keycloak-admin-credentials      # Keycloak admin API
│   ├── client-id
│   ├── client-secret
│   └── realm
├── openai-credentials              # LLM API
│   ├── api-key
│   ├── organization-id
│   └── endpoint-url
├── tls-certificates                # Service mTLS (managed by cert-manager)
│   ├── tls.crt
│   └── tls.key
├── jwt-signing-keys                # Token signing
│   ├── private-key.pem
│   └── public-key.pem
└── redis-credentials               # Cache
    └── password
```

#### 7.6.2 Vault Deployment and Configuration

**Vault StatefulSet (HA Mode):**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: vault
  namespace: vault
spec:
  serviceName: vault
  replicas: 3
  selector:
    matchLabels:
      app: vault
  template:
    metadata:
      labels:
        app: vault
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: vault
            topologyKey: kubernetes.io/hostname
      serviceAccountName: vault
      containers:
      - name: vault
        image: hashicorp/vault:1.15.4
        ports:
        - containerPort: 8200
          name: api
        - containerPort: 8201
          name: cluster
        env:
        - name: VAULT_ADDR
          value: "https://127.0.0.1:8200"
        - name: VAULT_API_ADDR
          value: "https://$(POD_IP):8200"
        - name: VAULT_CLUSTER_ADDR
          value: "https://$(POD_IP):8201"
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        args:
        - server
        - -config=/vault/config/vault.hcl
        volumeMounts:
        - name: config
          mountPath: /vault/config
        - name: data
          mountPath: /vault/data
        - name: tls
          mountPath: /vault/tls
        livenessProbe:
          httpGet:
            path: /v1/sys/health?standbyok=true
            port: 8200
            scheme: HTTPS
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /v1/sys/health?standbyok=true&perfstandbyok=true
            port: 8200
            scheme: HTTPS
          initialDelaySeconds: 30
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: vault-config
      - name: tls
        secret:
          secretName: vault-tls
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 50Gi
```

**Vault Configuration (Raft Storage + Auto-Unseal):**
```hcl
# vault.hcl
ui = true
disable_mlock = true

storage "raft" {
  path = "/vault/data"

  retry_join {
    leader_api_addr = "https://vault-0.vault.vault.svc.cluster.local:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-1.vault.vault.svc.cluster.local:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-2.vault.vault.svc.cluster.local:8200"
  }
}

listener "tcp" {
  address = "[::]:8200"
  cluster_address = "[::]:8201"
  tls_cert_file = "/vault/tls/tls.crt"
  tls_key_file = "/vault/tls/tls.key"
  tls_client_ca_file = "/vault/tls/ca.crt"
}

seal "awskms" {
  region     = "us-west-2"
  kms_key_id = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
}

api_addr = "https://vault.vault.svc.cluster.local:8200"
cluster_addr = "https://vault.vault.svc.cluster.local:8201"

telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}
```

**Vault Initialization and Unseal:**
```bash
# Initialize Vault (one-time, on first pod)
kubectl exec -n vault vault-0 -- vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > /tmp/vault-init.json

# Extract root token and unseal keys (store securely!)
cat /tmp/vault-init.json | jq -r '.root_token'
cat /tmp/vault-init.json | jq -r '.unseal_keys_b64[]'

# Auto-unseal is configured, but manual unseal for DR:
kubectl exec -n vault vault-0 -- vault operator unseal <key-1>
kubectl exec -n vault vault-0 -- vault operator unseal <key-2>
kubectl exec -n vault vault-0 -- vault operator unseal <key-3>
```

#### 7.6.3 Vault Secrets Engine Configuration

**Enable KV v2 for Static Secrets:**
```bash
# Login to Vault
export VAULT_ADDR=https://vault.vault.svc.cluster.local:8200
export VAULT_TOKEN=<root-token>

# Enable KV v2 secrets engine
vault secrets enable -version=2 -path=zta/kv kv

# Write static secrets
vault kv put zta/kv/prod/database \
  username=zta_admin \
  password=$(openssl rand -base64 32) \
  url=postgresql://postgres.zta-control-plane.svc.cluster.local:5432/zta

vault kv put zta/kv/prod/keycloak \
  admin_username=admin \
  admin_password=$(openssl rand -base64 32) \
  realm=zta-realm

vault kv put zta/kv/prod/openai \
  api_key=sk-... \
  organization_id=org-... \
  endpoint_url=https://api.openai.com/v1

vault kv put zta/kv/prod/redis \
  password=$(openssl rand -base64 32)

# Generate JWT signing keys
openssl genpkey -algorithm RSA -out /tmp/jwt-private.pem -pkeyopt rsa_keygen_bits:4096
openssl rsa -pubout -in /tmp/jwt-private.pem -out /tmp/jwt-public.pem

vault kv put zta/kv/prod/jwt \
  private_key=@/tmp/jwt-private.pem \
  public_key=@/tmp/jwt-public.pem
```

**Enable Dynamic Database Credentials:**
```bash
# Enable database secrets engine
vault secrets enable -path=zta/database database

# Configure PostgreSQL connection
vault write zta/database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  allowed_roles="zta-readonly,zta-readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.zta-control-plane.svc.cluster.local:5432/zta" \
  username="vault-admin" \
  password="vault-admin-password"

# Create role for read-only access
vault write zta/database/roles/zta-readonly \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Create role for read-write access (Auth Service)
vault write zta/database/roles/zta-readwrite \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="8h" \
  max_ttl="24h"

# Generate dynamic credentials (expires in 1h)
vault read zta/database/creds/zta-readonly
# Key                Value
# ---                -----
# lease_id           zta/database/creds/zta-readonly/abc123
# lease_duration     1h
# username           v-root-zta-readonly-abc123xyz
# password           A1a-random-password-xyz
```

#### 7.6.4 Kubernetes Authentication

**Enable Kubernetes Auth:**
```bash
vault auth enable kubernetes

# Configure Kubernetes auth with cluster details
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc.cluster.local" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token

# Create policy for ZTA services
vault policy write zta-services - <<EOF
# Allow reading static secrets
path "zta/kv/data/prod/*" {
  capabilities = ["read"]
}

# Allow generating dynamic database credentials
path "zta/database/creds/zta-readwrite" {
  capabilities = ["read"]
}

# Allow token renewal
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Allow cert-manager to access PKI
path "pki/intermediate/control-plane/sign/zta-services" {
  capabilities = ["create", "update"]
}
EOF

# Create Kubernetes role bound to service accounts
vault write auth/kubernetes/role/zta-auth-service \
  bound_service_account_names=zta-auth-service \
  bound_service_account_namespaces=zta-control-plane \
  policies=zta-services \
  ttl=1h

vault write auth/kubernetes/role/zta-policy-service \
  bound_service_account_names=zta-policy-service \
  bound_service_account_namespaces=zta-control-plane \
  policies=zta-services \
  ttl=1h

vault write auth/kubernetes/role/external-secrets-operator \
  bound_service_account_names=external-secrets \
  bound_service_account_namespaces=external-secrets \
  policies=zta-services \
  ttl=1h
```

#### 7.6.5 External Secrets Operator Integration

**ESO Installation:**
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: external-secrets
  namespace: external-secrets
spec:
  chart:
    spec:
      chart: external-secrets
      version: 0.9.11
      sourceRef:
        kind: HelmRepository
        name: external-secrets
  values:
    installCRDs: true
    webhook:
      port: 9443
```

**SecretStore for Vault:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: zta-control-plane
spec:
  provider:
    vault:
      server: "https://vault.vault.svc.cluster.local:8200"
      path: "zta/kv"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets-operator"
          serviceAccountRef:
            name: external-secrets
      caBundle: <base64-encoded-vault-ca>
```

**External Secrets Operator Integration:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: zta-db-credentials
  namespace: zta-control-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: zta-db-credentials
    creationPolicy: Owner
  data:
  - secretKey: username
    remoteRef:
      key: prod/database
      property: username
  - secretKey: password
    remoteRef:
      key: prod/database
      property: password
  - secretKey: url
    remoteRef:
      key: prod/database
      property: url
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: keycloak-admin-credentials
  namespace: zta-control-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: keycloak-admin-credentials
  data:
  - secretKey: username
    remoteRef:
      key: prod/keycloak
      property: admin_username
  - secretKey: password
    remoteRef:
      key: prod/keycloak
      property: admin_password
  - secretKey: realm
    remoteRef:
      key: prod/keycloak
      property: realm
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: openai-api-key
  namespace: zta-control-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: openai-api-key
  data:
  - secretKey: api-key
    remoteRef:
      key: prod/openai
      property: api_key
  - secretKey: organization-id
    remoteRef:
      key: prod/openai
      property: organization_id
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: jwt-signing-keys
  namespace: zta-control-plane
spec:
  refreshInterval: 24h  # JWT keys rotated daily
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: jwt-signing-keys
  data:
  - secretKey: private-key.pem
    remoteRef:
      key: prod/jwt
      property: private_key
  - secretKey: public-key.pem
    remoteRef:
      key: prod/jwt
      property: public_key
```

#### 7.6.6 Vault Agent Sidecar Injection

**Vault Agent for Dynamic Secrets:**
```yaml
# Auth Service pod with Vault Agent sidecar
apiVersion: v1
kind: Pod
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "zta-auth-service"
    vault.hashicorp.com/agent-inject-secret-db-creds: "zta/database/creds/zta-readwrite"
    vault.hashicorp.com/agent-inject-template-db-creds: |
      {{- with secret "zta/database/creds/zta-readwrite" -}}
      export DB_USERNAME="{{ .Data.username }}"
      export DB_PASSWORD="{{ .Data.password }}"
      export DB_URL="postgresql://{{ .Data.username }}:{{ .Data.password }}@postgres.zta-control-plane:5432/zta"
      {{- end }}
spec:
  serviceAccountName: zta-auth-service
  containers:
  - name: auth-service
    image: zta-auth-service:v1.0.0
    command:
    - /bin/sh
    - -c
    - |
      source /vault/secrets/db-creds
      ./auth-service
    volumeMounts:
    - name: vault-secrets
      mountPath: /vault/secrets
  # Vault Agent sidecar auto-injected by webhook
```

**Vault Agent Configuration (auto-generated):**
```hcl
exit_after_auth = false
pid_file = "/home/vault/.pid"

vault {
  address = "https://vault.vault.svc.cluster.local:8200"
  ca_cert = "/vault/ca/ca.crt"
}

auto_auth {
  method "kubernetes" {
    mount_path = "auth/kubernetes"
    config = {
      role = "zta-auth-service"
    }
  }

  sink "file" {
    config = {
      path = "/home/vault/.vault-token"
    }
  }
}

template {
  source = "/vault/configs/db-creds.tmpl"
  destination = "/vault/secrets/db-creds"

  wait {
    min = "2s"
    max = "60s"
  }
}
```

#### 7.6.7 Secrets Rotation Strategy

**Rotation Schedule:**

| Secret Type | Rotation Frequency | Rotation Method | Impact |
|-------------|-------------------|-----------------|--------|
| Database passwords (static) | 90 days | Manual in Vault, ESO auto-syncs | Pods restart to pick up new secret |
| Database credentials (dynamic) | 8 hours (auto) | Vault Agent auto-renews lease | Zero downtime (Agent handles rotation) |
| OpenAI API keys | 180 days | Manual update in Vault | Pods restart (AI Pipeline only) |
| JWT signing keys | 365 days | Automated via CronJob | Rolling restart of Auth Service |
| TLS certificates (control plane) | 90 days | cert-manager auto-renew | Rolling restart (30s downtime per pod) |
| TLS certificates (sidecars) | 24 hours | SPIRE auto-rotate | Zero downtime (Envoy SDS hot-reload) |
| Vault root token | Never (break-glass only) | Manual rotation procedure | No impact (not used in ops) |
| Vault unseal keys | Never (stored in KMS) | N/A (auto-unseal) | No impact |

**JWT Key Rotation CronJob:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: rotate-jwt-keys
  namespace: zta-control-plane
spec:
  schedule: "0 2 * * 0"  # Every Sunday at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: jwt-key-rotator
          containers:
          - name: rotate
            image: vault:1.15.4
            env:
            - name: VAULT_ADDR
              value: "https://vault.vault.svc.cluster.local:8200"
            command:
            - /bin/sh
            - -c
            - |
              # Authenticate with Vault
              vault login -method=kubernetes role=jwt-key-rotator

              # Read current keys
              vault kv get -format=json zta/kv/prod/jwt > /tmp/old-keys.json

              # Generate new keys
              openssl genpkey -algorithm RSA -out /tmp/new-private.pem -pkeyopt rsa_keygen_bits:4096
              openssl rsa -pubout -in /tmp/new-private.pem -out /tmp/new-public.pem

              # Write new keys to Vault
              vault kv put zta/kv/prod/jwt \
                private_key=@/tmp/new-private.pem \
                public_key=@/tmp/new-public.pem \
                previous_public_key=@/tmp/old-public.pem

              # Trigger Auth Service rollout
              kubectl rollout restart deployment/zta-auth-service -n zta-control-plane

              echo "JWT keys rotated successfully"
          restartPolicy: OnFailure
```

#### 7.6.8 Secrets Backup and Disaster Recovery

**Vault Backup Strategy:**
```bash
# Automated Raft snapshot backup (CronJob)
apiVersion: batch/v1
kind: CronJob
metadata:
  name: vault-backup
  namespace: vault
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: vault-backup
          containers:
          - name: backup
            image: vault:1.15.4
            env:
            - name: VAULT_ADDR
              value: "https://vault.vault.svc.cluster.local:8200"
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: s3-backup-credentials
                  key: access-key
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: s3-backup-credentials
                  key: secret-key
            command:
            - /bin/sh
            - -c
            - |
              # Take Raft snapshot
              vault operator raft snapshot save /tmp/vault-snapshot-$(date +%Y%m%d-%H%M%S).snap

              # Upload to S3
              aws s3 cp /tmp/vault-snapshot-*.snap s3://zta-vault-backups/snapshots/

              # Cleanup old local snapshots
              rm /tmp/vault-snapshot-*.snap

              # Cleanup old S3 snapshots (retain 30 days)
              aws s3 ls s3://zta-vault-backups/snapshots/ | while read -r line; do
                createDate=$(echo $line | awk '{print $1" "$2}')
                createDateSec=$(date -d "$createDate" +%s)
                olderThan=$(date -d "30 days ago" +%s)
                if [[ $createDateSec -lt $olderThan ]]; then
                  fileName=$(echo $line | awk '{print $4}')
                  aws s3 rm s3://zta-vault-backups/snapshots/$fileName
                fi
              done
          restartPolicy: OnFailure
```

**Vault Restore Procedure:**
```bash
# In DR scenario, restore Vault from snapshot

# 1. Download latest snapshot from S3
aws s3 cp s3://zta-vault-backups/snapshots/vault-snapshot-latest.snap /tmp/

# 2. Port-forward to Vault pod
kubectl port-forward -n vault vault-0 8200:8200

# 3. Restore snapshot
vault operator raft snapshot restore -force /tmp/vault-snapshot-latest.snap

# 4. Verify data
vault kv list zta/kv/prod/

# 5. Restart all Vault pods to sync
kubectl rollout restart statefulset/vault -n vault
```

**Sealed Secrets (GitOps-friendly):**
```bash
# For secrets that MUST be in Git (bootstrap secrets only)

# Install Sealed Secrets controller
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system

# Encrypt secret
kubectl create secret generic bootstrap-secret \
  --from-literal=password=super-secret \
  --dry-run=client -o yaml | \
  kubeseal --format yaml > bootstrap-sealed-secret.yaml

# Commit to Git (safe, encrypted with cluster public key)
git add bootstrap-sealed-secret.yaml
git commit -m "Add bootstrap sealed secret"
git push

# Sealed Secrets controller decrypts in-cluster
kubectl apply -f bootstrap-sealed-secret.yaml
# Creates regular Kubernetes Secret "bootstrap-secret"
```

### 7.7 GitOps Deployment Automation

#### 7.7.1 Repository Structure

**GitOps Repository Layout:**
```
zta-mas-gitops/
├── apps/                           # Application definitions
│   ├── control-plane/
│   │   ├── argocd-application.yaml
│   │   └── values/
│   │       ├── values-dev.yaml
│   │       ├── values-staging.yaml
│   │       └── values-prod.yaml
│   └── mas-workloads/
│       ├── production-mas/
│       └── dev-mas/
├── infrastructure/                 # Infrastructure components
│   ├── cilium/
│   ├── cert-manager/
│   ├── vault/
│   └── external-secrets-operator/
├── charts/                         # Helm charts
│   └── zta-mas-system/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       └── charts/                # Subcharts
└── kustomize/                      # Kustomize overlays
    ├── base/
    └── overlays/
        ├── dev/
        ├── staging/
        └── production/
```

#### 7.7.2 ArgoCD ApplicationSets

**Multi-Environment ApplicationSet:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: zta-control-plane
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - cluster: dev
        url: https://dev.k8s.example.com
        namespace: zta-control-plane-dev
        replicaCount: "1"
        resources: small
        domain: dev.zta.example.com
      - cluster: staging
        url: https://staging.k8s.example.com
        namespace: zta-control-plane-staging
        replicaCount: "2"
        resources: medium
        domain: staging.zta.example.com
      - cluster: prod
        url: https://prod.k8s.example.com
        namespace: zta-control-plane
        replicaCount: "3"
        resources: large
        domain: zta.example.com
  template:
    metadata:
      name: 'zta-control-plane-{{cluster}}'
      labels:
        environment: '{{cluster}}'
    spec:
      project: zta
      source:
        repoURL: https://github.com/your-org/zta-mas-gitops
        targetRevision: main
        path: charts/zta-mas-system
        helm:
          releaseName: zta-mas-system
          valueFiles:
          - values-{{cluster}}.yaml
          parameters:
          - name: global.environment
            value: '{{cluster}}'
          - name: global.domain
            value: '{{domain}}'
          - name: controlPlane.authService.replicas
            value: '{{replicaCount}}'
          - name: controlPlane.authService.resources.preset
            value: '{{resources}}'
      destination:
        server: '{{url}}'
        namespace: '{{namespace}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
          allowEmpty: false
        syncOptions:
        - CreateNamespace=true
        - PrunePropagationPolicy=foreground
        - PruneLast=true
        retry:
          limit: 5
          backoff:
            duration: 5s
            factor: 2
            maxDuration: 3m
```

**MAS Workloads ApplicationSet:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: mas-workloads
  namespace: argocd
spec:
  generators:
  - git:
      repoURL: https://github.com/your-org/zta-mas-gitops
      revision: main
      directories:
      - path: apps/mas-workloads/*
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: zta
      source:
        repoURL: https://github.com/your-org/zta-mas-gitops
        targetRevision: main
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

#### 7.7.3 Progressive Delivery with Argo Rollouts

**Canary Rollout for Auth Service:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
spec:
  replicas: 5
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: zta-auth-service
  template:
    metadata:
      labels:
        app: zta-auth-service
        version: stable
    spec:
      containers:
      - name: auth-service
        image: ghcr.io/your-org/zta-auth-service:v1.0.0
        ports:
        - containerPort: 8443
  strategy:
    canary:
      maxSurge: 1
      maxUnavailable: 0
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 25
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 75
      - pause: {duration: 5m}
      analysis:
        templates:
        - templateName: success-rate
        - templateName: latency-p95
        startingStep: 2
        args:
        - name: service-name
          value: zta-auth-service
      trafficRouting:
        istio:
          virtualService:
            name: zta-auth-service
            routes:
            - primary
```

**Analysis Template for Canary:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
  namespace: zta-control-plane
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    initialDelay: 1m
    interval: 1m
    count: 5
    successCondition: result[0] >= 0.95
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          sum(rate(http_requests_total{job="{{args.service-name}}",status=~"2.."}[5m]))
          /
          sum(rate(http_requests_total{job="{{args.service-name}}"}[5m]))
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: latency-p95
  namespace: zta-control-plane
spec:
  args:
  - name: service-name
  metrics:
  - name: latency-p95
    initialDelay: 1m
    interval: 1m
    count: 5
    successCondition: result[0] <= 2.0
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket{job="{{args.service-name}}"}[5m])) by (le)
          )
```

#### 7.7.4 Blue-Green Deployment Strategy

**Blue-Green Service Configuration:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
spec:
  selector:
    app: zta-auth-service
    version: blue  # Switch to 'green' during deployment
  ports:
  - port: 8443
    targetPort: 8443
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zta-auth-service-blue
  namespace: zta-control-plane
  labels:
    app: zta-auth-service
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zta-auth-service
      version: blue
  template:
    metadata:
      labels:
        app: zta-auth-service
        version: blue
    spec:
      containers:
      - name: auth-service
        image: ghcr.io/your-org/zta-auth-service:v1.0.0
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zta-auth-service-green
  namespace: zta-control-plane
  labels:
    app: zta-auth-service
    version: green
spec:
  replicas: 0  # Scaled up during deployment
  selector:
    matchLabels:
      app: zta-auth-service
      version: green
  template:
    metadata:
      labels:
        app: zta-auth-service
        version: green
    spec:
      containers:
      - name: auth-service
        image: ghcr.io/your-org/zta-auth-service:v1.1.0  # New version
```

**Automated Blue-Green Switch (ArgoCD Sync Wave):**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: zta-auth-service-deployment
  namespace: argocd
spec:
  syncPolicy:
    syncOptions:
    - ApplyOutOfSyncOnly=true
  source:
    path: apps/control-plane/auth-service
    repoURL: https://github.com/your-org/zta-mas-gitops
    targetRevision: main
  destination:
    namespace: zta-control-plane
    server: https://kubernetes.default.svc
  # Sync waves for blue-green:
  # Wave 0: Deploy green deployment (new version)
  # Wave 1: Run smoke tests on green
  # Wave 2: Switch service selector to green
  # Wave 3: Scale down blue deployment
```

**Pre-Sync Hook for Smoke Tests:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: zta-auth-service-smoke-test
  namespace: zta-control-plane
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
    argocd.argoproj.io/sync-wave: "1"
spec:
  template:
    spec:
      containers:
      - name: smoke-test
        image: curlimages/curl:latest
        command:
        - /bin/sh
        - -c
        - |
          # Test health endpoint
          for i in $(seq 1 30); do
            if curl -f http://zta-auth-service-green:8443/health; then
              echo "Health check passed"
              exit 0
            fi
            sleep 2
          done
          echo "Health check failed"
          exit 1
      restartPolicy: Never
```

#### 7.7.5 Flux CD Integration

**Flux GitRepository Source:**
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: zta-mas-system
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/your-org/zta-mas-gitops
  ref:
    branch: main
  secretRef:
    name: git-credentials
```

**Flux HelmRelease with Post-Deployment Tests:**
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: zta-mas-system
  namespace: flux-system
spec:
  interval: 10m
  chart:
    spec:
      chart: ./charts/zta-mas-system
      sourceRef:
        kind: GitRepository
        name: zta-mas-system
        namespace: flux-system
      interval: 1m
  releaseName: zta-mas-system
  targetNamespace: zta-control-plane
  install:
    createNamespace: true
    remediation:
      retries: 3
  upgrade:
    remediation:
      retries: 3
      remediateLastFailure: true
    cleanupOnFail: true
  test:
    enable: true
    timeout: 5m
  values:
    global:
      environment: production
      domain: zta.example.com
  valuesFrom:
  - kind: ConfigMap
    name: zta-mas-system-config
    valuesKey: values.yaml
  postRenderers:
  - kustomize:
      patches:
      - target:
          kind: Deployment
          name: zta-auth-service
        patch: |
          - op: add
            path: /spec/template/metadata/annotations/prometheus.io~1scrape
            value: "true"
```

**Flux Kustomization with Health Checks:**
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: zta-control-plane
  namespace: flux-system
spec:
  interval: 10m
  path: ./kustomize/overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: zta-mas-system
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: zta-auth-service
    namespace: zta-control-plane
  - apiVersion: apps/v1
    kind: StatefulSet
    name: postgresql
    namespace: zta-control-plane
  timeout: 10m
  retryInterval: 2m
  postBuild:
    substitute:
      ENVIRONMENT: production
      CLUSTER_NAME: prod-us-west-2
      REPLICA_COUNT: "3"
    substituteFrom:
    - kind: ConfigMap
      name: cluster-vars
```

**Flux Notification to Slack:**
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: zta-mas-system-alert
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
  - kind: GitRepository
    name: zta-mas-system
  - kind: HelmRelease
    name: zta-mas-system
---
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: zta-deployments
  secretRef:
    name: slack-webhook-url
```

#### 7.7.6 Helm Chart Repository

**ChartMuseum Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chartmuseum
  namespace: zta-control-plane
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chartmuseum
  template:
    metadata:
      labels:
        app: chartmuseum
    spec:
      containers:
      - name: chartmuseum
        image: ghcr.io/helm/chartmuseum:v0.16.0
        env:
        - name: STORAGE
          value: amazon
        - name: STORAGE_AMAZON_BUCKET
          value: zta-helm-charts
        - name: STORAGE_AMAZON_REGION
          value: us-west-2
        - name: AUTH_ANONYMOUS_GET
          value: "true"
        - name: DISABLE_API
          value: "false"
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: aws-credentials
          mountPath: /root/.aws
          readOnly: true
      volumes:
      - name: aws-credentials
        secret:
          secretName: chartmuseum-aws-credentials
```

**OCI Registry Alternative (Harbor):**
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: zta-mas-system
  namespace: flux-system
spec:
  chart:
    spec:
      chart: zta-mas-system
      version: 1.0.0
      sourceRef:
        kind: HelmRepository
        name: oci-harbor
        namespace: flux-system
---
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: oci-harbor
  namespace: flux-system
spec:
  type: oci
  url: oci://harbor.example.com/zta-charts
  interval: 5m
  secretRef:
    name: harbor-credentials
```

#### 7.7.7 Environment Promotion Strategy

**Promotion Workflow:**
```mermaid
graph LR
    DEV[Dev Environment<br/>Auto-deploy main]
    STAGING[Staging Environment<br/>Manual promotion]
    PROD[Production Environment<br/>Approved promotion]

    DEV -->|Tests pass| STAGING
    STAGING -->|QA approval| PROD

    DEV_TEST{Integration Tests}
    STAGING_TEST{E2E Tests}
    PROD_TEST{Smoke Tests}

    DEV --> DEV_TEST
    STAGING --> STAGING_TEST
    PROD --> PROD_TEST

    ROLLBACK[Rollback Procedure]
    PROD_TEST -->|Fail| ROLLBACK
```

**ArgoCD AppProject for Environment Isolation:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: zta-dev
  namespace: argocd
spec:
  description: ZTA MAS Development Environment
  sourceRepos:
  - https://github.com/your-org/zta-mas-gitops
  destinations:
  - namespace: 'zta-*-dev'
    server: https://dev.k8s.example.com
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
  namespaceResourceWhitelist:
  - group: '*'
    kind: '*'
---
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: zta-prod
  namespace: argocd
spec:
  description: ZTA MAS Production Environment
  sourceRepos:
  - https://github.com/your-org/zta-mas-gitops
  destinations:
  - namespace: 'zta-control-plane'
    server: https://prod.k8s.example.com
  - namespace: 'production-mas'
    server: https://prod.k8s.example.com
  clusterResourceWhitelist:
  - group: ''
    kind: Namespace
  - group: 'cilium.io'
    kind: CiliumNetworkPolicy
  namespaceResourceWhitelist:
  - group: 'apps'
    kind: Deployment
  - group: 'apps'
    kind: StatefulSet
  - group: ''
    kind: Service
  syncWindows:
  - kind: allow
    schedule: '0 8-18 * * 1-5'  # Business hours Mon-Fri
    duration: 10h
    applications:
    - '*'
  - kind: deny
    schedule: '0 0-6 * * *'  # Off-hours
    duration: 6h
    applications:
    - 'zta-control-plane-*'
```

**GitHub Actions for Promotion:**
```yaml
name: Promote to Production
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to promote'
        required: true

jobs:
  promote:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Update production values
      run: |
        yq eval '.global.imageTag = "${{ github.event.inputs.version }}"' \
          -i apps/control-plane/values/values-prod.yaml

    - name: Create PR
      uses: peter-evans/create-pull-request@v5
      with:
        title: "Promote version ${{ github.event.inputs.version }} to production"
        body: |
          ## Promotion Request

          **Version:** ${{ github.event.inputs.version }}
          **Promoted from:** Staging
          **Tests:** All staging tests passed

          **Approvals required:** 2
        branch: promote-${{ github.event.inputs.version }}
        delete-branch: true
```

---

### 7.8 mTLS and Certificate Management

#### 7.8.1 Certificate Architecture

**Trust Hierarchy:**
```mermaid
graph TB
    ROOT[Root CA<br/>Vault PKI Backend<br/>Validity: 10 years]

    INT_CP[Intermediate CA: Control Plane<br/>Validity: 5 years]
    INT_DATA[Intermediate CA: Data Plane<br/>Validity: 5 years]

    LEAF_AUTH[Auth Service Cert<br/>Validity: 90 days]
    LEAF_POLICY[Policy Service Cert<br/>Validity: 90 days]
    LEAF_TELEM[Telemetry Service Cert<br/>Validity: 90 days]

    LEAF_AGENT[Agent Sidecar Cert<br/>Validity: 24 hours]
    LEAF_MCP[MCP Sidecar Cert<br/>Validity: 24 hours]
    LEAF_APP[App Sidecar Cert<br/>Validity: 24 hours]

    ROOT --> INT_CP
    ROOT --> INT_DATA

    INT_CP --> LEAF_AUTH
    INT_CP --> LEAF_POLICY
    INT_CP --> LEAF_TELEM

    INT_DATA --> LEAF_AGENT
    INT_DATA --> LEAF_MCP
    INT_DATA --> LEAF_APP
```

**Certificate Types:**

| Component | Certificate Type | SAN (Subject Alternative Name) | Validity | Rotation |
|-----------|-----------------|--------------------------------|----------|----------|
| Root CA | Self-signed CA | `CN=ZTA Root CA` | 10 years | Manual (key ceremony) |
| Control Plane CA | Intermediate CA | `CN=ZTA Control Plane CA` | 5 years | Manual (with root key) |
| Data Plane CA | Intermediate CA | `CN=ZTA Data Plane CA` | 5 years | Manual (with root key) |
| Auth Service | Server cert | `DNS:zta-auth-service.zta-control-plane.svc.cluster.local` | 90 days | cert-manager auto-renew |
| Policy Service | Server cert | `DNS:zta-policy-service.zta-control-plane.svc.cluster.local` | 90 days | cert-manager auto-renew |
| Agent Sidecar | Client+Server cert | `URI:spiffe://zta.io/ns/production-mas/sa/agent` | 24 hours | Envoy SDS auto-fetch |
| MCP Sidecar | Client+Server cert | `URI:spiffe://zta.io/ns/production-mas/sa/mcp-server` | 24 hours | Envoy SDS auto-fetch |

#### 7.8.2 cert-manager Configuration

**Installation:**
```yaml
# cert-manager with Vault integration
apiVersion: v1
kind: Namespace
metadata:
  name: cert-manager
---
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: cert-manager
  namespace: cert-manager
spec:
  chart:
    spec:
      chart: cert-manager
      version: v1.13.3
      sourceRef:
        kind: HelmRepository
        name: jetstack
  values:
    installCRDs: true
    global:
      leaderElection:
        namespace: cert-manager
    webhook:
      securePort: 10260
    extraArgs:
    - --enable-certificate-owner-ref=true
    - --dns01-recursive-nameservers=8.8.8.8:53,1.1.1.1:53
```

**Root CA Issuer (Vault-backed):**
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: zta-root-ca
spec:
  vault:
    server: https://vault.vault.svc.cluster.local:8200
    path: pki/sign/zta-root-ca
    caBundle: <base64-encoded-vault-ca>
    auth:
      kubernetes:
        role: cert-manager
        mountPath: /v1/auth/kubernetes
        secretRef:
          name: cert-manager-vault-token
          key: token
```

**Intermediate CA Certificate:**
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: zta-control-plane-ca
  namespace: zta-control-plane
spec:
  secretName: zta-control-plane-ca-key-pair
  duration: 43800h  # 5 years
  renewBefore: 8760h  # 1 year before expiry
  commonName: "ZTA Control Plane Intermediate CA"
  isCA: true
  usages:
  - cert sign
  - crl sign
  issuerRef:
    name: zta-root-ca
    kind: ClusterIssuer
```

**Control Plane Service Certificates:**
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: zta-auth-service-tls
  namespace: zta-control-plane
spec:
  secretName: zta-auth-service-tls
  duration: 2160h  # 90 days
  renewBefore: 360h  # 15 days before expiry
  subject:
    organizations:
    - "ZTA Control Plane"
  commonName: zta-auth-service
  dnsNames:
  - zta-auth-service
  - zta-auth-service.zta-control-plane
  - zta-auth-service.zta-control-plane.svc
  - zta-auth-service.zta-control-plane.svc.cluster.local
  ipAddresses:
  - 127.0.0.1
  usages:
  - digital signature
  - key encipherment
  - server auth
  - client auth
  issuerRef:
    name: zta-control-plane-ca
    kind: Issuer
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: zta-control-plane-ca
  namespace: zta-control-plane
spec:
  ca:
    secretName: zta-control-plane-ca-key-pair
```

#### 7.8.3 SPIFFE/SPIRE Integration for Sidecars

**Why SPIFFE for Sidecars:**
- Short-lived certificates (24h validity)
- Automatic rotation via SDS (Secret Discovery Service)
- Workload identity based on Kubernetes service account
- No secret management required (certificates never touch disk)

**SPIRE Server Deployment:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: spire-server
  namespace: spire
spec:
  replicas: 3
  serviceName: spire-server
  selector:
    matchLabels:
      app: spire-server
  template:
    metadata:
      labels:
        app: spire-server
    spec:
      serviceAccountName: spire-server
      containers:
      - name: spire-server
        image: ghcr.io/spiffe/spire-server:1.8.5
        args:
        - -config
        - /run/spire/config/server.conf
        ports:
        - containerPort: 8081
          name: grpc
        volumeMounts:
        - name: spire-config
          mountPath: /run/spire/config
        - name: spire-data
          mountPath: /run/spire/data
        - name: spire-server-socket
          mountPath: /run/spire/sockets
        livenessProbe:
          httpGet:
            path: /live
            port: 8080
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
      volumes:
      - name: spire-config
        configMap:
          name: spire-server
  volumeClaimTemplates:
  - metadata:
      name: spire-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

**SPIRE Server Configuration:**
```hcl
# /run/spire/config/server.conf
server {
  bind_address = "0.0.0.0"
  bind_port = "8081"
  trust_domain = "zta.io"
  data_dir = "/run/spire/data"
  log_level = "INFO"
  ca_ttl = "24h"
  default_x509_svid_ttl = "1h"  # Short-lived!
}

plugins {
  DataStore "sql" {
    plugin_data {
      database_type = "postgres"
      connection_string = "postgresql://spire:password@postgres.zta-control-plane:5432/spire"
    }
  }

  KeyManager "disk" {
    plugin_data {
      keys_path = "/run/spire/data/keys.json"
    }
  }

  NodeAttestor "k8s_psat" {
    plugin_data {
      clusters = {
        "zta-cluster" = {
          service_account_allow_list = ["spire:spire-agent"]
        }
      }
    }
  }

  UpstreamAuthority "vault" {
    plugin_data {
      vault_addr = "https://vault.vault.svc.cluster.local:8200"
      pki_mount_point = "pki/intermediate/zta-data-plane"
      ca_cert_path = "/run/spire/vault-ca.crt"
      token_auth {
        token = "s.VAULT_TOKEN_HERE"
      }
    }
  }
}
```

**SPIRE Agent DaemonSet:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: spire-agent
  namespace: spire
spec:
  selector:
    matchLabels:
      app: spire-agent
  template:
    metadata:
      labels:
        app: spire-agent
    spec:
      hostPID: true
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      serviceAccountName: spire-agent
      containers:
      - name: spire-agent
        image: ghcr.io/spiffe/spire-agent:1.8.5
        args:
        - -config
        - /run/spire/config/agent.conf
        volumeMounts:
        - name: spire-config
          mountPath: /run/spire/config
        - name: spire-agent-socket
          mountPath: /run/spire/sockets
        - name: k8s-certs
          mountPath: /var/run/secrets/kubernetes.io/serviceaccount
          readOnly: true
      volumes:
      - name: spire-config
        configMap:
          name: spire-agent
      - name: spire-agent-socket
        hostPath:
          path: /run/spire/sockets
          type: DirectoryOrCreate
      - name: k8s-certs
        hostPath:
          path: /var/run/secrets/kubernetes.io/serviceaccount
```

**Workload Registration (Automatic via Controller):**
```yaml
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterSPIFFEID
metadata:
  name: agent-sidecars
spec:
  spiffeIDTemplate: "spiffe://zta.io/ns/{{ .PodMeta.Namespace }}/sa/{{ .PodSpec.ServiceAccountName }}"
  podSelector:
    matchLabels:
      app: agent
      zta.io/sidecar: "true"
  workloadSelectorTemplates:
  - "k8s:ns:{{ .PodMeta.Namespace }}"
  - "k8s:sa:{{ .PodSpec.ServiceAccountName }}"
  - "k8s:pod-label:app:agent"
```

#### 7.8.4 Envoy SDS Configuration for Sidecar

**Envoy SDS Integration:**
```yaml
# Sidecar Envoy configuration for certificate fetching
static_resources:
  clusters:
  - name: spire_agent
    connect_timeout: 1s
    http2_protocol_options: {}
    load_assignment:
      cluster_name: spire_agent
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              pipe:
                path: /run/spire/sockets/agent.sock  # Unix socket to SPIRE agent

tls_certificates:
- name: "default"
  sds_config:
    resource_api_version: V3
    api_config_source:
      api_type: GRPC
      transport_api_version: V3
      grpc_services:
      - envoy_grpc:
          cluster_name: spire_agent
      set_node_on_first_message_only: true

validation_context:
  sds_config:
    resource_api_version: V3
    api_config_source:
      api_type: GRPC
      transport_api_version: V3
      grpc_services:
      - envoy_grpc:
          cluster_name: spire_agent
      set_node_on_first_message_only: true
```

**Sidecar Pod with SPIRE Agent Socket:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: agent-with-sidecar
  namespace: production-mas
  labels:
    app: agent
    zta.io/sidecar: "true"
spec:
  serviceAccountName: agent
  containers:
  - name: agent
    image: my-agent:v1.0.0
    # Agent talks to localhost:15001 (sidecar)

  - name: zta-sidecar
    image: envoyproxy/envoy:v1.28.0
    args:
    - -c
    - /etc/envoy/envoy.yaml
    volumeMounts:
    - name: envoy-config
      mountPath: /etc/envoy
    - name: spire-agent-socket
      mountPath: /run/spire/sockets
      readOnly: true
    env:
    - name: SPIFFE_ENDPOINT_SOCKET
      value: unix:///run/spire/sockets/agent.sock

  volumes:
  - name: envoy-config
    configMap:
      name: zta-sidecar-envoy-config
  - name: spire-agent-socket
    hostPath:
      path: /run/spire/sockets
      type: Directory
```

#### 7.8.5 Certificate Rotation and Renewal

**Rotation Strategy:**

| Certificate | Rotation Trigger | Rotation Process | Downtime |
|-------------|-----------------|------------------|----------|
| **Root CA** | Manual (key compromise or policy) | 1. Generate new root<br/>2. Cross-sign with old root<br/>3. Distribute trust bundle<br/>4. Phase out old root over 1 year | Zero (trust bundle includes both) |
| **Intermediate CA** | 1 year before expiry | 1. cert-manager auto-requests from root<br/>2. New intermediate issued<br/>3. Services continue using old until renewed | Zero (overlapping validity) |
| **Service Certificates** | 15 days before expiry | 1. cert-manager auto-renews<br/>2. Updates Secret<br/>3. Deployment watches Secret, rolls pods | ~30s per pod (rolling restart) |
| **Sidecar Certificates** | 50% of TTL (12h for 24h cert) | 1. SPIRE agent auto-fetches new cert<br/>2. Envoy SDS receives via gRPC<br/>3. Envoy hot-reloads TLS context | Zero (SDS hot-reload) |

**Certificate Renewal Monitoring:**
```yaml
# Prometheus alert for certificate expiry
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: certificate-expiry-alerts
  namespace: zta-control-plane
spec:
  groups:
  - name: certificates
    interval: 1m
    rules:
    - alert: CertificateExpiringSoon
      expr: |
        (certmanager_certificate_expiration_timestamp_seconds - time()) / 86400 < 15
      for: 1h
      labels:
        severity: warning
      annotations:
        summary: "Certificate {{ $labels.name }} expires in {{ $value }} days"
        description: "Certificate {{ $labels.name }} in namespace {{ $labels.namespace }} expires soon"

    - alert: CertificateExpired
      expr: |
        (certmanager_certificate_expiration_timestamp_seconds - time()) < 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Certificate {{ $labels.name }} has EXPIRED"
```

#### 7.8.6 Trust Bundle Distribution

**Trust Bundle ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: zta-ca-bundle
  namespace: zta-control-plane
data:
  ca-bundle.crt: |
    # Root CA Certificate
    -----BEGIN CERTIFICATE-----
    MIIDXTCCAkWgAwIBAgIJAKZ... (Root CA)
    -----END CERTIFICATE-----

    # Control Plane Intermediate CA
    -----BEGIN CERTIFICATE-----
    MIIDXTCCAkWgAwIBAgIJAKZ... (CP Intermediate)
    -----END CERTIFICATE-----

    # Data Plane Intermediate CA
    -----BEGIN CERTIFICATE-----
    MIIDXTCCAkWgAwIBAgIJAKZ... (DP Intermediate)
    -----END CERTIFICATE-----
```

**Trust Bundle Injector (Mutating Webhook):**
```go
// Inject CA bundle into all ZTA pods
func (w *TrustBundleInjector) Handle(ctx context.Context, req admission.Request) admission.Response {
    pod := &corev1.Pod{}
    err := w.decoder.Decode(req, pod)

    // Check if pod needs ZTA trust bundle
    if pod.Labels["zta.io/enabled"] != "true" {
        return admission.Allowed("")
    }

    // Add volume with CA bundle
    pod.Spec.Volumes = append(pod.Spec.Volumes, corev1.Volume{
        Name: "zta-ca-bundle",
        VolumeSource: corev1.VolumeSource{
            ConfigMap: &corev1.ConfigMapVolumeSource{
                Name: "zta-ca-bundle",
            },
        },
    })

    // Mount into all containers
    for i := range pod.Spec.Containers {
        pod.Spec.Containers[i].VolumeMounts = append(
            pod.Spec.Containers[i].VolumeMounts,
            corev1.VolumeMount{
                Name:      "zta-ca-bundle",
                MountPath: "/etc/ssl/certs/zta-ca-bundle.crt",
                SubPath:   "ca-bundle.crt",
                ReadOnly:  true,
            },
        )

        // Set environment variable for trust bundle location
        pod.Spec.Containers[i].Env = append(
            pod.Spec.Containers[i].Env,
            corev1.EnvVar{
                Name:  "SSL_CERT_FILE",
                Value: "/etc/ssl/certs/zta-ca-bundle.crt",
            },
        )
    }

    return admission.PatchResponseFromPod(&req, pod)
}
```

#### 7.8.7 Vault PKI Backend Configuration

**Vault PKI Setup:**
```bash
# Enable PKI secrets engine for root CA
vault secrets enable -path=pki pki
vault secrets tune -max-lease-ttl=87600h pki  # 10 years

# Generate root CA
vault write -field=certificate pki/root/generate/internal \
    common_name="ZTA Root CA" \
    ttl=87600h > /tmp/zta-root-ca.crt

# Configure CA and CRL URLs
vault write pki/config/urls \
    issuing_certificates="https://vault.vault.svc.cluster.local:8200/v1/pki/ca" \
    crl_distribution_points="https://vault.vault.svc.cluster.local:8200/v1/pki/crl"

# Enable intermediate PKI for control plane
vault secrets enable -path=pki/intermediate/control-plane pki
vault secrets tune -max-lease-ttl=43800h pki/intermediate/control-plane

# Generate intermediate CSR
vault write -format=json pki/intermediate/control-plane/intermediate/generate/internal \
    common_name="ZTA Control Plane Intermediate CA" \
    | jq -r '.data.csr' > /tmp/control-plane.csr

# Sign intermediate with root
vault write -format=json pki/root/sign-intermediate \
    csr=@/tmp/control-plane.csr \
    format=pem_bundle \
    ttl=43800h \
    | jq -r '.data.certificate' > /tmp/control-plane-signed.crt

# Set signed certificate
vault write pki/intermediate/control-plane/intermediate/set-signed \
    certificate=@/tmp/control-plane-signed.crt

# Create role for cert-manager
vault write pki/intermediate/control-plane/roles/zta-services \
    allowed_domains="zta-control-plane.svc.cluster.local" \
    allow_subdomains=true \
    max_ttl=2160h \
    key_type=rsa \
    key_bits=4096 \
    require_cn=true

# Kubernetes auth for cert-manager
vault auth enable kubernetes

vault write auth/kubernetes/config \
    kubernetes_host="https://kubernetes.default.svc.cluster.local" \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

vault write auth/kubernetes/role/cert-manager \
    bound_service_account_names=cert-manager \
    bound_service_account_namespaces=cert-manager \
    policies=cert-manager-policy \
    ttl=1h
```

**Vault Policy for cert-manager:**
```hcl
# Policy: cert-manager-policy
path "pki/intermediate/control-plane/sign/zta-services" {
  capabilities = ["create", "update"]
}

path "pki/intermediate/control-plane/issue/zta-services" {
  capabilities = ["create", "update"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}
```

#### 7.8.8 mTLS Verification in Sidecar

**Envoy TLS Inspection Configuration:**
```yaml
# Envoy listener with mTLS enforcement
static_resources:
  listeners:
  - name: inbound
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 15001
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: inbound
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route: { cluster: local_app }
          http_filters:
          - name: envoy.filters.http.lua
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
              inline_code: |
                function envoy_on_request(request_handle)
                  -- Extract client SPIFFE ID from mTLS certificate
                  local client_cert = request_handle:connection():ssl()
                  if client_cert == nil then
                    request_handle:respond({[":status"] = "401"}, "mTLS required")
                    return
                  end

                  local spiffe_id = client_cert:uriSanPeerCertificate()
                  if spiffe_id == nil or not string.match(spiffe_id, "^spiffe://zta.io/") then
                    request_handle:respond({[":status"] = "403"}, "Invalid SPIFFE ID")
                    return
                  end

                  -- Add SPIFFE ID to request headers for application
                  request_handle:headers():add("X-Spiffe-ID", spiffe_id)
                end
          - name: envoy.filters.http.router
      transport_socket:
        name: envoy.transport_sockets.tls
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
          require_client_certificate: true  # Enforce mTLS
          common_tls_context:
            tls_certificate_sds_secret_configs:
            - name: "default"
              sds_config:
                resource_api_version: V3
                api_config_source:
                  api_type: GRPC
                  grpc_services:
                  - envoy_grpc:
                      cluster_name: spire_agent
            validation_context_sds_secret_config:
              name: "spiffe://zta.io"
              sds_config:
                resource_api_version: V3
                api_config_source:
                  api_type: GRPC
                  grpc_services:
                  - envoy_grpc:
                      cluster_name: spire_agent

  clusters:
  - name: local_app
    connect_timeout: 0.25s
    type: STATIC
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: local_app
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: 127.0.0.1
                port_value: 8000  # Application port
```

---

## 8. Security & Threat Model

### 8.1 Threat Model

#### 8.1.1 Threat Actors

| Actor | Trust Level | Capabilities | Motivation |
|-------|-------------|--------------|------------|
| Compromised Agent | Untrusted | Execute arbitrary code in agent pod, send network requests | Exfiltrate user data, access unauthorized tools, abuse LLM quota |
| Malicious MCP Server | Semi-trusted | Provide malicious tools, log token values | Steal tokens, execute code on agent, data exfiltration |
| External Attacker | Untrusted | Network access outside cluster | DDoS, credential stuffing, API abuse |
| Insider Threat | Trusted (Operator) | Kubernetes admin access | Data theft, service disruption |

#### 8.1.2 Threat Scenarios

**Threat 1: Token Exfiltration**
- **Attack**: Compromised agent extracts JWT token from memory, sends to external endpoint
- **Impact**: Attacker gains access to tools with stolen token
- **Mitigation**:
  - eBPF blocks egress to non-allowed endpoints (only LLM allowed)
  - Sidecar strips Authorization header from non-control-plane requests
  - Token has short TTL (5min)
  - Telemetry alerts on token reuse from different source IP

**Threat 2: LLM Misuse (Tool Check Bypass)**
- **Attack**: Agent directly calls LLM without going through auth server, claims LLM selected a tool
- **Impact**: Agent bypasses tool intent checks
- **Mitigation**:
  - LLM calls traced via telemetry (agent must log LLM request/response)
  - Deterministic check: Verify tool was in LLM's response (stored in telemetry)
  - AI check: Validate tool matches user's original prompt
  - If no LLM trace found, token exchange is denied

**Threat 3: Lateral Movement**
- **Attack**: Compromised agent pod tries to connect to other agents or MCP servers
- **Impact**: Spread malware, exfiltrate data from other workloads
- **Mitigation**:
  - CiliumNetworkPolicy enforces deny-by-default
  - Agent can only reach allowed MCP servers (explicit allow-list)
  - Agent-to-agent communication only via A2A protocol (L7 sidecar enforcement)
  - Hubble detects anomalous connection attempts

**Threat 4: MCP Server Impersonation**
- **Attack**: Attacker deploys fake MCP server, advertises malicious tools
- **Impact**: Agent executes malicious code, data theft
- **Mitigation**:
  - MCP servers must be registered in Policy Service
  - Discovery Service only queries registered servers
  - mTLS between sidecar and MCP server
  - Tool schemas validated against expected signature

**Threat 5: Control Plane Compromise**
- **Attack**: Attacker gains access to ZTA Auth Service, issues arbitrary tokens
- **Impact**: Complete system compromise
- **Mitigation**:
  - Control plane isolated in separate namespace
  - Network policies restrict ingress to control plane (only from MAS namespaces)
  - Secrets encrypted at rest (KMS)
  - Audit logging of all token operations
  - Keycloak separated from ZTA (separate secret store)

**Threat 6: Token Replay**
- **Attack**: Attacker captures valid token, replays it from different location
- **Impact**: Unauthorized tool access
- **Mitigation**:
  - Tokens include nonce (single-use for token exchange)
  - Telemetry correlates token usage with source pod identity
  - Short TTL (5min) limits replay window
  - Cilium identity validation (token must originate from expected pod)

**Threat 7: AI Pipeline Poisoning**
- **Attack**: Attacker manipulates embeddings or LLM responses to bypass tool checks
- **Impact**: Inappropriate tools approved
- **Mitigation**:
  - Embeddings cached with integrity check (HMAC)
  - LLM verifier uses deterministic temperature (0.0)
  - Multiple checks required (deterministic + AI)
  - Audit trail of all AI decisions
  - Periodic evaluation of AI matcher accuracy

### 8.2 Security Controls Summary

| Control | Layer | Enforcement Point | Fail Mode |
|---------|-------|-------------------|-----------|
| Deny-by-default networking | L3/L4 | eBPF (Cilium) | Fail-closed |
| Protocol enforcement (MCP/A2A only) | L7 | Sidecar | Fail-closed |
| Token validation | L7 | Sidecar + Control Plane | Fail-closed |
| Tool authorization | Application | Control Plane | Fail-closed |
| LLM endpoint restriction | L3/L4 | eBPF (FQDN policy) | Fail-closed |
| Token exfiltration prevention | L3/L4 | eBPF (egress block) | Fail-closed |
| Audit logging | Application | All components | N/A (telemetry) |
| mTLS between sidecars | L7 | Sidecar | Fail-closed |

### 8.3 Audit Strategy

**What is Logged:**
1. **Token Lifecycle Events**
   - Token issued (app_id, user_input_id, timestamp)
   - Token exchanged (subject_token, actor_token, requested_tools, blocking_reasons)
   - Token introspected (token_id, mcp_server_id, result)

2. **Network Events**
   - All flows (src_pod, dst_pod, protocol, verdict) via Hubble
   - Denied flows (policy name, blocking reason)

3. **Tool Operations**
   - Tool check results (check_type, satisfied, reason)
   - MCP tool invocations (tool_name, args, result)
   - AI pipeline decisions (matcher_type, similarity_score, llm_verdict)

4. **LLM Calls**
   - LLM requests (prompt, model, timestamp)
   - LLM responses (tool selections, completion text)
   - Token usage (input_tokens, output_tokens, cost)

**Log Retention:**
- Hot storage (PostgreSQL): 30 days
- Cold storage (S3/GCS): 1 year
- Compliance: 7 years (encrypted archives)

**Log Analysis:**
- Anomaly detection: Unusual tool request patterns
- Correlation: Link user input → LLM calls → tool invocations
- Forensics: Reconstruct full attack chain from logs

**Audit Dashboard (Grafana):**
- Token issuance rate per MAS
- Tool check failure reasons (top 10)
- Network policy denials (timeline)
- AI pipeline latency and accuracy

---

### 8.4 Security Hardening

This section provides comprehensive security hardening configurations including Pod Security Standards, admission control policies (OPA/Gatekeeper), runtime security (Falco), vulnerability scanning, and security best practices.

#### 8.4.1 Pod Security Standards

**PSS Enforcement Strategy:**

Kubernetes Pod Security Standards (PSS) replace deprecated Pod Security Policies (PSP). The ZTA-MAS system uses a tiered approach:

| Namespace | PSS Level | Enforcement | Justification |
|-----------|-----------|-------------|---------------|
| zta-control-plane | Restricted | Enforce | High-value targets, no privileged access needed |
| production-mas | Restricted | Enforce | Untrusted workloads (agents, apps) must be isolated |
| dev-mas | Baseline | Warn | Development flexibility with warnings |
| kube-system | Privileged | Audit | System components may need host access |
| cilium | Privileged | Audit | eBPF requires privileged containers |
| monitoring | Baseline | Enforce | Observability tools, minimal privileges |

**PSS Label Application:**

```yaml
# zta-control-plane namespace with Restricted PSS
apiVersion: v1
kind: Namespace
metadata:
  name: zta-control-plane
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.27
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: v1.27
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: v1.27
```

**Restricted PSS Requirements:**

All pods in `zta-control-plane` and `production-mas` must:

1. **No Privileged Containers:**
   ```yaml
   securityContext:
     privileged: false
   ```

2. **Run as Non-Root:**
   ```yaml
   securityContext:
     runAsNonRoot: true
     runAsUser: 1000
   ```

3. **Drop All Capabilities:**
   ```yaml
   securityContext:
     capabilities:
       drop:
       - ALL
   ```

4. **Read-Only Root Filesystem:**
   ```yaml
   securityContext:
     readOnlyRootFilesystem: true
   volumeMounts:
   - name: tmp
     mountPath: /tmp
   volumes:
   - name: tmp
     emptyDir: {}
   ```

5. **No Host Namespaces:**
   ```yaml
   hostNetwork: false
   hostPID: false
   hostIPC: false
   ```

6. **Seccomp Profile:**
   ```yaml
   securityContext:
     seccompProfile:
       type: RuntimeDefault
   ```

**Example Restricted Pod (Auth Service):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
spec:
  template:
    spec:
      serviceAccountName: zta-auth-service
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault

      containers:
      - name: auth-service
        image: ghcr.io/your-org/zta-auth-service:v1.0.0
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL

        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache

        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi

      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
```

#### 8.4.2 OPA Gatekeeper Policies

**Gatekeeper Installation:**

```bash
# Install Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml

# Verify installation
kubectl get pods -n gatekeeper-system
```

**Custom Constraint Templates:**

**1. Block Privileged Containers:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sblockprivileged
spec:
  crd:
    spec:
      names:
        kind: K8sBlockPrivileged
      validation:
        openAPIV3Schema:
          type: object
          properties:
            exemptions:
              type: array
              items:
                type: string
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8sblockprivileged

      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        container.securityContext.privileged
        not exempt(input.review.object.metadata.name)
        msg := sprintf("Privileged container %v is not allowed", [container.name])
      }

      exempt(name) {
        exemption := input.parameters.exemptions[_]
        name == exemption
      }
```

**Constraint:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sBlockPrivileged
metadata:
  name: block-privileged-containers
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
    excludedNamespaces:
    - kube-system
    - cilium
  parameters:
    exemptions: []
```

**2. Require Resource Limits:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequireresourcelimits
spec:
  crd:
    spec:
      names:
        kind: K8sRequireResourceLimits
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequireresourcelimits

      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.resources.limits.cpu
        msg := sprintf("Container %v must have CPU limit", [container.name])
      }

      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.resources.limits.memory
        msg := sprintf("Container %v must have memory limit", [container.name])
      }
```

**Constraint:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequireResourceLimits
metadata:
  name: require-resource-limits
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
    namespaces:
    - zta-control-plane
    - production-mas
```

**3. Enforce Image Registry:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sallowedrepos
spec:
  crd:
    spec:
      names:
        kind: K8sAllowedRepos
      validation:
        openAPIV3Schema:
          type: object
          properties:
            repos:
              type: array
              items:
                type: string
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8sallowedrepos

      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not startswith(container.image, input.parameters.repos[_])
        msg := sprintf("Container %v uses disallowed image: %v", [container.name, container.image])
      }
```

**Constraint:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAllowedRepos
metadata:
  name: allowed-image-repos
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
  parameters:
    repos:
    - "ghcr.io/your-org/"
    - "quay.io/your-org/"
    - "docker.io/library/"  # Official images only
```

**4. Block Latest Tag:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sblocklatesttag
spec:
  crd:
    spec:
      names:
        kind: K8sBlockLatestTag
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8sblocklatesttag

      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        endswith(container.image, ":latest")
        msg := sprintf("Container %v uses :latest tag, which is not allowed", [container.name])
      }

      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not contains(container.image, ":")
        msg := sprintf("Container %v has no tag specified (implicit :latest)", [container.name])
      }
```

**Constraint:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sBlockLatestTag
metadata:
  name: block-latest-tag
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
    namespaces:
    - zta-control-plane
    - production-mas
```

**5. Require ZTA Sidecar Annotation:**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequireztasidecar
spec:
  crd:
    spec:
      names:
        kind: K8sRequireZTASidecar
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequireztasidecar

      violation[{"msg": msg}] {
        input.review.object.kind == "Pod"
        input.review.object.metadata.namespace == "production-mas"
        not input.review.object.metadata.labels["zta.io/enabled"]
        msg := "Pods in production-mas must have zta.io/enabled label"
      }
```

**Gatekeeper Dashboard (Prometheus Metrics):**

```yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: gatekeeper
  namespace: gatekeeper-system
spec:
  selector:
    matchLabels:
      gatekeeper.sh/system: "yes"
  endpoints:
  - port: metrics
    interval: 30s
```

**Gatekeeper Alerts:**

```yaml
- alert: GatekeeperViolations
  expr: increase(gatekeeper_violations_total[5m]) > 10
  for: 5m
  annotations:
    summary: "High rate of Gatekeeper policy violations"
    description: "{{ $value }} violations in the last 5 minutes"
```

#### 8.4.3 Falco Runtime Security

**Falco Installation:**

```yaml
# Install Falco with Helm
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  --set driver.kind=ebpf \
  --set falco.grpc.enabled=true \
  --set falco.grpc_output.enabled=true \
  --set falcoctl.artifact.install.enabled=true \
  --set falcoctl.artifact.follow.enabled=true
```

**Custom Falco Rules (ZTA-specific):**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-rules-zta
  namespace: falco
data:
  zta_rules.yaml: |
    # Detect token exfiltration attempts
    - rule: Token Exfiltration Attempt
      desc: Detect attempts to send tokens to external endpoints
      condition: >
        (proc.name in (curl, wget, nc, ncat)) and
        (fd.name glob "*Authorization*" or fd.name glob "*Bearer*") and
        not fd.net in (zta-auth-service.zta-control-plane.svc.cluster.local, api.openai.com)
      output: >
        Token exfiltration attempt detected
        (user=%user.name command=%proc.cmdline container=%container.name
        image=%container.image.repository dest=%fd.name)
      priority: CRITICAL
      tags: [zta, token_exfiltration, network]

    # Detect privilege escalation
    - rule: Privilege Escalation in ZTA Namespace
      desc: Detect privilege escalation attempts in ZTA namespaces
      condition: >
        spawned_process and
        (container.ns in (zta-control-plane, production-mas)) and
        (proc.name in (sudo, su, setuid, chmod, chown))
      output: >
        Privilege escalation attempt
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: CRITICAL
      tags: [zta, privilege_escalation]

    # Detect unauthorized file writes
    - rule: Write to Sensitive Directory
      desc: Detect writes to sensitive directories
      condition: >
        open_write and
        container.ns = production-mas and
        (fd.name startswith /etc or fd.name startswith /root or fd.name startswith /bin or fd.name startswith /usr/bin)
      output: >
        Unauthorized file write to sensitive directory
        (user=%user.name file=%fd.name container=%container.name command=%proc.cmdline)
      priority: WARNING
      tags: [zta, filesystem, integrity]

    # Detect unexpected network connections
    - rule: Unexpected Outbound Connection
      desc: Detect outbound connections to non-whitelisted endpoints
      condition: >
        outbound and
        container.ns = production-mas and
        not fd.sip in (zta-auth-service, zta-policy-service, api.openai.com) and
        not fd.sport in (443, 8443)
      output: >
        Unexpected outbound connection
        (container=%container.name dest_ip=%fd.sip dest_port=%fd.sport command=%proc.cmdline)
      priority: WARNING
      tags: [zta, network, lateral_movement]

    # Detect container escape attempts
    - rule: Container Escape Attempt
      desc: Detect attempts to escape container isolation
      condition: >
        spawned_process and
        container and
        proc.name in (nsenter, unshare, capsh) or
        (proc.cmdline contains "mount" and proc.cmdline contains "/proc")
      output: >
        Container escape attempt detected
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: CRITICAL
      tags: [zta, container_escape, breakout]

    # Detect crypto mining
    - rule: Crypto Mining Activity
      desc: Detect cryptocurrency mining processes
      condition: >
        spawned_process and
        (proc.name in (xmrig, ethminer, cgminer, minerd) or
         proc.cmdline contains "stratum+tcp" or
         proc.cmdline contains "pool.minexmr.com")
      output: >
        Crypto mining activity detected
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: CRITICAL
      tags: [zta, cryptomining, malware]
```

**Falco Alert Integration (Slack):**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-config
  namespace: falco
data:
  falco.yaml: |
    json_output: true
    json_include_output_property: true
    http_output:
      enabled: true
      url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

    rules_file:
    - /etc/falco/falco_rules.yaml
    - /etc/falco/zta_rules.yaml

    priority: WARNING
    buffered_outputs: true
```

**Falco Sidekick for Multi-Channel Alerts:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: falco-sidekick
  namespace: falco
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: falco-sidekick
        image: falcosecurity/falco-sidekick:latest
        env:
        - name: SLACK_WEBHOOKURL
          valueFrom:
            secretKeyRef:
              name: falco-sidekick-secrets
              key: slack-webhook
        - name: PAGERDUTY_ROUTINGKEY
          valueFrom:
            secretKeyRef:
              name: falco-sidekick-secrets
              key: pagerduty-key
        - name: ELASTICSEARCH_HOSTPORT
          value: "elasticsearch.monitoring.svc.cluster.local:9200"
```

#### 8.4.4 Image Vulnerability Scanning

**Trivy Integration (CI/CD):**

```yaml
# .github/workflows/image-scan.yml
name: Image Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build image
      run: docker build -t zta-auth-service:${{ github.sha }} .

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'zta-auth-service:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH'
        exit-code: '1'  # Fail on critical/high vulnerabilities

    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

    - name: Trivy HTML Report
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'zta-auth-service:${{ github.sha }}'
        format: 'template'
        template: '@/contrib/html.tpl'
        output: 'trivy-report.html'

    - name: Upload report
      uses: actions/upload-artifact@v3
      with:
        name: trivy-report
        path: trivy-report.html
```

**Trivy Operator (Runtime Scanning):**

```yaml
# Install Trivy Operator
helm repo add aqua https://aquasecurity.github.io/helm-charts/
helm install trivy-operator aqua/trivy-operator \
  --namespace trivy-system \
  --create-namespace \
  --set="trivy.ignoreUnfixed=true"

# Trivy scans all running images and creates VulnerabilityReport CRDs
```

**Vulnerability Report Monitoring:**

```bash
# Get vulnerability reports
kubectl get vulnerabilityreports -n zta-control-plane

# Get detailed report
kubectl get vulnerabilityreport -n zta-control-plane \
  deployment-zta-auth-service-zta-auth-service -o yaml

# Example output:
# report:
#   summary:
#     criticalCount: 0
#     highCount: 2
#     mediumCount: 5
#     lowCount: 10
```

**Alert on Critical Vulnerabilities:**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: trivy-vulnerabilities
  namespace: monitoring
spec:
  groups:
  - name: trivy
    rules:
    - alert: CriticalVulnerabilitiesDetected
      expr: |
        trivy_image_vulnerabilities{severity="CRITICAL"} > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Critical vulnerabilities detected in {{ $labels.image_repository }}"
        description: "{{ $value }} critical vulnerabilities found"
```

#### 8.4.5 Network Policies (Defense in Depth)

**Additional Network Policies Beyond Cilium:**

**1. Deny All Egress by Default:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
  namespace: production-mas
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress: []  # Deny all by default
```

**2. Allow DNS Only:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production-mas
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

**3. Isolate Control Plane:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: control-plane-isolation
  namespace: zta-control-plane
spec:
  podSelector:
    matchLabels:
      tier: control-plane
  policyTypes:
  - Ingress
  ingress:
  # Only allow from MAS namespaces with ZTA sidecar
  - from:
    - namespaceSelector:
        matchLabels:
          zta.io/mas: "true"
    - podSelector:
        matchLabels:
          zta.io/enabled: "true"
    ports:
    - protocol: TCP
      port: 8443

  # Allow metrics scraping from Prometheus
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    - podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 9090
```

#### 8.4.6 Secrets Management Security

**Sealed Secrets for GitOps:**

```bash
# Install Sealed Secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Seal a secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Sealed secret can be committed to Git
git add sealed-secret.yaml
```

**External Secrets Operator Hardening:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: zta-control-plane
spec:
  provider:
    vault:
      server: "https://vault.vault.svc.cluster.local:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "zta-auth-service"
          serviceAccountRef:
            name: "zta-auth-service"
      # TLS verification
      caBundle: <base64-encoded-ca-cert>
      # Namespace restriction
      namespace: "zta-control-plane"
```

**Rotate Secrets Automatically:**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: rotate-db-credentials
  namespace: zta-control-plane
spec:
  schedule: "0 0 * * 0"  # Weekly
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: secret-rotator
          containers:
          - name: rotator
            image: vault:1.15.4
            command:
            - /bin/sh
            - -c
            - |
              # Generate new credentials in Vault
              vault write database/rotate-role/zta-db-role

              # Restart deployments to pick up new credentials
              kubectl rollout restart deployment/zta-auth-service -n zta-control-plane
              kubectl rollout restart deployment/zta-policy-service -n zta-control-plane
```

#### 8.4.7 RBAC Hardening

**Principle of Least Privilege:**

```yaml
# Auth Service ServiceAccount with minimal permissions
apiVersion: v1
kind: ServiceAccount
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
rules:
# Read-only access to ConfigMaps
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
  resourceNames: ["zta-auth-config"]

# Read-only access to Secrets
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["zta-db-credentials", "openai-api-key"]

# No pod exec, no secrets create/delete
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
subjects:
- kind: ServiceAccount
  name: zta-auth-service
roleRef:
  kind: Role
  name: zta-auth-service
  apiGroup: rbac.authorization.k8s.io
```

**Audit RBAC Permissions:**

```bash
# List all RBAC permissions for a ServiceAccount
kubectl auth can-i --list --as=system:serviceaccount:zta-control-plane:zta-auth-service

# Check specific permission
kubectl auth can-i delete secrets --as=system:serviceaccount:zta-control-plane:zta-auth-service
# Expected: no
```

#### 8.4.8 Security Scanning Summary

**Security Toolchain:**

| Tool | Purpose | Frequency | Alert Threshold |
|------|---------|-----------|-----------------|
| Trivy | Container image vulnerabilities | Every build + daily runtime scan | Critical: Block deploy, High: Alert |
| Gatekeeper | Policy enforcement (admission control) | Real-time | Any violation triggers alert |
| Falco | Runtime security (behavioral analysis) | Real-time | Priority >= WARNING |
| Kube-bench | CIS Kubernetes benchmark | Weekly | Score < 90% |
| Kube-hunter | Penetration testing | Monthly | Any finding |
| Snyk | Dependency vulnerabilities | Every commit | Critical: Block merge |

**Security Dashboard (Grafana):**

```yaml
# Security metrics to track
- Gatekeeper violations (last 24h)
- Falco critical alerts (last 7 days)
- Container images with critical CVEs
- Pods without resource limits
- Pods running as root
- Services without NetworkPolicy
- Secrets not encrypted at rest
- RBAC over-privileged accounts
```

---



## 9. Operational Model

### 9.1 Failure Modes

| Component | Failure Scenario | Impact | Recovery | Degradation Strategy |
|-----------|------------------|--------|----------|---------------------|
| **Auth Service** | Crash/OOM | No new tokens issued | Auto-restart, fallback to replicas | Sidecars use cached tokens (TTL 30s) |
| **Policy Service** | Crash | Cannot query app metadata | Auto-restart | Auth Service uses stale cache (Redis) |
| **AI Pipeline Service** | High latency (>5s) | Token exchange timeouts | Scale up replicas | Fallback to deterministic checks only |
| **Telemetry Service** | Event queue full | Dropped events | Scale up, flush to disk | Non-blocking (async), alert on backlog |
| **Sidecar** | Crash | Pod loses network connectivity | Kubelet restarts sidecar | Fail-closed (all traffic blocked) |
| **eBPF (Cilium)** | Agent crash on node | Network policies not enforced | Kubernetes reschedules pods | Fail-closed (kernel rejects packets) |
| **Keycloak** | Database connection lost | Token generation fails | Reconnect, use connection pool | Return 503, clients retry |
| **PostgreSQL** | Primary down | All writes fail | Promote replica to primary | Read-only mode (introspection still works) |
| **Redis** | Cache miss storm | High latency on control plane | Backpressure, rate limiting | Direct database queries (slower) |
| **External LLM** | API rate limit | AI checks fail | Exponential backoff | Fallback to embeddings only |

### 9.2 Capacity Planning

**Control Plane Scaling:**
- **Auth Service**: 500 tokens/sec per replica → 5 replicas = 2500 tokens/sec
- **AI Pipeline**: 50 matches/sec per replica (LLM bottleneck) → 10 replicas = 500 matches/sec
- **Telemetry**: 10k events/sec per replica → 5 replicas = 50k events/sec
- **PostgreSQL**: 10k writes/sec (with connection pooling)

**Sidecar Overhead:**
- CPU: 100m baseline + 10m per 100 req/sec
- Memory: 128Mi baseline + 1Mi per 1000 cached tokens
- Network: +50ms P95 latency (token introspection)

**Cluster Sizing (1000 pods):**
- Nodes: 20x 8-core machines (m5.2xlarge)
- Control plane: 3 dedicated nodes (c5.4xlarge)
- PostgreSQL: 2 dedicated nodes (r5.2xlarge, 64GB RAM)
- Cilium: DaemonSet on all nodes (minimal overhead)

### 9.3 Runbooks

#### Runbook 1: High Token Exchange Latency

**Symptoms:**
- P95 latency > 2s for `/oauth/token/exchange`
- Alert: `token_exchange_latency_p95 > 2000`

**Diagnosis:**
1. Check AI Pipeline Service latency:
   ```bash
   kubectl logs -n zta-control-plane deployment/zta-ai-pipeline-service | grep "matcher_latency"
   ```
2. Check external LLM API status (OpenAI status page)
3. Check PostgreSQL connection pool exhaustion:
   ```bash
   kubectl exec -n zta-control-plane statefulset/postgresql -- psql -c "SELECT count(*) FROM pg_stat_activity;"
   ```

**Remediation:**
1. Scale up AI Pipeline replicas:
   ```bash
   kubectl scale deployment/zta-ai-pipeline-service -n zta-control-plane --replicas=20
   ```
2. Increase cache TTL for embeddings:
   ```bash
   kubectl set env deployment/zta-ai-pipeline-service -n zta-control-plane EMBEDDING_CACHE_TTL=3600
   ```
3. Fallback to embeddings-only matcher:
   ```bash
   kubectl set env deployment/zta-ai-pipeline-service -n zta-control-plane MATCHER_TYPE=embeddings
   ```

#### Runbook 2: Sidecar Not Injecting

**Symptoms:**
- New pods missing `zta-sidecar` container
- Traffic blocked by network policies

**Diagnosis:**
1. Check mutating webhook status:
   ```bash
   kubectl get mutatingwebhookconfigurations zta-sidecar-injector -o yaml
   ```
2. Check webhook pod logs:
   ```bash
   kubectl logs -n zta-control-plane deployment/zta-sidecar-webhook
   ```
3. Verify pod has annotation:
   ```bash
   kubectl get pod <pod-name> -n production-mas -o jsonpath='{.metadata.annotations}'
   ```

**Remediation:**
1. Restart webhook:
   ```bash
   kubectl rollout restart deployment/zta-sidecar-webhook -n zta-control-plane
   ```
2. Manually patch pod (workaround):
   ```bash
   kubectl patch deployment <deployment-name> -n production-mas --type=json \
     -p='[{"op": "add", "path": "/spec/template/metadata/annotations/zta.io~1inject-sidecar", "value": "true"}]'
   ```

#### Runbook 3: Network Policy Blocking Legitimate Traffic

**Symptoms:**
- Agent cannot reach MCP server
- Hubble shows `POLICY_DENIED` verdicts

**Diagnosis:**
1. Check Hubble flows:
   ```bash
   hubble observe --namespace production-mas --verdict DROPPED
   ```
2. Inspect CiliumNetworkPolicy:
   ```bash
   kubectl get ciliumnetworkpolicy -n production-mas agent-to-mcp -o yaml
   ```
3. Verify pod labels:
   ```bash
   kubectl get pods -n production-mas --show-labels
   ```

**Remediation:**
1. Temporarily allow all (debugging only):
   ```bash
   kubectl delete ciliumnetworkpolicy -n production-mas default-deny-all
   ```
2. Update policy to include missing endpoint:
   ```yaml
   # Add to egress rules
   - toEndpoints:
     - matchLabels:
         app: new-mcp-server
   ```
3. Apply updated policy:
   ```bash
   kubectl apply -f updated-policy.yaml
   ```

### 9.4 Monitoring Dashboards

**Dashboard 1: ZTA Overview**
- Token issuance rate (gauge)
- Token exchange success rate (%)
- Tool check pass/fail ratio (stacked bar)
- AI pipeline latency (heatmap)
- Control plane resource usage (CPU, memory)

**Dashboard 2: Network Security**
- CiliumNetworkPolicy verdicts (allowed vs denied)
- Top denied flows (source → destination)
- Service map (Hubble topology)
- Token exfiltration attempts (alert panel)

**Dashboard 3: Agent Health**
- Pods with sidecars (count)
- Sidecar cache hit ratio (%)
- MCP tool invocation success rate (%)
- LLM API latency (P50, P95, P99)

---

## 9.5 Protocol Enforcement Details

### 9.5.1 MCP Protocol Enforcement in Sidecar

**MCP Protocol Structure:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "filesystem_read",
    "arguments": {
      "path": "/etc/passwd"
    }
  },
  "id": 1
}
```

**Sidecar Validation Logic:**

```python
class MCPProtocolValidator:
    def validate_request(self, http_request: HTTPRequest) -> ValidationResult:
        # 1. Check HTTP method
        if http_request.method != "POST":
            return ValidationResult(valid=False, reason="MCP requires POST")

        # 2. Check path prefix
        if not http_request.path.startswith("/mcp"):
            return ValidationResult(valid=False, reason="Invalid MCP path")

        # 3. Check Content-Type
        content_type = http_request.headers.get("Content-Type")
        if content_type != "application/json":
            return ValidationResult(valid=False, reason="MCP requires JSON")

        # 4. Parse body as JSON-RPC
        try:
            body = json.loads(http_request.body)
        except json.JSONDecodeError:
            return ValidationResult(valid=False, reason="Invalid JSON")

        # 5. Validate JSON-RPC structure
        if body.get("jsonrpc") != "2.0":
            return ValidationResult(valid=False, reason="Not JSON-RPC 2.0")

        if "method" not in body:
            return ValidationResult(valid=False, reason="Missing method")

        # 6. Check MCP method whitelist
        allowed_methods = [
            "initialize",
            "tools/list",
            "tools/call",
            "resources/list",
            "resources/read",
            "prompts/list",
            "prompts/get"
        ]
        if body["method"] not in allowed_methods:
            return ValidationResult(valid=False, reason=f"Method {body['method']} not allowed")

        # 7. Extract and validate token
        auth_header = http_request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return ValidationResult(valid=False, reason="Missing or invalid Authorization header")

        token = auth_header[7:]  # Strip "Bearer "
        token_valid = self.validate_token(token, required_tool=body["params"].get("name"))
        if not token_valid:
            return ValidationResult(valid=False, reason="Token invalid or tool not authorized")

        return ValidationResult(valid=True)

    def validate_token(self, token: str, required_tool: str) -> bool:
        # Call ZTA control plane for introspection
        response = requests.post(
            f"{self.control_plane_url}/oauth/introspect",
            json={"token": token, "requested_tool": required_tool},
            timeout=1.0
        )
        return response.json().get("active", False)
```

**Sidecar Configuration (Envoy Filter):**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: mcp-protocol-filter
  namespace: production-mas
spec:
  workloadSelector:
    labels:
      zta.io/enabled: "true"
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_OUTBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.lua
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
          inline_code: |
            function envoy_on_request(request_handle)
              local path = request_handle:headers():get(":path")
              local method = request_handle:headers():get(":method")
              local content_type = request_handle:headers():get("content-type")

              -- Only enforce on MCP paths
              if string.sub(path, 1, 4) == "/mcp" then
                -- Check HTTP method
                if method ~= "POST" then
                  request_handle:respond(
                    {[":status"] = "405"},
                    "MCP requires POST method"
                  )
                  return
                end

                -- Check Content-Type
                if content_type ~= "application/json" then
                  request_handle:respond(
                    {[":status"] = "415"},
                    "MCP requires application/json"
                  )
                  return
                end

                -- Parse JSON body (simplified)
                local body = request_handle:body():getBytes(0, request_handle:body():length())
                local success, json = pcall(cjson.decode, body)
                if not success then
                  request_handle:respond(
                    {[":status"] = "400"},
                    "Invalid JSON body"
                  )
                  return
                end

                -- Validate JSON-RPC
                if json.jsonrpc ~= "2.0" or not json.method then
                  request_handle:respond(
                    {[":status"] = "400"},
                    "Invalid JSON-RPC 2.0 structure"
                  )
                  return
                end
              end
            end
```

### 9.5.2 A2A Protocol Enforcement in Sidecar

**A2A Protocol Assumptions:**
- Agent-to-Agent communication uses a structured message format
- Messages contain sender identity, recipient identity, and message payload
- Authentication via JWT tokens

**A2A Message Format:**
```json
{
  "protocol": "a2a",
  "version": "1.0",
  "from": "agent-orchestrator",
  "to": "agent-worker-123",
  "message_type": "task_assignment",
  "payload": {
    "task_id": "abc-123",
    "action": "summarize_document",
    "parameters": {}
  },
  "timestamp": "2025-01-15T10:30:00Z",
  "signature": "..."
}
```

**Sidecar A2A Validator:**

```python
class A2AProtocolValidator:
    def validate_request(self, http_request: HTTPRequest) -> ValidationResult:
        # 1. Check A2A path
        if not http_request.path.startswith("/a2a"):
            return ValidationResult(valid=False, reason="Not A2A protocol")

        # 2. Parse message
        try:
            message = json.loads(http_request.body)
        except json.JSONDecodeError:
            return ValidationResult(valid=False, reason="Invalid JSON")

        # 3. Validate protocol field
        if message.get("protocol") != "a2a":
            return ValidationResult(valid=False, reason="Missing or invalid protocol field")

        # 4. Validate required fields
        required_fields = ["from", "to", "message_type", "payload", "timestamp"]
        for field in required_fields:
            if field not in message:
                return ValidationResult(valid=False, reason=f"Missing required field: {field}")

        # 5. Validate sender identity matches token
        auth_header = http_request.headers.get("Authorization")
        if not auth_header:
            return ValidationResult(valid=False, reason="Missing Authorization header")

        token = auth_header.replace("Bearer ", "")
        token_claims = self.decode_jwt(token)

        if token_claims.get("sub") != message["from"]:
            return ValidationResult(valid=False, reason="Sender identity mismatch")

        # 6. Check recipient is registered agent
        if not self.is_registered_agent(message["to"]):
            return ValidationResult(valid=False, reason="Recipient not registered")

        # 7. Verify message signature
        if not self.verify_signature(message):
            return ValidationResult(valid=False, reason="Invalid message signature")

        return ValidationResult(valid=True)

    def verify_signature(self, message: dict) -> bool:
        # Extract signature
        signature = message.pop("signature", None)
        if not signature:
            return False

        # Reconstruct canonical message
        canonical = json.dumps(message, sort_keys=True)

        # Verify with sender's public key
        sender_pubkey = self.get_agent_pubkey(message["from"])
        return crypto.verify_signature(canonical, signature, sender_pubkey)
```

**Network Policy for A2A:**
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: agent-to-agent-a2a
  namespace: production-mas
spec:
  endpointSelector:
    matchLabels:
      app.type: agent
      zta.io/enabled: "true"
  egress:
  - toEndpoints:
    - matchLabels:
        app.type: agent  # Agents can reach other agents
        zta.io/enabled: "true"
    toPorts:
    - ports:
      - port: "8000"
        protocol: TCP
      rules:
        http:
        - method: "POST"
          path: "/a2a/*"  # Only A2A protocol allowed
```

### 9.5.3 Protocol Violation Handling

**Response to Violations:**

| Violation Type | HTTP Status | Action | Alert |
|----------------|-------------|--------|-------|
| Non-POST to MCP | 405 Method Not Allowed | Block request | Log warning |
| Invalid JSON-RPC | 400 Bad Request | Block request | Log warning |
| Unknown MCP method | 403 Forbidden | Block request | Alert security team |
| Missing token | 401 Unauthorized | Block request | Log info |
| Invalid token | 403 Forbidden | Block request | Alert if repeated |
| A2A sender mismatch | 403 Forbidden | Block request | CRITICAL alert |
| Invalid signature | 403 Forbidden | Block request | CRITICAL alert |
| Wrong protocol path | 404 Not Found | Block request | Log warning |

**Telemetry Event on Violation:**
```json
{
  "event_type": "protocol_violation",
  "timestamp": "2025-01-15T10:30:00Z",
  "source_pod": "agent-abc-123",
  "destination_pod": "mcp-server-xyz",
  "violation_type": "invalid_mcp_method",
  "attempted_method": "tools/delete",
  "http_status": 403,
  "action": "blocked",
  "severity": "medium"
}
```

### 9.5.4 Protocol Enforcement Testing

**Integration Test Suite:**

```python
class TestProtocolEnforcement:
    def test_mcp_valid_request(self):
        # Valid MCP request should succeed
        response = sidecar.handle_request({
            "method": "POST",
            "path": "/mcp/tools/call",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer valid-token"
            },
            "body": json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "read_file"},
                "id": 1
            })
        })
        assert response.status == 200

    def test_mcp_wrong_method(self):
        # GET to MCP endpoint should be blocked
        response = sidecar.handle_request({
            "method": "GET",
            "path": "/mcp/tools/call",
            "headers": {"Authorization": "Bearer valid-token"}
        })
        assert response.status == 405
        assert "MCP requires POST" in response.body

    def test_mcp_invalid_jsonrpc(self):
        # Invalid JSON-RPC should be blocked
        response = sidecar.handle_request({
            "method": "POST",
            "path": "/mcp/tools/call",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer valid-token"
            },
            "body": json.dumps({
                "method": "tools/call",  # Missing jsonrpc field
                "params": {}
            })
        })
        assert response.status == 400

    def test_a2a_sender_mismatch(self):
        # Token sub != message.from should be blocked
        token_with_sub_agent_a = create_token(sub="agent-a")
        response = sidecar.handle_request({
            "method": "POST",
            "path": "/a2a/message",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token_with_sub_agent_a}"
            },
            "body": json.dumps({
                "protocol": "a2a",
                "from": "agent-b",  # Mismatch!
                "to": "agent-c",
                "message_type": "task",
                "payload": {}
            })
        })
        assert response.status == 403
        assert "Sender identity mismatch" in response.body

    def test_http_to_mcp_blocked(self):
        # Plain HTTP to MCP path should be blocked
        response = sidecar.handle_request({
            "method": "POST",
            "path": "/mcp/tools/call",
            "headers": {
                "Content-Type": "text/plain",  # Not JSON
                "Authorization": "Bearer valid-token"
            },
            "body": "plain text request"
        })
        assert response.status == 415
```

---

### 9.6 Observability Stack

This section defines the complete observability infrastructure for monitoring, alerting, tracing, and logging across the ZTA-MAS system.

#### 9.6.1 Observability Architecture

**Three Pillars of Observability:**
1. **Metrics** (Prometheus + Grafana): Time-series data for performance and health
2. **Traces** (OpenTelemetry + Tempo): Distributed request flow tracking
3. **Logs** (Loki + Promtail): Structured and unstructured log aggregation

**Component Diagram:**
```mermaid
graph TB
    subgraph "Metrics (Prometheus Stack)"
        PROM[Prometheus<br/>2 replicas + Thanos]
        SM[ServiceMonitors]
        PM[PodMonitors]
        RULES[PrometheusRules]
    end

    subgraph "Visualization (Grafana)"
        GRAFANA[Grafana<br/>2 replicas]
        DASH_ZTA[ZTA Dashboards]
        DASH_NET[Network Dashboards]
        DASH_SEC[Security Dashboards]
    end

    subgraph "Alerting (AlertManager)"
        ALERT[AlertManager<br/>3 replicas]
        SLACK[Slack Receiver]
        PD[PagerDuty Receiver]
    end

    subgraph "Tracing (Tempo Stack)"
        TEMPO[Grafana Tempo<br/>3 replicas]
        OTEL_COL[OpenTelemetry Collector<br/>DaemonSet]
    end

    subgraph "Logging (Loki Stack)"
        LOKI[Grafana Loki<br/>Write: 3, Read: 2]
        PROMTAIL[Promtail<br/>DaemonSet]
    end

    subgraph "ZTA Services"
        AUTH[Auth Service]
        POLICY[Policy Service]
        AI[AI Pipeline]
        TELEM[Telemetry Service]
        SIDECAR[Sidecars]
    end

    subgraph "Infrastructure"
        CILIUM[Cilium/Hubble]
        K8S[Kubernetes API]
    end

    AUTH --> SM
    POLICY --> SM
    AI --> SM
    TELEM --> SM
    SIDECAR --> PM
    CILIUM --> PROM
    K8S --> PROM

    SM --> PROM
    PM --> PROM
    PROM --> RULES
    RULES --> ALERT
    ALERT --> SLACK
    ALERT --> PD

    PROM --> GRAFANA
    GRAFANA --> DASH_ZTA
    GRAFANA --> DASH_NET
    GRAFANA --> DASH_SEC

    AUTH --> OTEL_COL
    POLICY --> OTEL_COL
    AI --> OTEL_COL
    SIDECAR --> OTEL_COL
    OTEL_COL --> TEMPO
    TEMPO --> GRAFANA

    AUTH --> PROMTAIL
    POLICY --> PROMTAIL
    AI --> PROMTAIL
    TELEM --> PROMTAIL
    SIDECAR --> PROMTAIL
    PROMTAIL --> LOKI
    LOKI --> GRAFANA
```

**Component Specifications:**

| Component | Purpose | Storage Backend | Retention | Replicas | Resource Requests |
|-----------|---------|-----------------|-----------|----------|-------------------|
| Prometheus | Metrics storage | Local SSD (200GB per replica) | 30 days local, 1 year Thanos | 2 + Thanos sidecar | 4 CPU, 8Gi RAM |
| Thanos | Long-term metrics | S3 (unlimited) | 1 year | Sidecar per Prometheus | 1 CPU, 2Gi RAM |
| Grafana | Visualization | PostgreSQL (dashboards) | N/A | 2 | 500m CPU, 1Gi RAM |
| AlertManager | Alert routing | Local disk (10GB) | 7 days | 3 (clustered) | 200m CPU, 512Mi RAM |
| Tempo | Trace storage | S3 (object storage) | 15 days | 3 (distributor, ingester, querier) | 2 CPU, 4Gi RAM |
| Loki | Log aggregation | S3 (object storage) | 30 days | 3 write, 2 read | 2 CPU, 4Gi RAM |
| OpenTelemetry Collector | Trace processing | Ephemeral (memory buffer) | N/A | DaemonSet | 500m CPU, 1Gi RAM |
| Promtail | Log shipping | Ephemeral | N/A | DaemonSet | 200m CPU, 512Mi RAM |

#### 9.6.2 Prometheus Deployment

**Prometheus Operator Custom Resource:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: zta-prometheus
  namespace: monitoring
spec:
  replicas: 2
  version: v2.48.0
  serviceAccountName: prometheus
  securityContext:
    fsGroup: 2000
    runAsNonRoot: true
    runAsUser: 1000

  # Storage
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: fast-ssd
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 200Gi

  # Retention
  retention: 30d
  retentionSize: "180GB"

  # Resource limits
  resources:
    requests:
      cpu: 4000m
      memory: 8Gi
    limits:
      cpu: 8000m
      memory: 16Gi

  # Scrape configuration
  serviceMonitorSelector:
    matchLabels:
      monitoring: zta
  podMonitorSelector:
    matchLabels:
      monitoring: zta
  ruleSelector:
    matchLabels:
      monitoring: zta

  # Thanos sidecar for long-term storage
  thanos:
    image: quay.io/thanos/thanos:v0.32.5
    version: v0.32.5
    objectStorageConfig:
      key: thanos.yaml
      name: thanos-object-storage

  # High availability
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - prometheus
        topologyKey: kubernetes.io/hostname
```

**Thanos Object Storage Configuration:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: thanos-object-storage
  namespace: monitoring
stringData:
  thanos.yaml: |
    type: S3
    config:
      bucket: "zta-metrics-long-term"
      endpoint: "s3.us-west-2.amazonaws.com"
      region: "us-west-2"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
```

#### 9.6.3 ServiceMonitors for ZTA Components

**Auth Service ServiceMonitor:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: zta-auth-service
  namespace: zta-control-plane
  labels:
    monitoring: zta
spec:
  selector:
    matchLabels:
      app: zta-auth-service
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    scheme: https
    tlsConfig:
      caFile: /etc/prometheus/secrets/zta-ca/ca.crt
      certFile: /etc/prometheus/secrets/zta-client-cert/tls.crt
      keyFile: /etc/prometheus/secrets/zta-client-cert/tls.key
    relabelings:
    - sourceLabels: [__meta_kubernetes_pod_name]
      targetLabel: pod
    - sourceLabels: [__meta_kubernetes_pod_node_name]
      targetLabel: node
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'go_.*'
      action: drop  # Drop Go runtime metrics to reduce cardinality
```

**Sidecar PodMonitor:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: zta-sidecars
  namespace: monitoring
  labels:
    monitoring: zta
spec:
  selector:
    matchLabels:
      zta.io/sidecar: "true"
  podMetricsEndpoints:
  - port: sidecar-metrics
    interval: 15s
    path: /stats/prometheus
    relabelings:
    - sourceLabels: [__meta_kubernetes_namespace]
      targetLabel: namespace
    - sourceLabels: [__meta_kubernetes_pod_label_app]
      targetLabel: app
    - sourceLabels: [__meta_kubernetes_pod_label_version]
      targetLabel: version
```

#### 9.6.4 Key Metrics Exported

**Auth Service Metrics:**
```
# Token operations
zta_auth_token_issued_total{app_id, mas_id}
zta_auth_token_exchanged_total{app_id, mas_id, result="success|failed"}
zta_auth_token_introspection_total{result="active|invalid"}

# Latency histograms
zta_auth_token_generation_duration_seconds{quantile}
zta_auth_token_exchange_duration_seconds{quantile}

# Tool checks
zta_auth_tool_check_total{check_type="deterministic|ai", result="pass|fail"}
zta_auth_tool_check_duration_seconds{check_type, quantile}

# External dependencies
zta_auth_keycloak_request_duration_seconds{operation, quantile}
zta_auth_database_query_duration_seconds{query_type, quantile}
```

**Policy Service Metrics:**
```
# Policy operations
zta_policy_app_registered_total
zta_policy_mas_created_total
zta_policy_cilium_policy_generated_total{namespace}

# Cache performance
zta_policy_cache_hit_ratio{cache_type="app|mas|policy"}
zta_policy_cache_size_bytes{cache_type}
```

**AI Pipeline Metrics:**
```
# Matcher performance
zta_ai_matcher_duration_seconds{matcher_type="embeddings|llm|hybrid", quantile}
zta_ai_matcher_result_total{matcher_type, result="match|nomatch"}

# LLM API calls
zta_ai_llm_request_total{model, result="success|timeout|error"}
zta_ai_llm_request_duration_seconds{model, quantile}
zta_ai_llm_tokens_consumed_total{model, type="prompt|completion"}

# Embeddings
zta_ai_embedding_request_total{model}
zta_ai_embedding_cache_hit_ratio
```

**Sidecar Metrics (Envoy):**
```
# Request metrics
envoy_cluster_upstream_rq_total{cluster}
envoy_cluster_upstream_rq_xx{cluster, envoy_response_code_class="2|4|5"}
envoy_cluster_upstream_rq_time{cluster, quantile}

# Token operations
zta_sidecar_token_injection_total
zta_sidecar_token_introspection_total{result="cached|fresh"}
zta_sidecar_token_introspection_cache_hit_ratio

# Protocol enforcement
zta_sidecar_protocol_validation_total{protocol="mcp|a2a", result="pass|fail"}
zta_sidecar_protocol_violation_total{protocol, violation_type}

# Connection metrics
envoy_cluster_upstream_cx_total{cluster}
envoy_cluster_upstream_cx_active{cluster}
```

**Cilium/Hubble Metrics:**
```
# Network policy enforcement
cilium_policy_l3_total{direction="ingress|egress", verdict="forwarded|denied"}
cilium_policy_l4_total{direction, verdict, protocol}
cilium_policy_l7_total{direction, verdict, protocol}

# Identity management
cilium_identity_count
cilium_endpoint_count{state}

# Hubble flows
hubble_flows_processed_total{verdict}
hubble_drop_total{reason}
```

#### 9.6.5 PrometheusRules (Alerting)

**Critical Alerts:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: zta-critical-alerts
  namespace: monitoring
  labels:
    monitoring: zta
spec:
  groups:
  - name: zta.critical
    interval: 30s
    rules:

    # High token exchange failure rate
    - alert: HighTokenExchangeFailureRate
      expr: |
        (
          sum(rate(zta_auth_token_exchanged_total{result="failed"}[5m]))
          /
          sum(rate(zta_auth_token_exchanged_total[5m]))
        ) > 0.05
      for: 5m
      labels:
        severity: critical
        component: auth-service
      annotations:
        summary: "High token exchange failure rate"
        description: "{{ $value | humanizePercentage }} of token exchanges are failing (threshold: 5%)"
        runbook_url: "https://docs.zta.io/runbooks/high-token-failure"

    # Auth service down
    - alert: AuthServiceDown
      expr: up{job="zta-auth-service"} == 0
      for: 2m
      labels:
        severity: critical
        component: auth-service
      annotations:
        summary: "Auth Service is down"
        description: "Auth Service has been down for more than 2 minutes"
        runbook_url: "https://docs.zta.io/runbooks/auth-service-down"

    # AI Pipeline high latency
    - alert: AIMatcherHighLatency
      expr: |
        histogram_quantile(0.95,
          sum(rate(zta_ai_matcher_duration_seconds_bucket[5m])) by (le, matcher_type)
        ) > 5
      for: 10m
      labels:
        severity: warning
        component: ai-pipeline
      annotations:
        summary: "AI Matcher P95 latency above 5s"
        description: "{{ $labels.matcher_type }} matcher P95 latency: {{ $value }}s"
        runbook_url: "https://docs.zta.io/runbooks/ai-pipeline-latency"

    # Certificate expiring soon
    - alert: CertificateExpiringSoon
      expr: |
        (certmanager_certificate_expiration_timestamp_seconds - time()) / 86400 < 15
      for: 1h
      labels:
        severity: warning
        component: cert-manager
      annotations:
        summary: "Certificate {{ $labels.name }} expiring in {{ $value }} days"
        description: "Certificate in namespace {{ $labels.namespace }} expires in less than 15 days"
        runbook_url: "https://docs.zta.io/runbooks/certificate-renewal"

    # Network policy denials spike
    - alert: NetworkPolicyDenialsSpike
      expr: |
        sum(rate(cilium_policy_l3_total{verdict="denied"}[5m])) by (namespace)
        > 10
      for: 5m
      labels:
        severity: warning
        component: cilium
      annotations:
        summary: "High rate of network policy denials in {{ $labels.namespace }}"
        description: "{{ $value }} denials/sec detected (possible attack or misconfiguration)"
        runbook_url: "https://docs.zta.io/runbooks/network-policy-denials"

    # Sidecar token introspection failures
    - alert: SidecarTokenIntrospectionFailures
      expr: |
        sum(rate(zta_sidecar_token_introspection_total{result="error"}[5m])) by (namespace, pod)
        > 1
      for: 5m
      labels:
        severity: warning
        component: sidecar
      annotations:
        summary: "Sidecar {{ $labels.pod }} experiencing token introspection failures"
        description: "{{ $value }} introspection failures/sec"
        runbook_url: "https://docs.zta.io/runbooks/sidecar-token-failures"
```

**Warning Alerts:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: zta-warning-alerts
  namespace: monitoring
  labels:
    monitoring: zta
spec:
  groups:
  - name: zta.warnings
    interval: 1m
    rules:

    # Low cache hit ratio
    - alert: LowSidecarCacheHitRatio
      expr: zta_sidecar_token_introspection_cache_hit_ratio < 0.7
      for: 15m
      labels:
        severity: warning
        component: sidecar
      annotations:
        summary: "Low sidecar cache hit ratio: {{ $value | humanizePercentage }}"
        description: "Cache TTL may need adjustment (target: >85%)"

    # High LLM API latency
    - alert: HighLLMAPILatency
      expr: |
        histogram_quantile(0.95,
          sum(rate(zta_ai_llm_request_duration_seconds_bucket[5m])) by (le, model)
        ) > 2
      for: 10m
      labels:
        severity: warning
        component: ai-pipeline
      annotations:
        summary: "High LLM API latency for {{ $labels.model }}"
        description: "P95 latency: {{ $value }}s (threshold: 2s)"

    # PostgreSQL connection pool exhaustion
    - alert: PostgreSQLConnectionPoolExhaustion
      expr: |
        (
          sum(pg_stat_activity_count) by (datname)
          /
          pg_settings_max_connections
        ) > 0.8
      for: 5m
      labels:
        severity: warning
        component: postgresql
      annotations:
        summary: "PostgreSQL connection pool usage high"
        description: "Database {{ $labels.datname }} using {{ $value | humanizePercentage }} of connections"
```

#### 9.6.6 AlertManager Configuration

**AlertManager Deployment:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: Alertmanager
metadata:
  name: zta-alertmanager
  namespace: monitoring
spec:
  replicas: 3
  version: v0.26.0

  # Clustering for HA
  listenLocal: false
  portName: web

  # Storage
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: fast-ssd
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi

  # Resources
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

  # Anti-affinity for HA
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - alertmanager
        topologyKey: kubernetes.io/hostname
```

**AlertManager Configuration (Secret):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-zta-alertmanager
  namespace: monitoring
stringData:
  alertmanager.yaml: |
    global:
      resolve_timeout: 5m
      slack_api_url: '${SLACK_WEBHOOK_URL}'

    route:
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      receiver: 'default'
      routes:

      # Critical alerts go to PagerDuty
      - match:
          severity: critical
        receiver: 'pagerduty-critical'
        continue: true

      # All alerts go to Slack
      - match_re:
          severity: critical|warning
        receiver: 'slack-alerts'

    receivers:
    - name: 'default'
      slack_configs:
      - channel: '#zta-alerts'
        title: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

    - name: 'pagerduty-critical'
      pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        description: '{{ .GroupLabels.alertname }}'
        details:
          firing: '{{ template "pagerduty.default.instances" . }}'

    - name: 'slack-alerts'
      slack_configs:
      - channel: '#zta-alerts'
        title: '[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .GroupLabels.alertname }}'
        text: |-
          {{ range .Alerts }}
          *Summary:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          *Runbook:* {{ .Annotations.runbook_url }}
          *Labels:*
          {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
          {{ end }}
          {{ end }}
        send_resolved: true
```

#### 9.6.7 Distributed Tracing with Tempo

**Tempo Deployment:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tempo-config
  namespace: monitoring
data:
  tempo.yaml: |
    server:
      http_listen_port: 3200

    distributor:
      receivers:
        otlp:
          protocols:
            grpc:
              endpoint: 0.0.0.0:4317
            http:
              endpoint: 0.0.0.0:4318

    ingester:
      trace_idle_period: 10s
      max_block_bytes: 1_000_000
      max_block_duration: 5m

    compactor:
      compaction:
        block_retention: 336h  # 14 days

    storage:
      trace:
        backend: s3
        s3:
          bucket: zta-traces
          endpoint: s3.us-west-2.amazonaws.com
          region: us-west-2
        wal:
          path: /var/tempo/wal
        block:
          bloom_filter_false_positive: 0.05

    query_frontend:
      search:
        duration_slo: 5s
        throughput_bytes_slo: 1e+09
      trace_by_id:
        duration_slo: 5s
```

**OpenTelemetry Collector DaemonSet:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: otel-collector
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      serviceAccountName: otel-collector
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:0.89.0
        command:
        - /otelcol-contrib
        - --config=/conf/otel-collector-config.yaml
        ports:
        - containerPort: 4317  # OTLP gRPC
        - containerPort: 4318  # OTLP HTTP
        - containerPort: 8888  # Metrics
        env:
        - name: K8S_NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: K8S_POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        volumeMounts:
        - name: config
          mountPath: /conf
      volumes:
      - name: config
        configMap:
          name: otel-collector-config
```

**OpenTelemetry Collector Configuration:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: monitoring
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318

    processors:
      batch:
        timeout: 10s
        send_batch_size: 1024

      resource:
        attributes:
        - key: service.namespace
          from_attribute: k8s.namespace.name
          action: upsert
        - key: service.instance.id
          from_attribute: k8s.pod.name
          action: upsert

      k8sattributes:
        auth_type: "serviceAccount"
        passthrough: false
        extract:
          metadata:
          - k8s.namespace.name
          - k8s.deployment.name
          - k8s.pod.name
          - k8s.pod.uid
          - k8s.node.name
        pod_association:
        - sources:
          - from: resource_attribute
            name: k8s.pod.ip

    exporters:
      otlp:
        endpoint: tempo.monitoring.svc.cluster.local:4317
        tls:
          insecure: false
          ca_file: /etc/otel/certs/ca.crt

      prometheus:
        endpoint: "0.0.0.0:8888"
        namespace: otel

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [k8sattributes, resource, batch]
          exporters: [otlp]

        metrics:
          receivers: [otlp]
          processors: [k8sattributes, resource, batch]
          exporters: [prometheus]
```

**Service Instrumentation Example (Python):**
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Configure tracing
resource = Resource.create(attributes={
    "service.name": "zta-auth-service",
    "service.version": "1.0.0",
    "deployment.environment": "production"
})

provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="otel-collector.monitoring.svc.cluster.local:4317",
    insecure=False
)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Instrument code
@tracer.start_as_current_span("token_exchange")
def exchange_token(request):
    span = trace.get_current_span()
    span.set_attribute("app_id", request.app_id)
    span.set_attribute("mas_id", request.mas_id)

    with tracer.start_as_current_span("validate_token"):
        # Token validation logic
        pass

    with tracer.start_as_current_span("run_tool_checks"):
        # Tool check pipeline
        pass

    return response
```

#### 9.6.8 Logging with Loki

**Loki StatefulSet (Write Path):**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: loki-write
  namespace: monitoring
spec:
  serviceName: loki-write
  replicas: 3
  selector:
    matchLabels:
      app: loki
      component: write
  template:
    metadata:
      labels:
        app: loki
        component: write
    spec:
      containers:
      - name: loki
        image: grafana/loki:2.9.3
        args:
        - -config.file=/etc/loki/loki.yaml
        - -target=write
        ports:
        - containerPort: 3100
          name: http
        - containerPort: 9095
          name: grpc
        resources:
          requests:
            cpu: 2000m
            memory: 4Gi
          limits:
            cpu: 4000m
            memory: 8Gi
        volumeMounts:
        - name: config
          mountPath: /etc/loki
        - name: data
          mountPath: /loki
      volumes:
      - name: config
        configMap:
          name: loki-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

**Loki Configuration:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: loki-config
  namespace: monitoring
data:
  loki.yaml: |
    auth_enabled: false

    server:
      http_listen_port: 3100
      grpc_listen_port: 9095

    common:
      path_prefix: /loki
      storage:
        filesystem:
          chunks_directory: /loki/chunks
          rules_directory: /loki/rules
      replication_factor: 3
      ring:
        kvstore:
          store: memberlist

    memberlist:
      join_members:
      - loki-write-0.loki-write.monitoring.svc.cluster.local:7946
      - loki-write-1.loki-write.monitoring.svc.cluster.local:7946
      - loki-write-2.loki-write.monitoring.svc.cluster.local:7946

    schema_config:
      configs:
      - from: 2023-01-01
        store: boltdb-shipper
        object_store: s3
        schema: v12
        index:
          prefix: loki_index_
          period: 24h

    storage_config:
      boltdb_shipper:
        active_index_directory: /loki/index
        cache_location: /loki/index_cache
        shared_store: s3

      aws:
        s3: s3://us-west-2/zta-logs
        region: us-west-2
        s3forcepathstyle: false

    limits_config:
      retention_period: 720h  # 30 days
      ingestion_rate_mb: 100
      ingestion_burst_size_mb: 200
      per_stream_rate_limit: 50MB
      per_stream_rate_limit_burst: 100MB

    chunk_store_config:
      max_look_back_period: 720h

    table_manager:
      retention_deletes_enabled: true
      retention_period: 720h

    query_range:
      parallelise_shardable_queries: true
      cache_results: true
      results_cache:
        cache:
          memcached_client:
            host: memcached.monitoring.svc.cluster.local
            service: memcached
```

**Promtail DaemonSet:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: promtail
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: promtail
  template:
    metadata:
      labels:
        app: promtail
    spec:
      serviceAccountName: promtail
      containers:
      - name: promtail
        image: grafana/promtail:2.9.3
        args:
        - -config.file=/etc/promtail/promtail.yaml
        env:
        - name: HOSTNAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        volumeMounts:
        - name: config
          mountPath: /etc/promtail
        - name: varlog
          mountPath: /var/log
          readOnly: true
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 2Gi
      volumes:
      - name: config
        configMap:
          name: promtail-config
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

**Promtail Configuration:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: monitoring
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0

    positions:
      filename: /tmp/positions.yaml

    clients:
    - url: http://loki-write.monitoring.svc.cluster.local:3100/loki/api/v1/push
      batchwait: 1s
      batchsize: 1048576
      timeout: 10s

    scrape_configs:
    # Kubernetes pod logs
    - job_name: kubernetes-pods
      kubernetes_sd_configs:
      - role: pod

      relabel_configs:
      # Only scrape pods with zta.io/logs=true
      - source_labels: [__meta_kubernetes_pod_label_zta_io_logs]
        regex: "true"
        action: keep

      # Add namespace
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace

      # Add pod name
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod

      # Add container name
      - source_labels: [__meta_kubernetes_pod_container_name]
        target_label: container

      # Add app label
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app

      # Add node name
      - source_labels: [__meta_kubernetes_pod_node_name]
        target_label: node

      # Extract log path
      - source_labels: [__meta_kubernetes_pod_uid, __meta_kubernetes_pod_container_name]
        target_label: __path__
        separator: /
        replacement: /var/log/pods/*$1/*.log

      pipeline_stages:
      # Parse JSON logs
      - json:
          expressions:
            level: level
            timestamp: timestamp
            message: message
            trace_id: trace_id
            span_id: span_id

      # Extract level
      - labels:
          level:

      # Extract trace context
      - labels:
          trace_id:
          span_id:

      # Parse timestamp
      - timestamp:
          source: timestamp
          format: RFC3339

      # Drop debug logs in production
      - match:
          selector: '{level="debug", namespace=~".*-prod"}'
          action: drop
```

#### 9.6.9 Grafana Dashboards

**Grafana Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      securityContext:
        fsGroup: 472
        runAsUser: 472
      containers:
      - name: grafana
        image: grafana/grafana:10.2.2
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: GF_DATABASE_TYPE
          value: postgres
        - name: GF_DATABASE_HOST
          value: postgresql.zta-control-plane.svc.cluster.local:5432
        - name: GF_DATABASE_NAME
          value: grafana
        - name: GF_DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: grafana-db-credentials
              key: username
        - name: GF_DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-db-credentials
              key: password
        - name: GF_AUTH_ANONYMOUS_ENABLED
          value: "false"
        - name: GF_AUTH_BASIC_ENABLED
          value: "true"
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-admin-credentials
              key: password
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        volumeMounts:
        - name: dashboards-provisioning
          mountPath: /etc/grafana/provisioning/dashboards
        - name: datasources-provisioning
          mountPath: /etc/grafana/provisioning/datasources
        - name: dashboards
          mountPath: /var/lib/grafana/dashboards
      volumes:
      - name: dashboards-provisioning
        configMap:
          name: grafana-dashboards-provisioning
      - name: datasources-provisioning
        configMap:
          name: grafana-datasources
      - name: dashboards
        configMap:
          name: grafana-dashboards
```

**Grafana Datasources:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus.monitoring.svc.cluster.local:9090
      isDefault: true
      jsonData:
        timeInterval: 30s

    - name: Loki
      type: loki
      access: proxy
      url: http://loki-read.monitoring.svc.cluster.local:3100
      jsonData:
        derivedFields:
        - datasourceName: Tempo
          matcherRegex: "trace_id=(\\w+)"
          name: TraceID
          url: "$${__value.raw}"

    - name: Tempo
      type: tempo
      access: proxy
      url: http://tempo.monitoring.svc.cluster.local:3200
      jsonData:
        tracesToLogs:
          datasourceUid: Loki
          tags: ['trace_id']
          spanStartTimeShift: '-1h'
          spanEndTimeShift: '1h'
        serviceMap:
          datasourceUid: Prometheus
```

**Dashboard: ZTA Overview (JSON):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-zta-overview
  namespace: monitoring
data:
  zta-overview.json: |
    {
      "dashboard": {
        "title": "ZTA Overview",
        "tags": ["zta", "overview"],
        "timezone": "browser",
        "schemaVersion": 38,
        "panels": [
          {
            "id": 1,
            "title": "Token Issuance Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "sum(rate(zta_auth_token_issued_total[5m]))",
                "legendFormat": "Tokens/sec"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
          },
          {
            "id": 2,
            "title": "Token Exchange Success Rate",
            "type": "stat",
            "targets": [
              {
                "expr": "sum(rate(zta_auth_token_exchanged_total{result='success'}[5m])) / sum(rate(zta_auth_token_exchanged_total[5m]))",
                "legendFormat": "Success Rate"
              }
            ],
            "fieldConfig": {
              "defaults": {
                "unit": "percentunit",
                "thresholds": {
                  "mode": "absolute",
                  "steps": [
                    {"value": 0, "color": "red"},
                    {"value": 0.95, "color": "yellow"},
                    {"value": 0.99, "color": "green"}
                  ]
                }
              }
            },
            "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
          },
          {
            "id": 3,
            "title": "Tool Check Pass/Fail Ratio",
            "type": "piechart",
            "targets": [
              {
                "expr": "sum by (result) (rate(zta_auth_tool_check_total[5m]))",
                "legendFormat": "{{ result }}"
              }
            ],
            "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
          },
          {
            "id": 4,
            "title": "AI Pipeline Latency (P95)",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, sum by (le, matcher_type) (rate(zta_ai_matcher_duration_seconds_bucket[5m])))",
                "legendFormat": "{{ matcher_type }}"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
          },
          {
            "id": 5,
            "title": "Control Plane CPU Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "sum by (pod) (rate(container_cpu_usage_seconds_total{namespace='zta-control-plane'}[5m]))",
                "legendFormat": "{{ pod }}"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
          },
          {
            "id": 6,
            "title": "Network Policy Verdicts",
            "type": "timeseries",
            "targets": [
              {
                "expr": "sum by (verdict) (rate(cilium_policy_l3_total[5m]))",
                "legendFormat": "{{ verdict }}"
              }
            ],
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
          }
        ]
      }
    }
```

#### 9.6.10 Observability Costs and Sizing

**Cost Breakdown (Monthly for 1000 pods):**

| Component | Storage | Compute | Egress | Total (AWS) |
|-----------|---------|---------|--------|-------------|
| Prometheus (30d retention) | 2x 200GB SSD = $80 | 2x m5.xlarge = $280 | Negligible | ~$360/mo |
| Thanos (1y long-term) | S3: ~500GB = $11.50 | 2x t3.medium = $60 | $45 (S3 access) | ~$116.50/mo |
| Loki (30d retention) | S3: ~2TB = $46 | 5x m5.xlarge = $700 | $90 (S3 access) | ~$836/mo |
| Tempo (15d retention) | S3: ~800GB = $18.40 | 3x m5.large = $210 | $40 (S3 access) | ~$268.40/mo |
| Grafana | PostgreSQL: Included | 2x t3.medium = $60 | Negligible | ~$60/mo |
| **TOTAL** | **~$156/mo** | **~$1310/mo** | **~$175/mo** | **~$1641/mo** |

**Optimization Recommendations:**
- Use spot instances for Loki write nodes (save 60%)
- Enable S3 Intelligent-Tiering (save 20% on storage)
- Implement metric relabeling to drop high-cardinality metrics (reduce Prometheus storage by 30%)
- Use compression for Loki logs (reduce S3 storage by 50%)

**Sizing Guidelines:**

| Workload Scale | Prometheus Storage | Loki Ingestion Rate | Tempo Traces/sec | Total Nodes |
|----------------|-------------------|---------------------|------------------|-------------|
| Small (< 100 pods) | 50GB | 10 MB/s | 100 | 5 nodes |
| Medium (100-500 pods) | 100GB | 50 MB/s | 500 | 10 nodes |
| Large (500-2000 pods) | 200GB | 200 MB/s | 2000 | 20 nodes |
| XLarge (2000+ pods) | 500GB | 1 GB/s | 10000 | 50 nodes |

---



## 10. Implementation Roadmap

### 10.1 Migration Strategy: Monolith to Microservices

This section provides a detailed, step-by-step migration strategy for transitioning the existing monolithic Zero Trust Authorization server to a cloud-native, microservices-based architecture running in Kubernetes.

#### 10.1.1 Migration Overview

**Current State (Monolith):**
```mermaid
graph TB
    subgraph "Monolithic ZTA Server"
        AUTH[Auth Logic]
        POLICY[Policy Logic]
        AI[AI Pipeline]
        TELEM[Telemetry]
        DISC[Discovery]

        AUTH --> SHARED_DB[(PostgreSQL)]
        POLICY --> SHARED_DB
        AI --> SHARED_DB
        TELEM --> SHARED_DB
        DISC --> SHARED_DB
    end

    AGENTS[Agents] --> AUTH
    MCP[MCP Servers] --> AUTH
    KC[Keycloak] <--> AUTH
    LLM[LLM API] <--> AI
```

**Target State (Microservices):**
```mermaid
graph TB
    subgraph "Control Plane"
        AUTH_SVC[Auth Service<br/>StatefulSet]
        POLICY_SVC[Policy Service<br/>Deployment]
        AI_SVC[AI Pipeline Service<br/>Deployment]
        TELEM_SVC[Telemetry Service<br/>Deployment]
        DISC_SVC[Discovery Service<br/>Deployment]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Shared)]
        REDIS[(Redis<br/>Cache)]
    end

    subgraph "Data Plane"
        SIDECAR[Sidecars<br/>DaemonSet]
    end

    AGENTS[Agents] --> SIDECAR
    SIDECAR --> AUTH_SVC
    MCP[MCP Servers] --> SIDECAR
    SIDECAR --> AUTH_SVC

    AUTH_SVC --> PG
    AUTH_SVC --> REDIS
    AUTH_SVC --> POLICY_SVC
    AUTH_SVC --> AI_SVC

    POLICY_SVC --> PG
    POLICY_SVC --> REDIS

    AI_SVC --> LLM[LLM API]
    AI_SVC --> REDIS

    TELEM_SVC --> PG
    DISC_SVC --> PG

    KC[Keycloak] <--> AUTH_SVC
```

**Migration Principles:**
1. **Zero Downtime**: All migrations must maintain service availability
2. **Reversible**: Every step must have a rollback plan
3. **Validated**: Each phase includes automated validation
4. **Gradual**: Use feature flags and traffic splitting
5. **Observable**: Enhanced monitoring during migration

#### 10.1.2 Pre-Migration Checklist

**Infrastructure Prerequisites:**
```yaml
# 1. Kubernetes cluster ready
- Kubernetes version: >= 1.27
- Node count: >= 10 nodes (for migration overlap)
- Cilium installed: with Hubble enabled
- cert-manager installed: for TLS
- Prometheus stack: for monitoring migration

# 2. Backup and baseline
- PostgreSQL backup taken: < 1 hour old
- Keycloak realm exported
- Baseline metrics captured: token rate, latency, error rate
- Load test baseline established

# 3. Feature flags infrastructure
- Feature flag service deployed (LaunchDarkly, Unleash, or custom)
- Flags defined for each service: auth-service-v2, ai-pipeline-v2, etc.
- Admin UI accessible for emergency toggle

# 4. Observability enhancement
- Distributed tracing enabled in monolith
- Custom metrics exported (service=monolith)
- Correlation IDs added to all requests
- Grafana dashboard: "Migration Progress"
```

**Code Preparation:**
```python
# Add service version tags to all metrics
from prometheus_client import Counter

token_issued_counter = Counter(
    'zta_auth_token_issued_total',
    'Total tokens issued',
    ['service_version', 'app_id', 'mas_id']  # service_version: monolith|microservice
)

# Add feature flag checks
from feature_flags import FeatureFlagClient

ff_client = FeatureFlagClient()

def exchange_token(request):
    # Route to microservice if flag enabled
    if ff_client.is_enabled('auth-service-v2'):
        return exchange_token_v2(request)  # Microservice
    else:
        return exchange_token_v1(request)  # Monolith
```

#### 10.1.3 Phase-by-Phase Migration

**Phase 0: Preparation (Week 0)**

**Objective**: Establish migration infrastructure without changing traffic flow.

**Steps:**
1. Deploy observability stack (Prometheus, Grafana, Loki, Tempo)
2. Deploy feature flag service
3. Add service version labels to monolith metrics
4. Create "Migration Dashboard" in Grafana
5. Establish baseline performance (P50, P95, P99 latencies)
6. Document rollback procedures
7. Set up blue-green infrastructure slots

**Validation:**
```bash
# Verify metrics are tagged
curl -s http://prometheus:9090/api/v1/query?query='zta_auth_token_issued_total{service_version="monolith"}' | jq .

# Verify feature flags
curl -s http://feature-flags:8080/api/flags | jq '.flags[] | select(.name=="auth-service-v2")'

# Expected: enabled=false, traffic_split=0%
```

**Rollback**: N/A (no changes to traffic flow yet)

---

**Phase 1: Deploy Microservices (Shadow Mode) - Week 1**

**Objective**: Deploy all microservices alongside monolith in "shadow mode" (receiving traffic but not serving responses).

**Steps:**
1. Build and push Docker images for all 5 microservices
2. Deploy microservices with `replicas: 1` (minimal footprint)
3. Configure microservices to read from shared PostgreSQL
4. Deploy Redis for inter-service caching
5. Route duplicate traffic to microservices (using Envoy shadowing or custom middleware)
6. Monitor microservice logs/metrics (DO NOT serve responses yet)

**Helm Values (shadow mode):**
```yaml
migration:
  shadowMode:
    enabled: true
    services:
      authService:
        enabled: true
        replicas: 1
      policyService:
        enabled: true
        replicas: 1
      aiPipeline:
        enabled: true
        replicas: 1
      telemetry:
        enabled: true
        replicas: 1
      discovery:
        enabled: true
        replicas: 1

  monolith:
    enabled: true  # Still serving all traffic
    replicas: 3
```

**Traffic Shadowing Configuration (Envoy):**
```yaml
- match:
    prefix: "/oauth/token/exchange"
  route:
    cluster: monolith-auth-service  # Primary
    request_mirror_policies:
    - cluster: auth-service-v2      # Shadow (duplicate traffic)
      runtime_fraction:
        default_value:
          numerator: 100              # 100% shadow
```

**Validation:**
```bash
# Verify microservices are receiving traffic
kubectl logs -n zta-control-plane deployment/zta-auth-service --tail=100 | grep "token_exchange_request"

# Compare response times (should be similar)
# Monolith P95 latency
curl -s 'http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(zta_auth_token_exchange_duration_seconds_bucket{service_version="monolith"}[5m]))'

# Microservice P95 latency (shadow)
curl -s 'http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(zta_auth_token_exchange_duration_seconds_bucket{service_version="microservice"}[5m]))'

# Verify NO production traffic served by microservices
kubectl logs -n zta-control-plane deployment/zta-auth-service | grep "response_sent" | wc -l
# Expected: 0 (shadowing doesn't send responses)
```

**Rollback:**
```bash
# Disable shadowing
helm upgrade zta-mas-system ./charts/zta-mas-system \
  --set migration.shadowMode.enabled=false \
  --namespace zta-control-plane

# Delete microservice deployments (optional)
kubectl delete deployment -n zta-control-plane -l migration-phase=shadow
```

---

**Phase 2: Canary Auth Service (1% Traffic) - Week 2**

**Objective**: Route 1% of production traffic to Auth Service microservice.

**Steps:**
1. Enable feature flag `auth-service-v2` with 1% traffic split
2. Configure Envoy to route 1% of `/oauth/token` requests to microservice
3. Monitor error rates, latency, and correctness
4. Compare monolith vs microservice metrics side-by-side
5. If stable for 48 hours, proceed to 5%

**Feature Flag Configuration:**
```json
{
  "name": "auth-service-v2",
  "enabled": true,
  "traffic_split": {
    "monolith": 99,
    "microservice": 1
  },
  "rollout_strategy": "gradual",
  "validation_rules": {
    "error_rate_threshold": 0.01,  // < 1% errors
    "latency_p95_max_ms": 500
  }
}
```

**Envoy Route Configuration (Weighted Clusters):**
```yaml
- match:
    prefix: "/oauth/token"
  route:
    weighted_clusters:
      clusters:
      - name: monolith-auth-service
        weight: 99
      - name: auth-service-v2
        weight: 1
      runtime_key_prefix: zta.auth_service.traffic_split
    retry_policy:
      retry_on: "5xx"
      num_retries: 3
      per_try_timeout: 2s
```

**Monitoring Alerts (Critical):**
```yaml
- alert: MigrationCanaryErrorRateHigh
  expr: |
    (
      sum(rate(zta_auth_token_exchanged_total{service_version="microservice", result="failed"}[5m]))
      /
      sum(rate(zta_auth_token_exchanged_total{service_version="microservice"}[5m]))
    ) > 0.05
  for: 5m
  annotations:
    summary: "Auth Service v2 error rate > 5% (target: < 1%)"
    action: "ROLLBACK IMMEDIATELY"

- alert: MigrationCanaryLatencyHigh
  expr: |
    histogram_quantile(0.95,
      rate(zta_auth_token_exchange_duration_seconds_bucket{service_version="microservice"}[5m])
    ) > 0.5
  for: 10m
  annotations:
    summary: "Auth Service v2 P95 latency > 500ms"
    action: "Investigate or rollback"
```

**Validation:**
```bash
# Verify 1% traffic split
curl -s http://prometheus:9090/api/v1/query?query='sum(rate(zta_auth_token_issued_total{service_version="microservice"}[5m])) / sum(rate(zta_auth_token_issued_total[5m]))'
# Expected: ~0.01 (1%)

# Compare error rates
# Monolith error rate
curl -s 'http://prometheus:9090/api/v1/query?query=(sum(rate(zta_auth_token_exchanged_total{service_version="monolith",result="failed"}[5m])) / sum(rate(zta_auth_token_exchanged_total{service_version="monolith"}[5m])))'

# Microservice error rate
curl -s 'http://prometheus:9090/api/v1/query?query=(sum(rate(zta_auth_token_exchanged_total{service_version="microservice",result="failed"}[5m])) / sum(rate(zta_auth_token_exchanged_total{service_version="microservice"}[5m])))'

# Verify no regressions
# Success: microservice error rate <= monolith error rate + 1%
```

**Rollback (Automatic):**
```python
# Automated rollback trigger
class MigrationSafetyMonitor:
    def check_canary_health(self):
        microservice_error_rate = get_error_rate('microservice')
        microservice_latency_p95 = get_latency_p95('microservice')

        if microservice_error_rate > 0.05:  # > 5%
            self.rollback('High error rate')

        if microservice_latency_p95 > 500:  # > 500ms
            self.rollback('High latency')

    def rollback(self, reason):
        logger.critical(f"AUTOMATIC ROLLBACK TRIGGERED: {reason}")

        # Set feature flag to 0%
        ff_client.update_flag('auth-service-v2', traffic_split={'microservice': 0, 'monolith': 100})

        # Update Envoy config
        envoy_admin.update_route_weights('auth-service', {'monolith': 100, 'microservice': 0})

        # Alert on-call
        pagerduty.trigger_alert(f"Migration rollback: {reason}")
```

**Manual Rollback:**
```bash
# Update feature flag
curl -X PATCH http://feature-flags:8080/api/flags/auth-service-v2 \
  -H "Content-Type: application/json" \
  -d '{"traffic_split": {"microservice": 0, "monolith": 100}}'

# Verify traffic shifted back
kubectl exec -n zta-control-plane deployment/envoy-gateway -- \
  curl -s localhost:19000/config_dump | jq '.configs[] | select(.["@type"] | contains("RouteConfiguration"))'
```

---

**Phase 3: Gradual Traffic Increase (Weeks 3-5)**

**Objective**: Progressively increase traffic to Auth Service microservice: 1% → 5% → 25% → 50% → 100%.

**Traffic Progression Schedule:**

| Week | Traffic % | Duration | Validation Window | Rollback SLA |
|------|-----------|----------|-------------------|--------------|
| 2 | 1% | 48 hours | 2 hours | < 5 minutes |
| 3 | 5% | 72 hours | 4 hours | < 5 minutes |
| 4 | 25% | 5 days | 8 hours | < 10 minutes |
| 5 (Mon) | 50% | 2 days | 12 hours | < 15 minutes |
| 5 (Wed) | 75% | 2 days | 12 hours | < 15 minutes |
| 5 (Fri) | 100% | Permanent | 24 hours | < 30 minutes |

**Validation Checklist (Each Step):**
```bash
#!/bin/bash
# validate_migration_step.sh

set -e

SERVICE=$1  # e.g., auth-service-v2
TRAFFIC_PCT=$2  # e.g., 25

echo "Validating ${SERVICE} at ${TRAFFIC_PCT}% traffic..."

# 1. Check error rate
ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query?query=(sum(rate(zta_auth_token_exchanged_total{service_version=\"microservice\",result=\"failed\"}[10m])) / sum(rate(zta_auth_token_exchanged_total{service_version=\"microservice\"}[10m])))" | jq -r '.data.result[0].value[1]')

if (( $(echo "$ERROR_RATE > 0.02" | bc -l) )); then
  echo "ERROR: Error rate too high: ${ERROR_RATE} (threshold: 0.02)"
  exit 1
fi

# 2. Check latency P95
LATENCY_P95=$(curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, rate(zta_auth_token_exchange_duration_seconds_bucket{service_version=\"microservice\"}[10m]))" | jq -r '.data.result[0].value[1]')

if (( $(echo "$LATENCY_P95 > 0.5" | bc -l) )); then
  echo "ERROR: P95 latency too high: ${LATENCY_P95}s (threshold: 0.5s)"
  exit 1
fi

# 3. Check traffic split matches target
ACTUAL_TRAFFIC=$(curl -s "http://prometheus:9090/api/v1/query?query=(sum(rate(zta_auth_token_issued_total{service_version=\"microservice\"}[5m])) / sum(rate(zta_auth_token_issued_total[5m])))" | jq -r '.data.result[0].value[1]')
EXPECTED_TRAFFIC=$(echo "scale=2; $TRAFFIC_PCT / 100" | bc)

DIFF=$(echo "$ACTUAL_TRAFFIC - $EXPECTED_TRAFFIC" | bc | tr -d '-')
if (( $(echo "$DIFF > 0.03" | bc -l) )); then
  echo "ERROR: Traffic split mismatch. Expected: ${EXPECTED_TRAFFIC}, Actual: ${ACTUAL_TRAFFIC}"
  exit 1
fi

# 4. Check no database errors
DB_ERRORS=$(kubectl logs -n zta-control-plane deployment/zta-auth-service --tail=1000 | grep -c "database connection error" || true)
if [ $DB_ERRORS -gt 5 ]; then
  echo "ERROR: Too many database errors: ${DB_ERRORS}"
  exit 1
fi

# 5. Verify no memory leaks
MEMORY_USAGE=$(kubectl top pod -n zta-control-plane -l app=zta-auth-service --no-headers | awk '{print $3}' | sed 's/Mi//' | head -1)
if [ $MEMORY_USAGE -gt 4000 ]; then
  echo "WARNING: High memory usage: ${MEMORY_USAGE}Mi (threshold: 4000Mi)"
fi

echo "✅ Validation passed for ${SERVICE} at ${TRAFFIC_PCT}%"
```

**Automated Traffic Shift Script:**
```bash
#!/bin/bash
# shift_traffic.sh

SERVICE=$1
FROM_PCT=$2
TO_PCT=$3

echo "Shifting traffic from ${FROM_PCT}% to ${TO_PCT}% for ${SERVICE}..."

# Update feature flag
curl -X PATCH http://feature-flags:8080/api/flags/${SERVICE} \
  -H "Content-Type: application/json" \
  -d "{\"traffic_split\": {\"microservice\": ${TO_PCT}, \"monolith\": $((100 - TO_PCT))}}"

# Wait for Envoy to pick up config change
sleep 30

# Run validation
./validate_migration_step.sh ${SERVICE} ${TO_PCT}

if [ $? -eq 0 ]; then
  echo "✅ Traffic shift successful: ${FROM_PCT}% → ${TO_PCT}%"
else
  echo "❌ Validation failed. Rolling back..."
  ./shift_traffic.sh ${SERVICE} ${TO_PCT} ${FROM_PCT}
  exit 1
fi
```

---

**Phase 4: Migrate Remaining Services (Weeks 6-8)**

**Objective**: Migrate Policy, AI Pipeline, Telemetry, and Discovery services using the same gradual rollout pattern.

**Service Priority Order:**
1. **Telemetry Service** (Week 6) - Lowest risk, async operations
2. **Discovery Service** (Week 6) - Low request rate, cacheable
3. **Policy Service** (Week 7) - Medium risk, high read/low write
4. **AI Pipeline Service** (Week 8) - Highest risk, external LLM dependency

**Per-Service Migration Template:**
```bash
# Week 6: Telemetry Service
./migrate_service.sh telemetry-service 1 5 25 50 100
# Progression: 1% → 5% → 25% → 50% → 100% over 5 days

# Week 6: Discovery Service
./migrate_service.sh discovery-service 1 5 25 50 100

# Week 7: Policy Service
./migrate_service.sh policy-service 1 5 25 50 100

# Week 8: AI Pipeline Service (slower rollout due to LLM dependency)
./migrate_service.sh ai-pipeline-service 1 5 10 25 50 75 100
# Progression: 1% → 5% → 10% → 25% → 50% → 75% → 100% over 7 days
```

**migrate_service.sh:**
```bash
#!/bin/bash
# migrate_service.sh <service_name> <step1_pct> <step2_pct> ...

SERVICE=$1
shift  # Remove first argument, leaving only traffic percentages

PREV_PCT=0
for TARGET_PCT in "$@"; do
  echo "=== Migrating ${SERVICE}: ${PREV_PCT}% → ${TARGET_PCT}% ==="

  # Shift traffic
  ./shift_traffic.sh ${SERVICE} ${PREV_PCT} ${TARGET_PCT}

  if [ $? -ne 0 ]; then
    echo "❌ Migration failed at ${TARGET_PCT}%. Aborting."
    exit 1
  fi

  # Soak time (longer for higher traffic percentages)
  if [ $TARGET_PCT -lt 10 ]; then
    SOAK_HOURS=24
  elif [ $TARGET_PCT -lt 50 ]; then
    SOAK_HOURS=48
  else
    SOAK_HOURS=72
  fi

  echo "Soaking for ${SOAK_HOURS} hours at ${TARGET_PCT}%..."
  sleep $((SOAK_HOURS * 3600))

  # Re-validate after soak
  ./validate_migration_step.sh ${SERVICE} ${TARGET_PCT}

  PREV_PCT=$TARGET_PCT
done

echo "✅ Migration complete for ${SERVICE}"
```

---

**Phase 5: Decommission Monolith (Week 9)**

**Objective**: Safely remove monolith after all services migrated to microservices.

**Pre-Decommission Checklist:**
```yaml
- All services at 100% microservice traffic: YES
- Monolith received 0 requests in past 7 days: YES
- Database migrations completed: YES
- Monolith-specific metrics removed from dashboards: YES
- Monolith container images archived: YES
- Rollback plan documented: YES
- Business approval obtained: YES
```

**Decommission Steps:**
1. Set monolith replicas to 1 (from 3)
2. Wait 48 hours, monitor for unexpected traffic
3. Set replicas to 0
4. Wait 7 days (keep deployment definition)
5. Delete deployment entirely
6. Archive Docker images to S3 (for emergency rollback)
7. Update documentation

**Decommission Script:**
```bash
#!/bin/bash
# decommission_monolith.sh

echo "=== Decommissioning ZTA Monolith ==="

# Step 1: Scale down to 1 replica
echo "Step 1/5: Scaling to 1 replica..."
kubectl scale deployment/zta-monolith -n zta-control-plane --replicas=1
sleep 48h  # 48-hour soak

# Step 2: Verify zero traffic
echo "Step 2/5: Verifying zero traffic..."
TRAFFIC=$(curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(zta_auth_token_issued_total{service_version=\"monolith\"}[24h]))" | jq -r '.data.result[0].value[1]')
if [ "$TRAFFIC" != "0" ]; then
  echo "❌ Monolith still receiving traffic: ${TRAFFIC} req/s. Aborting."
  exit 1
fi

# Step 3: Scale to zero
echo "Step 3/5: Scaling to 0 replicas..."
kubectl scale deployment/zta-monolith -n zta-control-plane --replicas=0
sleep 168h  # 7-day grace period

# Step 4: Archive images
echo "Step 4/5: Archiving container images..."
MONOLITH_IMAGE=$(kubectl get deployment/zta-monolith -n zta-control-plane -o jsonpath='{.spec.template.spec.containers[0].image}')
docker pull $MONOLITH_IMAGE
docker save $MONOLITH_IMAGE | gzip > zta-monolith-$(date +%Y%m%d).tar.gz
aws s3 cp zta-monolith-*.tar.gz s3://zta-backups/decommissioned-images/

# Step 5: Delete deployment
echo "Step 5/5: Deleting deployment..."
kubectl delete deployment/zta-monolith -n zta-control-plane

echo "✅ Monolith decommissioned successfully"
echo "Emergency rollback: docker load < zta-monolith-*.tar.gz && kubectl apply -f monolith-backup.yaml"
```

#### 10.1.4 Data Migration Strategy

**Database Schema Changes:**

The monolith uses a shared PostgreSQL database. Microservices will initially continue using the shared database, with optional future migration to per-service databases.

**Migration Approach: Shared Database (Recommended)**

```
Monolith (Week 0)              Microservices (Week 9)
     |                                  |
     v                                  v
 [PostgreSQL]  =============>      [PostgreSQL]
   Shared DB                         Shared DB

   Tables:                           Tables:
   - apps                            - apps (read/write by Policy Service)
   - mas                             - mas (read/write by Policy Service)
   - tools                           - tools (read/write by Policy Service)
   - tokens (audit)                  - tokens (write by Auth, read by Telemetry)
   - traces                          - traces (write by Telemetry)
```

**No schema changes required** if using shared database. Services coordinate via database transactions.

**Optional: Per-Service Databases (Advanced)**

If splitting databases, use this approach:

```sql
-- Week 10: Split databases (optional)
-- 1. Create separate databases
CREATE DATABASE zta_auth;
CREATE DATABASE zta_policy;
CREATE DATABASE zta_telemetry;

-- 2. Migrate tables
-- Auth Service: tokens audit table
CREATE TABLE zta_auth.tokens AS SELECT * FROM zta_shared.tokens;

-- Policy Service: apps, mas, tools, scopes
CREATE TABLE zta_policy.apps AS SELECT * FROM zta_shared.apps;
CREATE TABLE zta_policy.mas AS SELECT * FROM zta_shared.mas;

-- Telemetry: traces, events
CREATE TABLE zta_telemetry.traces AS SELECT * FROM zta_shared.traces;

-- 3. Enable logical replication (for gradual cutover)
ALTER TABLE zta_shared.apps REPLICA IDENTITY FULL;
CREATE PUBLICATION apps_pub FOR TABLE apps;

-- 4. Set up replication to zta_policy
CREATE SUBSCRIPTION apps_sub CONNECTION 'host=postgres port=5432 dbname=zta_shared' PUBLICATION apps_pub;
```

**Foreign Key Handling:**

If splitting databases, replace foreign keys with application-level checks:

```python
# Before (monolith): Database enforces FK
class Token(SQLModel):
    app_id: str = Field(foreign_key="apps.id")

# After (microservices): Application enforces FK
class TokenService:
    def create_token(self, app_id: str):
        # Validate app exists via Policy Service API
        app = await policy_service_client.get_app(app_id)
        if not app:
            raise AppNotFoundError(f"App {app_id} does not exist")

        # Create token
        token = Token(app_id=app_id)
        self.token_repository.save(token)
```

#### 10.1.5 Testing Strategy

**Test Pyramid:**

```
           /\
          /  \
         / E2E \ (10% of tests)
        /------\
       /        \
      / Contract \ (20% of tests)
     /------------\
    /              \
   /  Integration   \ (30% of tests)
  /------------------\
 /                    \
/       Unit           \ (40% of tests)
/______________________\
```

**Test Suite:**

**1. Unit Tests (40%)**
```python
# test_auth_service.py
def test_token_exchange_valid_request():
    auth_service = AuthService(mock_policy_service, mock_ai_pipeline)
    request = TokenExchangeRequest(app_id="agent-1", subject_token="valid-token")

    response = auth_service.exchange_token(request)

    assert response.access_token is not None
    assert response.token_type == "Bearer"

def test_token_exchange_invalid_app():
    auth_service = AuthService(mock_policy_service, mock_ai_pipeline)
    request = TokenExchangeRequest(app_id="non-existent", subject_token="valid-token")

    with pytest.raises(AppNotFoundError):
        auth_service.exchange_token(request)
```

**2. Integration Tests (30%)**
```python
# test_auth_service_integration.py
@pytest.mark.integration
def test_token_flow_with_real_database():
    # Use testcontainers for real PostgreSQL
    with PostgresContainer("postgres:15") as postgres:
        auth_service = AuthService(
            database_url=postgres.get_connection_url()
        )

        # Create app
        app = auth_service.create_app(name="test-agent", type="agent")

        # Generate token
        token = auth_service.generate_token(app_id=app.id, user_input="test task")

        # Exchange token
        exchanged = auth_service.exchange_token(
            app_id=app.id,
            subject_token=token,
            requested_tool="filesystem_read"
        )

        assert exchanged is not None
```

**3. Contract Tests (20%)**
```python
# test_auth_policy_contract.py
from pact import Consumer, Provider

pact = Consumer('AuthService').has_pact_with(Provider('PolicyService'))

def test_get_app_contract():
    (pact
     .given('app exists with id agent-1')
     .upon_receiving('a request for app details')
     .with_request('GET', '/apps/agent-1')
     .will_respond_with(200, body={
         'id': 'agent-1',
         'name': 'Test Agent',
         'type': 'agent',
         'mas_id': 'mas-1'
     }))

    with pact:
        policy_client = PolicyServiceClient('http://localhost:1234')
        app = policy_client.get_app('agent-1')
        assert app.id == 'agent-1'
```

**4. End-to-End Tests (10%)**
```python
# test_e2e_token_flow.py
@pytest.mark.e2e
def test_complete_token_flow():
    # Deploy full stack in test environment
    kubectl.apply('test-cluster-config.yaml')

    # User app gets token
    response = requests.post('https://user-app/start-task', json={'task': 'Read file'})
    assert response.status_code == 200

    # Agent exchanges token
    agent_response = requests.post('https://agent/execute', json={'token': response.json()['token']})
    assert agent_response.status_code == 200

    # MCP server validates token and executes
    mcp_response = requests.post('https://mcp-server/tools/call',
                                  json={'tool': 'filesystem_read'},
                                  headers={'Authorization': f'Bearer {agent_response.json()["delegated_token"]}'})
    assert mcp_response.status_code == 200
```

**5. Load Tests (Continuous)**
```javascript
// load_test.js (k6)
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 100 },   // Ramp up to 100 VUs
    { duration: '10m', target: 100 },  // Stay at 100 VUs
    { duration: '5m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],    // Error rate < 1%
  },
};

export default function () {
  // Generate token
  let tokenRes = http.post('https://zta-auth-service/oauth/token', JSON.stringify({
    client_id: 'test-client',
    client_secret: 'test-secret',
    user_input: 'Read file /etc/passwd'
  }), { headers: { 'Content-Type': 'application/json' } });

  check(tokenRes, {
    'token generated': (r) => r.status === 200,
    'token has access_token': (r) => r.json('access_token') !== undefined,
  });

  let token = tokenRes.json('access_token');

  // Exchange token
  let exchangeRes = http.post('https://zta-auth-service/oauth/token/exchange', JSON.stringify({
    subject_token: token,
    requested_tool: 'filesystem_read'
  }), { headers: { 'Content-Type': 'application/json' } });

  check(exchangeRes, {
    'token exchanged': (r) => r.status === 200,
  });

  sleep(1);
}
```

**Run Load Test:**
```bash
# Baseline (before migration)
k6 run --out json=baseline.json load_test.js

# During migration (per phase)
k6 run --out json=phase2_5pct.json load_test.js

# Compare results
k6 inspect baseline.json phase2_5pct.json
```

#### 10.1.6 Rollback Procedures

**Rollback Decision Matrix:**

| Trigger | Severity | Rollback Speed | Procedure |
|---------|----------|----------------|-----------|
| Error rate > 5% | Critical | Immediate (< 1 min) | Automated traffic shift to 0% |
| P95 latency > 2x baseline | High | Fast (< 5 min) | Automated traffic shift to 0% |
| Database deadlock | High | Fast (< 5 min) | Manual: Scale down microservice |
| Memory leak detected | Medium | Gradual (< 30 min) | Manual: Restart pods, shift traffic |
| Business logic bug | Medium | Gradual (< 60 min) | Manual: Deploy hotfix or rollback |
| User complaints (no metrics) | Low | Slow (< 4 hours) | Investigate, then decide |

**Automated Rollback (Error Rate):**
```python
# rollback_monitor.py
import time
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url="http://prometheus:9090", disable_ssl=True)

def check_error_rate(service, threshold=0.05):
    query = f'''
    (
      sum(rate(zta_auth_token_exchanged_total{{service_version="microservice", result="failed"}}[5m]))
      /
      sum(rate(zta_auth_token_exchanged_total{{service_version="microservice"}}[5m]))
    )
    '''
    result = prom.custom_query(query)

    if result and len(result) > 0:
        error_rate = float(result[0]['value'][1])
        if error_rate > threshold:
            return error_rate
    return 0

def rollback(service, reason):
    print(f"🚨 ROLLBACK TRIGGERED: {reason}")

    # Update feature flag to 0%
    requests.patch(f'http://feature-flags:8080/api/flags/{service}',
                   json={'traffic_split': {'microservice': 0, 'monolith': 100}})

    # Update Envoy config
    requests.post(f'http://envoy-admin:19000/update_route_weights',
                  json={'service': service, 'weights': {'monolith': 100, 'microservice': 0}})

    # Trigger PagerDuty alert
    requests.post('https://events.pagerduty.com/v2/enqueue', json={
        'routing_key': os.getenv('PAGERDUTY_KEY'),
        'event_action': 'trigger',
        'payload': {
            'summary': f'Migration rollback: {service}',
            'severity': 'critical',
            'source': 'migration-monitor',
            'custom_details': {'reason': reason}
        }
    })

while True:
    for service in ['auth-service-v2', 'policy-service-v2', 'ai-pipeline-v2']:
        error_rate = check_error_rate(service)
        if error_rate > 0.05:
            rollback(service, f'Error rate {error_rate:.2%} > 5%')

    time.sleep(30)  # Check every 30 seconds
```

**Manual Rollback Runbook:**
```bash
# RUNBOOK: Emergency Rollback

## Symptoms
- User reports of failures
- High error rate in Grafana
- PagerDuty alert

## Step 1: Identify affected service
kubectl get pods -n zta-control-plane -l migration-phase=active
# Look for CrashLoopBackOff or high restart count

## Step 2: Check recent deployments
kubectl rollout history deployment/zta-auth-service -n zta-control-plane

## Step 3: Rollback traffic (FAST)
# Option A: Feature flag (preferred)
curl -X PATCH http://feature-flags:8080/api/flags/auth-service-v2 \
  -d '{"traffic_split": {"microservice": 0, "monolith": 100}}'

# Option B: Helm rollback
helm rollback zta-mas-system -n zta-control-plane

# Option C: kubectl rollout undo
kubectl rollout undo deployment/zta-auth-service -n zta-control-plane

## Step 4: Verify rollback
# Check traffic shifted
curl -s http://prometheus:9090/api/v1/query?query='sum(rate(zta_auth_token_issued_total{service_version="microservice"}[1m]))'
# Should return 0

# Check error rate decreased
curl -s http://prometheus:9090/api/v1/query?query='sum(rate(zta_auth_token_exchanged_total{result="failed"}[5m])) / sum(rate(zta_auth_token_exchanged_total[5m]))'

## Step 5: Root cause analysis (post-incident)
kubectl logs -n zta-control-plane deployment/zta-auth-service --previous --tail=1000 > incident.log
# Analyze logs, identify bug, create Jira ticket
```

#### 10.1.7 Success Criteria

**Migration Complete When:**

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| All services migrated | 100% | `kubectl get deployment -n zta-control-plane -l app=monolith` returns 0 pods |
| Error rate unchanged | < 1% regression | Compare 7-day average before/after |
| Latency unchanged | < 10% regression | P95 latency before/after |
| Zero downtime | 0 seconds | No 5xx errors during migration |
| Cost neutral or lower | <= $1000/month increase | AWS Cost Explorer |
| Team velocity maintained | >= baseline | Sprint velocity (story points) |
| Rollback capability proven | < 5 minutes | Test rollback in staging |
| Documentation complete | 100% | All runbooks written and reviewed |

**Post-Migration Validation:**
```bash
#!/bin/bash
# post_migration_validation.sh

echo "=== Post-Migration Validation ==="

# 1. Verify monolith decommissioned
MONOLITH_PODS=$(kubectl get pods -n zta-control-plane -l app=zta-monolith --no-headers | wc -l)
if [ $MONOLITH_PODS -ne 0 ]; then
  echo "❌ Monolith still running: ${MONOLITH_PODS} pods"
  exit 1
fi
echo "✅ Monolith decommissioned"

# 2. Compare error rates (7-day average)
BEFORE_ERROR_RATE=0.008  # From baseline
AFTER_ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(zta_auth_token_exchanged_total{result=\"failed\"}[7d])) / sum(rate(zta_auth_token_exchanged_total[7d]))" | jq -r '.data.result[0].value[1]')

DIFF=$(echo "$AFTER_ERROR_RATE - $BEFORE_ERROR_RATE" | bc)
if (( $(echo "$DIFF > 0.001" | bc -l) )); then
  echo "❌ Error rate regression: ${DIFF} (${AFTER_ERROR_RATE} vs ${BEFORE_ERROR_RATE})"
  exit 1
fi
echo "✅ Error rate maintained: ${AFTER_ERROR_RATE}"

# 3. Compare latency (7-day P95)
BEFORE_LATENCY=0.35  # From baseline
AFTER_LATENCY=$(curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, rate(zta_auth_token_exchange_duration_seconds_bucket[7d]))" | jq -r '.data.result[0].value[1]')

LATENCY_DIFF=$(echo "$AFTER_LATENCY - $BEFORE_LATENCY" | bc)
if (( $(echo "$LATENCY_DIFF > 0.035" | bc -l) )); then
  echo "❌ Latency regression: ${LATENCY_DIFF}s (${AFTER_LATENCY}s vs ${BEFORE_LATENCY}s)"
  exit 1
fi
echo "✅ Latency maintained: ${AFTER_LATENCY}s"

# 4. Verify all microservices healthy
UNHEALTHY=$(kubectl get pods -n zta-control-plane -l tier=control-plane --field-selector=status.phase!=Running --no-headers | wc -l)
if [ $UNHEALTHY -ne 0 ]; then
  echo "❌ Unhealthy pods detected: ${UNHEALTHY}"
  kubectl get pods -n zta-control-plane -l tier=control-plane --field-selector=status.phase!=Running
  exit 1
fi
echo "✅ All pods healthy"

# 5. Smoke test end-to-end flow
./smoke_test.sh
if [ $? -ne 0 ]; then
  echo "❌ Smoke test failed"
  exit 1
fi
echo "✅ Smoke test passed"

echo ""
echo "========================================="
echo "✅ MIGRATION VALIDATION SUCCESSFUL"
echo "========================================="
echo "All criteria met. Migration complete."
```

---



### 10.2 Performance Testing & Capacity Planning

This section provides comprehensive performance testing strategies, load testing scripts, capacity planning formulas, and autoscaling configurations for the ZTA-MAS system.

#### 10.2.1 Performance Testing Strategy

**Testing Pyramid:**

```mermaid
graph TB
    subgraph "Performance Testing Layers"
        CHAOS[Chaos Testing<br/>5% - Break things intentionally]
        STRESS[Stress Testing<br/>10% - Beyond capacity]
        LOAD[Load Testing<br/>30% - Expected capacity]
        SOAK[Soak Testing<br/>30% - Sustained load]
        SMOKE[Smoke Testing<br/>25% - Basic functionality]
    end

    SMOKE --> SOAK
    SOAK --> LOAD
    LOAD --> STRESS
    STRESS --> CHAOS
```

**Test Types:**

| Test Type | Purpose | Duration | Frequency | Trigger |
|-----------|---------|----------|-----------|---------|
| Smoke Test | Verify basic functionality | 5 minutes | Every commit | CI pipeline |
| Soak Test | Detect memory leaks, resource exhaustion | 24 hours | Weekly | Scheduled |
| Load Test | Validate expected capacity | 30 minutes | Every release | Pre-deployment |
| Stress Test | Find breaking point | 1 hour | Monthly | Capacity planning |
| Spike Test | Validate autoscaling | 15 minutes | Every release | Pre-deployment |
| Chaos Test | Validate resilience | 2 hours | Monthly | Scheduled |

#### 10.2.2 Load Testing with k6

**k6 Test Suite Structure:**
```
load-tests/
├── smoke/
│   ├── token_generation.js
│   └── token_exchange.js
├── load/
│   ├── normal_load.js
│   ├── peak_load.js
│   └── sustained_load.js
├── stress/
│   ├── breaking_point.js
│   └── spike_test.js
├── soak/
│   └── long_running.js
├── scenarios/
│   ├── user_journey.js
│   └── agent_workflow.js
├── lib/
│   ├── config.js
│   ├── helpers.js
│   └── assertions.js
└── k6.config.js
```

**Smoke Test (token_generation.js):**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const tokenGenDuration = new Trend('token_generation_duration');

export const options = {
  vus: 10,
  duration: '5m',
  thresholds: {
    http_req_duration: ['p(95)<200'],  // 95% of requests < 200ms
    http_req_failed: ['rate<0.01'],    // Error rate < 1%
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://zta-auth-service.zta-control-plane.svc.cluster.local:8443';

export default function () {
  const payload = JSON.stringify({
    client_id: 'test-client-' + __VU,
    client_secret: 'test-secret',
    user_input: 'Read file /etc/passwd',
    grant_type: 'client_credentials'
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const startTime = new Date();
  const response = http.post(`${BASE_URL}/oauth/token`, payload, params);
  const endTime = new Date();

  tokenGenDuration.add(endTime - startTime);

  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'has access_token': (r) => r.json('access_token') !== undefined,
    'token is JWT': (r) => {
      const token = r.json('access_token');
      return token && token.split('.').length === 3;
    },
    'response time < 200ms': (r) => r.timings.duration < 200,
  });

  errorRate.add(!success);

  if (!success) {
    console.error(`Request failed: ${response.status} ${response.body}`);
  }

  sleep(1);
}

export function handleSummary(data) {
  return {
    'stdout': JSON.stringify(data, null, 2),
    'summary.json': JSON.stringify(data),
  };
}
```

**Load Test (normal_load.js):**
```javascript
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Counter, Trend } from 'k6/metrics';
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const tokenGenCounter = new Counter('tokens_generated');
const tokenExchangeCounter = new Counter('tokens_exchanged');
const toolCheckCounter = new Counter('tool_checks_performed');
const aiCheckDuration = new Trend('ai_check_duration');

export const options = {
  stages: [
    { duration: '2m', target: 50 },    // Ramp-up
    { duration: '5m', target: 50 },    // Stay at 50 VUs
    { duration: '2m', target: 100 },   // Ramp to 100
    { duration: '10m', target: 100 },  // Stay at 100
    { duration: '2m', target: 200 },   // Ramp to 200
    { duration: '10m', target: 200 },  // Peak load
    { duration: '5m', target: 0 },     // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    'group_duration{group:::token_generation}': ['p(95)<200'],
    'group_duration{group:::token_exchange}': ['p(95)<500'],
    'group_duration{group:::token_exchange_with_ai}': ['p(95)<2000'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://zta-auth-service.zta-control-plane.svc.cluster.local:8443';
const ENABLE_AI_CHECKS = __ENV.ENABLE_AI_CHECKS === 'true';

export default function () {
  let accessToken;

  // Scenario 1: Generate token (70% of traffic)
  group('token_generation', function () {
    const response = http.post(`${BASE_URL}/oauth/token`, JSON.stringify({
      client_id: `test-client-${__VU}`,
      client_secret: 'test-secret',
      user_input: `Task ${randomString(20)}`,
      grant_type: 'client_credentials'
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    check(response, {
      'token generated': (r) => r.status === 200,
      'has access_token': (r) => r.json('access_token') !== undefined,
    });

    if (response.status === 200) {
      accessToken = response.json('access_token');
      tokenGenCounter.add(1);
    }
  });

  if (!accessToken) {
    sleep(1);
    return;
  }

  sleep(randomIntBetween(1, 3));

  // Scenario 2: Exchange token (30% involves AI check)
  const useAiCheck = ENABLE_AI_CHECKS && Math.random() < 0.3;
  const groupName = useAiCheck ? 'token_exchange_with_ai' : 'token_exchange';

  group(groupName, function () {
    const toolName = ['filesystem_read', 'filesystem_write', 'database_query', 'api_call'][randomIntBetween(0, 3)];

    const startTime = new Date();
    const response = http.post(`${BASE_URL}/oauth/token/exchange`, JSON.stringify({
      grant_type: 'urn:ietf:params:oauth:grant-type:token-exchange',
      subject_token: accessToken,
      subject_token_type: 'urn:ietf:params:oauth:token-type:access_token',
      requested_tool: toolName,
      actor_id: `agent-${__VU}`,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    const endTime = new Date();

    const success = check(response, {
      'token exchanged': (r) => r.status === 200 || r.status === 403,
      'has response': (r) => r.body.length > 0,
    });

    if (success) {
      tokenExchangeCounter.add(1);
      if (useAiCheck) {
        aiCheckDuration.add(endTime - startTime);
        toolCheckCounter.add(1);
      }
    }
  });

  sleep(randomIntBetween(1, 5));
}

export function handleSummary(data) {
  const summary = {
    duration: data.state.testRunDurationMs / 1000,
    vus_max: data.metrics.vus_max.values.max,
    iterations: data.metrics.iterations.values.count,
    tokens_generated: data.metrics.tokens_generated.values.count,
    tokens_exchanged: data.metrics.tokens_exchanged.values.count,
    tool_checks: data.metrics.tool_checks_performed.values.count,
    http_req_duration_p95: data.metrics.http_req_duration.values['p(95)'],
    http_req_duration_p99: data.metrics.http_req_duration.values['p(99)'],
    http_req_failed_rate: data.metrics.http_req_failed.values.rate,
    requests_per_second: data.metrics.http_reqs.values.rate,
  };

  console.log('\n=== Load Test Summary ===');
  console.log(`Duration: ${summary.duration}s`);
  console.log(`Max VUs: ${summary.vus_max}`);
  console.log(`Total Iterations: ${summary.iterations}`);
  console.log(`Tokens Generated: ${summary.tokens_generated}`);
  console.log(`Tokens Exchanged: ${summary.tokens_exchanged}`);
  console.log(`Tool Checks: ${summary.tool_checks}`);
  console.log(`P95 Latency: ${summary.http_req_duration_p95}ms`);
  console.log(`P99 Latency: ${summary.http_req_duration_p99}ms`);
  console.log(`Error Rate: ${(summary.http_req_failed_rate * 100).toFixed(2)}%`);
  console.log(`Requests/sec: ${summary.requests_per_second.toFixed(2)}`);

  return {
    'stdout': JSON.stringify(data, null, 2),
    'summary.json': JSON.stringify(summary),
    'results.html': htmlReport(data),
  };
}

function htmlReport(data) {
  // Generate HTML report (simplified)
  return `
<!DOCTYPE html>
<html>
<head>
  <title>ZTA Load Test Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #4CAF50; color: white; }
    .pass { color: green; }
    .fail { color: red; }
  </style>
</head>
<body>
  <h1>ZTA Load Test Report</h1>
  <p>Timestamp: ${new Date().toISOString()}</p>
  <table>
    <tr><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
    <tr>
      <td>P95 Latency</td>
      <td>${data.metrics.http_req_duration.values['p(95)']}ms</td>
      <td>&lt; 500ms</td>
      <td class="${data.metrics.http_req_duration.values['p(95)'] < 500 ? 'pass' : 'fail'}">
        ${data.metrics.http_req_duration.values['p(95)'] < 500 ? '✓ PASS' : '✗ FAIL'}
      </td>
    </tr>
    <tr>
      <td>Error Rate</td>
      <td>${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%</td>
      <td>&lt; 1%</td>
      <td class="${data.metrics.http_req_failed.values.rate < 0.01 ? 'pass' : 'fail'}">
        ${data.metrics.http_req_failed.values.rate < 0.01 ? '✓ PASS' : '✗ FAIL'}
      </td>
    </tr>
  </table>
</body>
</html>
  `;
}
```

**Stress Test (breaking_point.js):**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },
    { duration: '5m', target: 300 },
    { duration: '2m', target: 400 },  // Push to breaking point
    { duration: '5m', target: 400 },
    { duration: '10m', target: 0 },
  ],
  thresholds: {
    // Relaxed thresholds - expect some failures
    http_req_failed: ['rate<0.1'],  // Allow up to 10% errors
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://zta-auth-service.zta-control-plane.svc.cluster.local:8443';

export default function () {
  const response = http.post(`${BASE_URL}/oauth/token`, JSON.stringify({
    client_id: `stress-test-${__VU}`,
    client_secret: 'test-secret',
    user_input: 'Stress test task',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(response, {
    'status is 200 or 429 or 503': (r) => [200, 429, 503].includes(r.status),
  });

  sleep(0.1);  // Minimal sleep to maximize load
}

export function handleSummary(data) {
  const maxRPS = Math.max(...data.metrics.http_reqs.values.rate);
  const errorRate = data.metrics.http_req_failed.values.rate;
  const p99Latency = data.metrics.http_req_duration.values['p(99)'];

  console.log('\n=== Stress Test Summary ===');
  console.log(`Breaking Point:`);
  console.log(`  Max RPS before degradation: ${maxRPS.toFixed(0)}`);
  console.log(`  Error rate at peak: ${(errorRate * 100).toFixed(2)}%`);
  console.log(`  P99 latency at peak: ${p99Latency}ms`);
  console.log(`\nRecommendation:`);
  console.log(`  Safe operating capacity: ${(maxRPS * 0.7).toFixed(0)} RPS (70% of max)`);

  return {
    'stress_test_summary.json': JSON.stringify({
      breaking_point_rps: maxRPS,
      safe_capacity_rps: maxRPS * 0.7,
      error_rate_at_peak: errorRate,
      p99_latency_at_peak: p99Latency,
    }),
  };
}
```

**Soak Test (long_running.js):**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 50 },
    { duration: '24h', target: 50 },  // Sustained load for 24 hours
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://zta-auth-service.zta-control-plane.svc.cluster.local:8443';

export default function () {
  const response = http.post(`${BASE_URL}/oauth/token`, JSON.stringify({
    client_id: `soak-test-${__VU}`,
    client_secret: 'test-secret',
    user_input: 'Soak test task',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(5);  // Realistic think time
}

export function handleSummary(data) {
  // Check for memory leaks (increasing latency over time)
  const durationHours = data.state.testRunDurationMs / (1000 * 60 * 60);
  const p95Latency = data.metrics.http_req_duration.values['p(95)'];

  console.log('\n=== Soak Test Summary ===');
  console.log(`Duration: ${durationHours.toFixed(1)} hours`);
  console.log(`P95 Latency: ${p95Latency}ms`);
  console.log(`\nMemory Leak Check:`);
  console.log(`  Expected: Latency stable over time`);
  console.log(`  Actual: ${p95Latency < 600 ? '✓ PASS - No degradation' : '✗ FAIL - Latency increased'}`);

  return {
    'soak_test_summary.json': JSON.stringify(data),
  };
}
```

#### 10.2.3 Performance Regression Testing

**CI/CD Integration:**

```yaml
# .github/workflows/performance-test.yml
name: Performance Regression Test

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  performance-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up k6
      run: |
        curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -L | tar xvz
        sudo mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/

    - name: Deploy to test cluster
      run: |
        kubectl apply -k test/k8s/
        kubectl wait --for=condition=ready pod -l app=zta-auth-service -n zta-control-plane --timeout=300s

    - name: Run baseline test
      run: |
        k6 run --out json=baseline.json load-tests/smoke/token_generation.js

    - name: Download previous baseline
      uses: actions/download-artifact@v3
      with:
        name: baseline
        path: previous/
      continue-on-error: true

    - name: Compare results
      run: |
        python3 scripts/compare_performance.py previous/baseline.json baseline.json > comparison.txt
        cat comparison.txt

    - name: Check for regression
      run: |
        REGRESSION=$(python3 scripts/check_regression.py comparison.txt)
        if [ "$REGRESSION" = "true" ]; then
          echo "❌ Performance regression detected!"
          cat comparison.txt
          exit 1
        fi

    - name: Upload baseline
      uses: actions/upload-artifact@v3
      with:
        name: baseline
        path: baseline.json

    - name: Comment PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const comparison = fs.readFileSync('comparison.txt', 'utf8');
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## Performance Test Results\n\n\`\`\`\n${comparison}\n\`\`\``,
          });
```

**Comparison Script (compare_performance.py):**
```python
#!/usr/bin/env python3
import json
import sys

def compare_performance(previous_file, current_file):
    with open(previous_file, 'r') as f:
        previous = json.load(f)
    with open(current_file, 'r') as f:
        current = json.load(f)

    metrics = {
        'p95_latency': {
            'previous': previous['metrics']['http_req_duration']['values']['p(95)'],
            'current': current['metrics']['http_req_duration']['values']['p(95)'],
            'threshold': 0.1,  # 10% regression
            'unit': 'ms'
        },
        'error_rate': {
            'previous': previous['metrics']['http_req_failed']['values']['rate'],
            'current': current['metrics']['http_req_failed']['values']['rate'],
            'threshold': 0.01,  # 1% absolute increase
            'unit': '%',
            'multiplier': 100
        },
        'throughput': {
            'previous': previous['metrics']['http_reqs']['values']['rate'],
            'current': current['metrics']['http_reqs']['values']['rate'],
            'threshold': -0.1,  # Allow 10% decrease
            'unit': 'req/s'
        }
    }

    print("Performance Comparison Report")
    print("=" * 80)

    regressions = []

    for name, data in metrics.items():
        prev = data['previous']
        curr = data['current']
        threshold = data['threshold']

        if 'multiplier' in data:
            prev *= data['multiplier']
            curr *= data['multiplier']

        change = (curr - prev) / prev if prev > 0 else 0

        status = '✓' if abs(change) <= abs(threshold) else '✗'
        if status == '✗':
            regressions.append(name)

        print(f"\n{name.replace('_', ' ').title()}:")
        print(f"  Previous: {prev:.2f} {data['unit']}")
        print(f"  Current:  {curr:.2f} {data['unit']}")
        print(f"  Change:   {change*100:+.2f}% ({status})")
        print(f"  Threshold: {threshold*100:.0f}%")

    print("\n" + "=" * 80)

    if regressions:
        print(f"❌ REGRESSION DETECTED in: {', '.join(regressions)}")
        return False
    else:
        print("✅ NO REGRESSION - Performance maintained or improved")
        return True

if __name__ == '__main__':
    result = compare_performance(sys.argv[1], sys.argv[2])
    sys.exit(0 if result else 1)
```

#### 10.2.4 Capacity Planning Formulas

**Component Sizing Formulas:**

**1. Auth Service:**
```
Replicas = ceil(Target_TPS / TPS_per_replica) * Safety_Factor

Where:
  TPS_per_replica = 500 (measured)
  Safety_Factor = 1.5 (50% headroom)

Example:
  Target: 2000 TPS
  Replicas = ceil(2000 / 500) * 1.5 = 4 * 1.5 = 6 replicas

CPU per replica = Base_CPU + (TPS * CPU_per_request)
  Base_CPU = 500m
  CPU_per_request = 1m

  @ 500 TPS: CPU = 500m + (500 * 1m) = 1000m (1 CPU core)

Memory per replica = Base_Memory + (Cache_entries * Memory_per_entry)
  Base_Memory = 512Mi
  Memory_per_entry = 1Ki
  Cache_entries = Token_rate * TTL

  @ 500 TPS with 30s TTL: Cache = 500 * 30 = 15000 entries
  Memory = 512Mi + (15000 * 1Ki) = 512Mi + 15Mi = 527Mi
```

**2. AI Pipeline Service:**
```
Replicas = ceil(AI_checks_per_sec / Checks_per_replica) * Safety_Factor

Where:
  Checks_per_replica = 50/sec (LLM bottleneck)
  Safety_Factor = 2.0 (100% headroom due to external dependency)

Example:
  Target: 200 AI checks/sec
  Replicas = ceil(200 / 50) * 2.0 = 4 * 2 = 8 replicas

CPU per replica = 2000m (constant due to LLM API calls)
Memory per replica = 4Gi (embeddings cache)
```

**3. Sidecar Overhead:**
```
Sidecar_CPU = Base_CPU + (Request_rate * CPU_per_request)
  Base_CPU = 100m
  CPU_per_request = 0.1m

  @ 10 req/sec: CPU = 100m + (10 * 0.1m) = 101m
  @ 100 req/sec: CPU = 100m + (100 * 0.1m) = 110m

Sidecar_Memory = Base_Memory + (Cached_tokens * Memory_per_token)
  Base_Memory = 128Mi
  Memory_per_token = 1Ki

  @ 1000 cached tokens: Memory = 128Mi + (1000 * 1Ki) = 129Mi
```

**4. PostgreSQL:**
```
Required_IOPS = (Writes_per_sec + Reads_per_sec) * IOPS_per_query
  IOPS_per_query = 10 (average)

Example:
  Writes: 500/sec, Reads: 2000/sec
  IOPS = (500 + 2000) * 10 = 25,000 IOPS

  Storage: Use gp3 with 16,000 baseline + provisioned 9,000 = 25,000 IOPS

Connections = Active_services * Connections_per_service
  Active_services = 15 (5 control plane services * 3 replicas)
  Connections_per_service = 10 (connection pool)

  Total = 15 * 10 = 150 connections

  PostgreSQL max_connections should be set to 200 (33% headroom)
```

**5. Cluster Node Sizing:**
```
Total_Pods = Control_plane_pods + Data_plane_pods + Observability_pods

Control_plane_pods:
  - Auth Service: 6 replicas
  - Policy Service: 3 replicas
  - AI Pipeline: 8 replicas
  - Telemetry: 5 replicas
  - Discovery: 2 replicas
  - Keycloak: 3 replicas
  - PostgreSQL: 3 replicas (HA)
  - Redis: 3 replicas
  Total: 33 pods

Data_plane_pods:
  - Application workloads: 1000 pods (each with sidecar)

Observability_pods:
  - Prometheus: 2 replicas
  - Grafana: 2 replicas
  - Loki: 5 replicas
  - Tempo: 3 replicas
  Total: 12 pods

Grand Total: 33 + 1000 + 12 = 1045 pods

Node Count = ceil(Total_Pods / Pods_per_node) * Safety_Factor
  Pods_per_node = 110 (k8s max) - 20 (system pods) = 90
  Safety_Factor = 1.3 (30% headroom)

  Nodes = ceil(1045 / 90) * 1.3 = 12 * 1.3 = 16 nodes

Node Type: m5.2xlarge (8 vCPU, 32GB RAM)
  - Cost: $0.384/hour * 16 nodes * 730 hours/month = $4,482/month
```

#### 10.2.5 Horizontal Pod Autoscaler (HPA) Configurations

**Auth Service HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: zta-auth-service-hpa
  namespace: zta-control-plane
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: zta-auth-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  # Scale on CPU
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Scale on memory
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  # Scale on custom metric (token rate)
  - type: Pods
    pods:
      metric:
        name: zta_auth_token_issued_total
      target:
        type: AverageValue
        averageValue: "400"  # 400 tokens/sec per pod

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max

    scaleDown:
      stabilizationWindowSeconds: 300  # 5 min cooldown
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      selectPolicy: Min
```

**AI Pipeline HPA (with external LLM metric):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: zta-ai-pipeline-hpa
  namespace: zta-control-plane
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: zta-ai-pipeline-service
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: Pods
    pods:
      metric:
        name: zta_ai_matcher_duration_seconds
      target:
        type: AverageValue
        averageValue: "1000m"  # 1 second average latency

  - type: External
    external:
      metric:
        name: openai_api_latency_seconds
        selector:
          matchLabels:
            service: openai
      target:
        type: AverageValue
        averageValue: "500m"  # Scale up if LLM API slow

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30  # Fast scale-up
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 5
        periodSeconds: 30
      selectPolicy: Max

    scaleDown:
      stabilizationWindowSeconds: 600  # Slow scale-down (10 min)
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
      selectPolicy: Min
```

**Sidecar HPA (via DaemonSet scaling - not typical, but for illustration):**

Since sidecars are injected per-pod, we don't HPA them directly. Instead, we use **Cluster Autoscaler** to add nodes when pod density increases.

**Cluster Autoscaler Configuration:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-config
  namespace: kube-system
data:
  config.yaml: |
    scaleDownEnabled: true
    scaleDownDelayAfterAdd: 10m
    scaleDownDelayAfterDelete: 10s
    scaleDownDelayAfterFailure: 3m
    scaleDownUnneededTime: 10m
    scaleDownUtilizationThreshold: 0.5
    skipNodesWithLocalStorage: false
    skipNodesWithSystemPods: true
    maxNodeProvisionTime: 15m

    nodeGroups:
    - name: zta-worker-nodes
      minSize: 10
      maxSize: 50
      targetSize: 15
```

#### 10.2.6 Vertical Pod Autoscaler (VPA) Recommendations

**VPA for Control Plane Services:**
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: zta-auth-service-vpa
  namespace: zta-control-plane
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: zta-auth-service
  updatePolicy:
    updateMode: "Auto"  # Or "Recreate" for StatefulSets
  resourcePolicy:
    containerPolicies:
    - containerName: zta-auth-service
      minAllowed:
        cpu: 500m
        memory: 512Mi
      maxAllowed:
        cpu: 4000m
        memory: 8Gi
      controlledResources: ["cpu", "memory"]
      mode: Auto
```

**VPA Recommendations Viewer:**
```bash
# Get VPA recommendations
kubectl describe vpa zta-auth-service-vpa -n zta-control-plane

# Output example:
# Recommendation:
#   Container Recommendations:
#     Container Name: zta-auth-service
#     Lower Bound:
#       Cpu:     800m
#       Memory:  1Gi
#     Target:
#       Cpu:     1200m
#       Memory:  1.5Gi
#     Uncapped Target:
#       Cpu:     1500m
#       Memory:  2Gi
#     Upper Bound:
#       Cpu:     2000m
#       Memory:  4Gi
```

#### 10.2.7 Performance Benchmarks & Targets

**Latency Targets (SLA):**

| Operation | P50 | P95 | P99 | Max Acceptable |
|-----------|-----|-----|-----|----------------|
| Token Generation | 50ms | 150ms | 250ms | 500ms |
| Token Exchange (no AI) | 100ms | 300ms | 500ms | 1000ms |
| Token Exchange (with AI) | 500ms | 1500ms | 2500ms | 5000ms |
| Token Introspection (cached) | 5ms | 10ms | 20ms | 50ms |
| Token Introspection (uncached) | 30ms | 80ms | 150ms | 300ms |
| MCP Tool Call | 200ms | 600ms | 1000ms | 2000ms |

**Throughput Targets:**

| Component | Target RPS | Measured Max | Safety Margin |
|-----------|-----------|--------------|---------------|
| Auth Service (per replica) | 400 | 500 | 25% |
| Policy Service (per replica) | 1600 | 2000 | 25% |
| AI Pipeline (per replica) | 40 | 50 | 25% |
| Telemetry (per replica) | 8000 | 10000 | 25% |
| Sidecar (per pod) | 80 | 100 | 25% |

**Resource Utilization Targets:**

| Resource | Target Utilization | Alert Threshold | Critical Threshold |
|----------|-------------------|-----------------|-------------------|
| CPU | 60-70% | >80% | >90% |
| Memory | 60-70% | >85% | >95% |
| Disk IOPS | 50-60% | >80% | >90% |
| Network Bandwidth | 40-50% | >70% | >85% |
| PostgreSQL Connections | 50-60% | >80% | >90% |

**Scalability Targets:**

| Metric | 100 pods | 500 pods | 1000 pods | 5000 pods |
|--------|----------|----------|-----------|-----------|
| Token Generation Rate | 500/sec | 2500/sec | 5000/sec | 25000/sec |
| Control Plane Nodes | 3 | 5 | 10 | 30 |
| Worker Nodes | 5 | 15 | 30 | 150 |
| PostgreSQL Storage | 50GB | 200GB | 500GB | 2TB |
| Monthly Cost (AWS) | $2k | $8k | $15k | $70k |

#### 10.2.8 Chaos Engineering Tests

**Chaos Test Scenarios:**

```yaml
# chaos-test-suite.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Workflow
metadata:
  name: zta-chaos-test-suite
  namespace: chaos-testing
spec:
  entry: entry
  templates:
  - name: entry
    templateType: Serial
    children:
    - pod-failure-test
    - network-delay-test
    - cpu-stress-test
    - database-failure-test

  - name: pod-failure-test
    templateType: PodChaos
    deadline: 10m
    podChaos:
      action: pod-kill
      mode: one
      selector:
        namespaces:
        - zta-control-plane
        labelSelectors:
          app: zta-auth-service
      duration: 30s

  - name: network-delay-test
    templateType: NetworkChaos
    deadline: 15m
    networkChaos:
      action: delay
      mode: all
      selector:
        namespaces:
        - zta-control-plane
        labelSelectors:
          app: zta-auth-service
      delay:
        latency: "100ms"
        correlation: "50"
        jitter: "50ms"
      duration: 10m

  - name: cpu-stress-test
    templateType: StressChaos
    deadline: 10m
    stressChaos:
      mode: one
      selector:
        namespaces:
        - zta-control-plane
        labelSelectors:
          app: zta-ai-pipeline-service
      stressors:
        cpu:
          workers: 4
          load: 80
      duration: 5m

  - name: database-failure-test
    templateType: PodChaos
    deadline: 5m
    podChaos:
      action: pod-failure
      mode: one
      selector:
        namespaces:
        - zta-control-plane
        labelSelectors:
          app: postgresql
      duration: 2m
```

**Run Chaos Tests:**
```bash
# Install Chaos Mesh
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh --namespace=chaos-testing --create-namespace

# Run chaos suite
kubectl apply -f chaos-test-suite.yaml

# Monitor during chaos
watch kubectl get pods -n zta-control-plane

# Verify resilience
kubectl logs -n chaos-testing -l app=chaos-test-monitor
```

---



### Phase 1: Control Plane Foundation (Weeks 1-4)

**Goals:**
- Deploy monolithic ZTA server to Kubernetes
- Integrate with Keycloak and PostgreSQL
- Validate token flows in cluster

**Deliverables:**
1. Helm chart for monolithic ZTA server
2. CiliumNetworkPolicy for control plane isolation
3. PostgreSQL StatefulSet with backup automation
4. Keycloak StatefulSet with admin realm
5. End-to-end test: User app → ZTA → Keycloak → Token

**Success Criteria:**
- ZTA server handles 100 tokens/sec
- Zero downtime during pod restarts
- Audit logs persisted to PostgreSQL

---

### Phase 2: Sidecar Injection (Weeks 5-8)

**Goals:**
- Build and deploy ZTA sidecar proxy
- Implement mutating webhook for injection
- Validate L7 protocol enforcement

**Deliverables:**
1. ZTA sidecar container image (Envoy-based or custom)
2. Mutating webhook for sidecar injection
3. Init container for iptables configuration
4. Sidecar ConfigMap and DaemonSet (if needed)
5. End-to-end test: Agent → Sidecar → MCP server

**Success Criteria:**
- Sidecars auto-inject on pods with `zta.io/enabled=true`
- Sidecars enforce MCP protocol (block HTTP to non-MCP endpoints)
- Sidecar cache reduces control plane load by 80%

---

### Phase 3: eBPF Network Enforcement (Weeks 9-12)

**Goals:**
- Deploy Cilium with Hubble
- Implement deny-by-default CiliumNetworkPolicies
- Validate token extraction in eBPF

**Deliverables:**
1. CiliumNetworkPolicy per MAS component
2. Custom eBPF program for JWT extraction (optional)
3. Hubble flow export to Telemetry Service
4. Grafana dashboard for network security
5. End-to-end test: eBPF blocks unauthorized egress

**Success Criteria:**
- Agent cannot reach external endpoints (except LLM)
- eBPF drops 100% of policy-violating traffic
- Hubble logs all flows with token metadata

---

### Phase 4: Control Plane Decomposition (Weeks 13-16)

**Goals:**
- Split monolithic ZTA into microservices
- Deploy Auth, Policy, AI Pipeline, Telemetry, Discovery services
- Migrate data to service-specific databases (optional)

**Deliverables:**
1. 5 separate container images (auth, policy, ai, telemetry, discovery)
2. Service mesh (optional: Istio/Linkerd) or direct HTTP
3. Redis for cross-service caching
4. Updated Helm chart with sub-charts
5. End-to-end test: Full token flow through decomposed services

**Success Criteria:**
- AI Pipeline can scale independently (10 replicas)
- Auth Service maintains 99.9% uptime during AI Pipeline issues
- Latency P95 < 500ms for token exchange

---

### Phase 5: CRDs and Operator (Weeks 17-20)

**Goals:**
- Define MultiAgentSystem, ZTAPolicy CRDs
- Build Kubernetes Operator to reconcile CRDs
- Automate CiliumNetworkPolicy generation

**Deliverables:**
1. CRD manifests (multiagentsystem, ztapolicy, mcpserver)
2. Operator codebase (Kubebuilder or Operator SDK)
3. Reconciliation loops for CRD → CiliumNetworkPolicy
4. GitOps integration (ArgoCD Application manifests)
5. End-to-end test: Create MAS via kubectl, policies auto-apply

**Success Criteria:**
- Operator reconciles CRDs within 5s
- CiliumNetworkPolicy auto-updated when MAS changes
- Zero manual policy editing required

---

### Phase 6: Production Hardening (Weeks 21-24)

**Goals:**
- Implement high availability and disaster recovery
- Security audit and penetration testing
- Performance optimization

**Deliverables:**
1. Multi-region PostgreSQL replication
2. Control plane auto-scaling (HPA)
3. Secrets encryption at rest (KMS)
4. Security audit report and remediation
5. Load testing: 10k tokens/sec, 1000 concurrent agents
6. Runbooks and incident response procedures

**Success Criteria:**
- Zero downtime during PostgreSQL failover
- System handles 10k tokens/sec at P95 < 1s
- Security audit: Zero critical vulnerabilities

---

### Phase 7: Advanced Features (Weeks 25-28)

**Goals:**
- eBPF-based token validation (fast path)
- Multi-tenancy (multiple MAS per cluster)
- Advanced AI pipeline (hybrid matcher, fine-tuning)

**Deliverables:**
1. eBPF program with JWT signature verification
2. Namespace isolation per MAS tenant
3. Hybrid task-tool matcher (embeddings + LLM)
4. Fine-tuned LLM model for tool intent
5. Cost optimization dashboard (LLM API spend)

**Success Criteria:**
- eBPF validates 90% of tokens (10% fallback to sidecar)
- 5 MAS tenants co-exist without interference
- AI matcher accuracy > 95% (F1 score)

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **MAS** | Multi-Agent System: A logical grouping of agents, MCP servers, and clients with shared policies |
| **MCP** | Model Context Protocol: HTTP-based protocol for agent-to-tool communication |
| **A2A** | Agent-to-Agent protocol: Communication protocol between AI agents |
| **eBPF** | Extended Berkeley Packet Filter: Kernel-level programmable packet processing |
| **Cilium** | Kubernetes CNI using eBPF for networking and security |
| **Hubble** | Cilium's observability layer for network flows |
| **Sidecar** | Container running alongside application container in same pod |
| **Token Exchange** | OAuth2 RFC 8693: Exchange one token for another (delegation/impersonation) |
| **Tool Check** | Security validation that requested tool matches user intent |
| **Task-Tool Matcher** | AI pipeline that matches user tasks to appropriate tools |
| **ZTA** | Zero Trust Architecture: Security model with deny-by-default and continuous verification |

---

## Appendix B: Component Port Assignments

| Component | Port | Protocol | Purpose |
|-----------|------|----------|---------|
| ZTA Auth Service | 8443 | HTTPS | Token operations |
| ZTA Policy Service | 8443 | HTTPS | App/MAS management |
| ZTA AI Pipeline Service | 8443 | HTTPS | Task-tool matching |
| ZTA Telemetry Service | 8443 | HTTPS | Event ingestion |
| ZTA Discovery Service | 8443 | HTTPS | MCP tool discovery |
| ZTA Sidecar (inbound) | 15001 | HTTP | Receive traffic from app |
| ZTA Sidecar (outbound) | 15002 | HTTP | Send traffic to external |
| ZTA Sidecar (metrics) | 15003 | HTTP | Prometheus metrics |
| Keycloak | 8080 | HTTP | OAuth2 endpoints |
| PostgreSQL | 5432 | TCP | Database |
| Redis | 6379 | TCP | Cache |
| Hubble Relay | 4245 | gRPC | Flow export |
| Hubble UI | 8081 | HTTP | Web interface |

---

## Appendix C: Example Full Deployment

**Complete MultiAgentSystem with 3 Apps:**

```bash
# 1. Install control plane
helm install zta-system ./charts/zta-mas-system \
  --namespace zta-control-plane \
  --create-namespace \
  --values values-prod.yaml

# 2. Wait for control plane ready
kubectl wait --for=condition=ready pod -l tier=control-plane -n zta-control-plane --timeout=300s

# 3. Create MAS namespace
kubectl create namespace production-mas

# 4. Deploy MultiAgentSystem CRD
kubectl apply -f - <<EOF
apiVersion: zta.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: production-mas
  namespace: production-mas
spec:
  name: "Production Multi-Agent System"
  authorizationServer: "production-realm"
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  - DETERMINISTIC_LLM_SELECTED_TOOLS
  - AI_POWERED_TOOL_MATCH
  apps:
  - name: user-app
    type: client
    baseUrl: "http://user-app:8000"
  - name: agent
    type: agent
    baseUrl: "http://agent:8000"
  - name: filesystem-mcp
    type: mcp_server
    baseUrl: "http://filesystem-mcp:8080"
EOF

# 5. Deploy agent with sidecar
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent
  namespace: production-mas
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
        zta.io/enabled: "true"
      annotations:
        zta.io/inject-sidecar: "true"
    spec:
      containers:
      - name: agent
        image: my-agent:v1.0.0
        ports:
        - containerPort: 8000
EOF

# 6. Verify sidecar injection
kubectl get pods -n production-mas
# Should show 2 containers per pod (agent + zta-sidecar)

# 7. Test token flow
kubectl exec -n production-mas deployment/agent -c agent -- curl http://localhost:15001/oauth/token

# 8. Check network policies
kubectl get ciliumnetworkpolicy -n production-mas

# 9. View Hubble flows
hubble observe --namespace production-mas --last 100
```

---

## Appendix D: Performance Benchmarks

**Token Operations (Target Latency):**
- Token generation (client credentials): P95 < 200ms
- Token exchange (no AI check): P95 < 500ms
- Token exchange (with AI check): P95 < 2000ms
- Token introspection (cached): P95 < 10ms
- Token introspection (uncached): P95 < 100ms

**Throughput (Per Replica):**
- Auth Service: 500 tokens/sec
- Policy Service: 2000 reads/sec
- AI Pipeline (embeddings): 100 matches/sec
- AI Pipeline (LLM verifier): 50 matches/sec
- Telemetry Service: 10k events/sec

**Sidecar Overhead:**
- Additional latency: +50ms P95
- CPU overhead: 100m per pod
- Memory overhead: 128Mi per pod
- Cache hit ratio: 85% (at 30s TTL)

**eBPF Performance:**
- Policy lookup: < 1μs
- Packet drop: < 10μs
- Token extraction: < 100μs
- JWT validation (eBPF): < 500μs

---

## Appendix E: Document Summary & Implementation Checklist

### Key Architectural Decisions

✅ **Component Decomposition** (§3)
- Monolith split into 6 microservices: Auth, Policy, AI Pipeline, Telemetry, Discovery, Sidecar
- Control plane (StatefulSet) + Data plane (Sidecar per pod)
- Justification: Scalability, isolation, independent failure domains

✅ **Sidecar Proxy Implementation** (§4.3)
- Technology: Envoy with Lua filters for protocol validation
- Responsibilities: L7 protocol enforcement (MCP/A2A), token injection, caching, telemetry
- Configuration: Envoy xDS API + ConfigMap
- Injection: Mutating webhook (automatic for pods with `zta.io/enabled=true`)

✅ **eBPF Enforcement** (§4.2, §5.5)
- Cilium for L3/L4 policy enforcement
- Custom eBPF programs for token extraction (experimental)
- Hubble for flow observability
- Deny-by-default with explicit allow-lists

✅ **Network Policies** (§5.2)
- Default deny in all MAS namespaces
- Identity-aware policies (Cilium security identities)
- FQDN-based LLM egress control
- HTTP path-based filtering for MCP/A2A

✅ **Custom Resources** (§7.2)
- `MultiAgentSystem` CRD: Declarative MAS definition
- `ZTAPolicy` CRD: Simplified policy abstraction
- Operator: Auto-generates CiliumNetworkPolicies, manages Keycloak realms

✅ **Protocol Enforcement** (§9.5)
- MCP: JSON-RPC 2.0 validation, method whitelist
- A2A: Structured message format, signature verification
- Sidecar enforcement: Fail-closed on violations
- Telemetry: All violations logged

✅ **Security Model** (§8)
- 7 threat scenarios addressed
- Token exfiltration prevention: eBPF egress blocking
- Lateral movement: Network policies + identity validation
- AI pipeline poisoning: Multiple check layers

✅ **Operational Runbooks** (§9.3)
- 6 detailed runbooks for common failure scenarios
- Auto-scaling strategies
- Capacity planning formulas
- Monitoring dashboards

### Implementation Roadmap Summary

| Phase | Duration | Key Deliverable | Risk |
|-------|----------|-----------------|------|
| 1: Control Plane | 4 weeks | Monolith deployed to K8s | Medium (Keycloak integration) |
| 2: Sidecar Injection | 4 weeks | Sidecar proxy + webhook | High (Envoy complexity) |
| 3: eBPF Integration | 4 weeks | Cilium policies + Hubble | Medium (eBPF expertise) |
| 4: Protocol Enforcement | 3 weeks | MCP/A2A validators | Medium (Edge cases) |
| 5: Operator | 4 weeks | CRDs + controller logic | High (Reconciliation complexity) |
| 6: AI Pipeline | 4 weeks | Embeddings + LLM verifier | Medium (OpenAI integration) |
| 7: Production Hardening | 5 weeks | mTLS, audit logging, HA | High (Security critical) |

**Total: 28 weeks (7 months)**

### Critical Success Factors

1. **eBPF Expertise**: Team must have Cilium experience or dedicate learning time
2. **Envoy Proficiency**: Sidecar implementation requires deep Envoy/xDS knowledge
3. **Keycloak Integration**: Token exchange flows depend on stable IdP
4. **AI Pipeline Latency**: Must optimize embeddings cache to meet <2s P95 target
5. **Operator Reliability**: CRD controller bugs can break entire system
6. **GitOps Readiness**: Helm charts must support ArgoCD/Flux from day 1

### Non-Negotiables Compliance

| Constraint | Compliance | Evidence |
|------------|------------|----------|
| Mandatory sidecars for all MAS components | ✅ | §3.3.6, §6.1 (mutating webhook) |
| Only MCP/A2A protocols internally | ✅ | §9.5 (protocol validators) |
| Single OpenAI-compatible LLM endpoint | ✅ | §5.2.4 (FQDN policy) |
| eBPF L3/L4 enforcement | ✅ | §4.2, §5.2 (Cilium) |
| Token capture at network layer | ✅ | §4.2.2, §5.5 (eBPF programs) |
| Deny-by-default networking | ✅ | §5.2.1 (default deny policy) |
| Clear responsibility split | ✅ | §4.1 (enforcement table) |
| Buildable design | ✅ | Concrete code examples, Helm charts, CRDs |

### Open Questions for Implementation Team

1. **Sidecar Technology Choice**: Envoy vs custom Golang proxy?
   - Recommendation: Envoy (maturity, ecosystem)
   - Trade-off: Complexity vs features

2. **eBPF Token Validation**: Implement in kernel or delegate to sidecar?
   - Recommendation: Hybrid (eBPF extracts, sidecar validates)
   - Rationale: eBPF limited in JWT parsing

3. **AI Pipeline Deployment**: Separate cluster or same cluster?
   - Recommendation: Same cluster, dedicated node pool (GPU optional)
   - Rationale: Reduce latency, simplify networking

4. **Keycloak HA**: Embedded PostgreSQL or external?
   - Recommendation: External PostgreSQL (shared with ZTA)
   - Rationale: Simpler backup, single DB to manage

5. **Certificate Management**: cert-manager or external CA?
   - Recommendation: cert-manager + Vault
   - Rationale: Kubernetes-native, auto-renewal

### Validation Checklist (Pre-Production)

- [ ] All control plane services have ≥3 replicas (HA)
- [ ] Default deny policy active in all MAS namespaces
- [ ] Sidecar injection validated with 10+ test pods
- [ ] MCP protocol violations logged and blocked (test suite passing)
- [ ] A2A signature verification working (test suite passing)
- [ ] eBPF policies prevent lateral movement (pentested)
- [ ] Token exfiltration blocked (tested with malicious pod)
- [ ] LLM egress restricted to single FQDN (tested)
- [ ] Hubble flows exported to telemetry (verified)
- [ ] Keycloak realm auto-creation by operator (tested)
- [ ] CRD controller handles concurrent updates (stress tested)
- [ ] AI pipeline latency <2s P95 under load (benchmarked)
- [ ] Telemetry batch writes work under 50k events/sec (load tested)
- [ ] Audit logs immutable (PostgreSQL append-only table)
- [ ] Secrets encrypted at rest (KMS configured)
- [ ] GitOps deployment works (ArgoCD sync successful)
- [ ] Runbooks tested in staging (at least 3 failure scenarios)
- [ ] Capacity planning validated (1000 pod test)

## Appendix F: Quick Start Guide

### 30-Minute Demo Deployment

This quick start deploys a minimal ZTA-MAS system for evaluation purposes.

**Prerequisites:**
```bash
# Kubernetes cluster (kind, minikube, or cloud)
kubectl version --client

# Helm 3+
helm version

# Docker for building images
docker --version
```

**Step 1: Create Kind Cluster with Cilium**
```bash
# Create kind cluster
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  disableDefaultCNI: true
  podSubnet: 10.244.0.0/16
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

# Install Cilium
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --version 1.14.5 \
  --namespace kube-system \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true

# Wait for Cilium
kubectl wait --for=condition=ready pod -l k8s-app=cilium -n kube-system --timeout=300s
```

**Step 2: Deploy Dependencies**
```bash
# PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --namespace zta-control-plane \
  --create-namespace \
  --set auth.postgresPassword=demo123

# Keycloak
helm install keycloak bitnami/keycloak \
  --namespace zta-control-plane \
  --set auth.adminPassword=admin \
  --set postgresql.enabled=false \
  --set externalDatabase.host=postgresql \
  --set externalDatabase.password=demo123
```

**Step 3: Deploy ZTA Control Plane**
```bash
# Clone repo (hypothetical)
git clone https://github.com/your-org/zta-mas-system
cd zta-mas-system

# Deploy with Helm
helm install zta-mas-system ./charts/zta-mas-system \
  --namespace zta-control-plane \
  --set global.environment=demo \
  --set controlPlane.replicas=1 \
  --set sidecar.injection.enabled=true

# Wait for deployment
kubectl wait --for=condition=available deployment --all -n zta-control-plane --timeout=300s
```

**Step 4: Create Sample MAS**
```yaml
kubectl apply -f - <<EOF
apiVersion: zta.io/v1alpha1
kind: MultiAgentSystem
metadata:
  name: demo-mas
  namespace: demo-mas
spec:
  name: "Demo Multi-Agent System"
  authorizationServer: "demo-realm"
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  apps:
  - name: demo-agent
    type: agent
    baseUrl: "http://demo-agent.demo-mas.svc.cluster.local:8000"
  - name: demo-mcp
    type: mcp_server
    baseUrl: "http://demo-mcp.demo-mas.svc.cluster.local:8080"
EOF
```

**Step 5: Deploy Sample Workloads**
```bash
# Deploy agent with sidecar
kubectl apply -f examples/demo-agent.yaml -n demo-mas

# Deploy MCP server with sidecar
kubectl apply -f examples/demo-mcp.yaml -n demo-mas

# Verify sidecars injected
kubectl get pods -n demo-mas
# Should show 2 containers per pod (app + zta-sidecar)
```

**Step 6: Test Token Flow**
```bash
# Port-forward to auth service
kubectl port-forward -n zta-control-plane svc/zta-auth-service 8443:8443 &

# Generate token
curl -k -X POST https://localhost:8443/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "demo-agent",
    "client_secret": "demo-secret",
    "user_input": "Read file /etc/hosts",
    "grant_type": "client_credentials"
  }'

# Exchange token
curl -k -X POST https://localhost:8443/oauth/token/exchange \
  -H "Content-Type: application/json" \
  -d '{
    "subject_token": "<token_from_previous_step>",
    "requested_tool": "filesystem_read"
  }'
```

**Step 7: View Observability**
```bash
# Port-forward Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Open browser: http://localhost:3000
# Default credentials: admin/admin

# Port-forward Hubble UI
kubectl port-forward -n kube-system svc/hubble-ui 8081:80

# Open browser: http://localhost:8081
```

**Cleanup:**
```bash
kind delete cluster
```

---

## Appendix G: Architectural Decision Records (ADRs)

### ADR-001: Envoy as Sidecar Proxy

**Status:** Accepted  
**Date:** 2025-01-10  
**Deciders:** Architecture Team

**Context:**
Need a sidecar proxy for L7 protocol enforcement (MCP/A2A), token injection, and telemetry.

**Options Considered:**
1. Envoy
2. Custom Golang proxy
3. Nginx + Lua
4. Linkerd2-proxy

**Decision:**
Use Envoy with Lua filters for protocol validation.

**Rationale:**
- **Envoy**: Mature, battle-tested, excellent observability, xDS for dynamic config
- **Custom Golang**: Full control but high development/maintenance cost
- **Nginx**: Good for simple reverse proxy but limited L7 inspection
- **Linkerd2-proxy**: Purpose-built for service mesh, less flexible for custom protocols

**Consequences:**
- ✅ Rich feature set (circuit breakers, retries, metrics)
- ✅ Dynamic configuration via xDS
- ✅ Large ecosystem and community
- ❌ Complexity: Steep learning curve
- ❌ Resource overhead: 100-200m CPU, 128-256Mi RAM per sidecar

---

### ADR-002: Cilium for Network Policy Enforcement

**Status:** Accepted  
**Date:** 2025-01-10  
**Deciders:** Architecture Team

**Context:**
Need eBPF-based L3/L4 network policy enforcement with observability.

**Options Considered:**
1. Cilium
2. Calico (eBPF mode)
3. Calico (iptables mode)
4. kube-proxy + NetworkPolicy

**Decision:**
Use Cilium with Hubble for policy enforcement and observability.

**Rationale:**
- **Cilium**: Native eBPF, identity-aware, L7 visibility, FQDN policies
- **Calico eBPF**: Good but less mature eBPF implementation
- **Calico iptables**: Legacy, no eBPF benefits
- **kube-proxy**: No L7 awareness, limited observability

**Consequences:**
- ✅ eBPF performance: Lower latency, higher throughput vs iptables
- ✅ Hubble: Real-time flow observability
- ✅ Identity-aware: Policies based on labels, not IPs
- ❌ Complexity: eBPF debugging harder than iptables
- ❌ Kernel requirement: Linux 4.19+ with eBPF support

---

### ADR-003: Keycloak as Identity Provider

**Status:** Accepted  
**Date:** 2025-01-10  
**Deciders:** Architecture Team

**Context:**
Need OAuth2/OIDC provider for token issuance and validation.

**Options Considered:**
1. Keycloak
2. Auth0 (managed)
3. Okta (managed)
4. Custom OAuth2 server

**Decision:**
Use Keycloak as self-hosted IdP.

**Rationale:**
- **Keycloak**: Open-source, feature-rich, supports token exchange (RFC 8693)
- **Auth0/Okta**: Managed but vendor lock-in, higher cost
- **Custom**: Full control but development overhead

**Consequences:**
- ✅ No vendor lock-in
- ✅ Token exchange support (RFC 8693)
- ✅ Realm-per-MAS isolation
- ❌ Operational overhead: HA, backups, upgrades
- ❌ Performance: Added latency vs cloud IdP

---

### ADR-004: Hybrid AI Check Strategy

**Status:** Accepted  
**Date:** 2025-01-12  
**Deciders:** Security + Architecture Team

**Context:**
Need to validate that requested tools match user's task intent.

**Options Considered:**
1. Deterministic only (exact match)
2. Embeddings only (cosine similarity)
3. LLM verifier only (GPT-4)
4. Hybrid (deterministic + AI)

**Decision:**
Use hybrid strategy: Deterministic checks + LLM verifier for high-risk tools.

**Rationale:**
- **Deterministic**: Fast but brittle, can't handle synonyms/paraphrasing
- **Embeddings**: Fast, handles similarity but can have false positives
- **LLM**: Accurate but slow and expensive
- **Hybrid**: Best of all worlds

**Consequences:**
- ✅ High accuracy (LLM verifier)
- ✅ Low latency for most requests (deterministic + embeddings)
- ✅ Cost-effective (LLM only for subset)
- ❌ Complexity: Multiple check implementations
- ❌ Latency variance: 100ms (embeddings) vs 2s (LLM)

---

### ADR-005: PostgreSQL Shared Database

**Status:** Accepted (with future review)  
**Date:** 2025-01-10  
**Deciders:** Architecture Team

**Context:**
Microservices need data persistence. Should they share a database or have separate DBs?

**Options Considered:**
1. Shared PostgreSQL database
2. Database-per-service
3. Event sourcing + CQRS

**Decision:**
Start with shared PostgreSQL, optionally split later.

**Rationale:**
- **Shared DB**: Simpler, ACID transactions across services, easier migration from monolith
- **DB-per-service**: Better isolation but complex distributed transactions
- **Event sourcing**: Eventual consistency, high complexity

**Consequences:**
- ✅ Simpler initial implementation
- ✅ ACID transactions across tables
- ✅ Lower operational overhead (one DB to manage)
- ❌ Tight coupling: Schema changes affect multiple services
- ❌ Scaling: Cannot scale services independently
- **Future**: May split to per-service DBs in Phase 10+

---

### ADR-006: GitOps with ArgoCD

**Status:** Accepted  
**Date:** 2025-01-13  
**Deciders:** Platform Team

**Context:**
Need deployment automation and configuration management.

**Options Considered:**
1. ArgoCD
2. FluxCD
3. Spinnaker
4. Jenkins X

**Decision:**
Use ArgoCD for GitOps-based deployments.

**Rationale:**
- **ArgoCD**: UI-first, easy to adopt, ApplicationSets for multi-env
- **FluxCD**: Git-first, no UI, more automation-friendly
- **Spinnaker**: Enterprise-grade but complex
- **Jenkins X**: Opinionated, tightly coupled to Jenkins

**Consequences:**
- ✅ GitOps: Declarative, auditable, rollback-friendly
- ✅ UI: Easy to visualize deployments
- ✅ ApplicationSets: Multi-cluster management
- ❌ Another component to manage
- ❌ Learning curve for team

---

## Appendix H: FAQ

### General Questions

**Q1: Why decompose the monolith into microservices?**

**A:** Scalability and fault isolation. The AI Pipeline (LLM calls) has different scaling characteristics than the Auth Service. In the monolith, a slow LLM call could exhaust all available resources and block token generation. Microservices allow independent scaling and failure domains.

**Q2: Why is a sidecar required for every pod?**

**A:** Zero Trust principle: Never trust the application to enforce security policies. The sidecar acts as a policy enforcement point (PEP) that validates every request/response, injects tokens, and logs telemetry. If the application is compromised, the sidecar still enforces policies.

**Q3: Can we use Istio instead of a custom sidecar?**

**A:** Partial solution. Istio provides mTLS, observability, and traffic management but doesn't understand MCP/A2A protocols or token exchange flows. You'd still need custom logic. Our sidecar (Envoy + Lua filters) is effectively a lightweight, purpose-built Istio alternative.

**Q4: How much overhead does the sidecar add?**

**A:**
- **Latency**: +50ms P95 (token introspection cache helps)
- **CPU**: 100m baseline + 10m per 100 req/sec
- **Memory**: 128Mi baseline + 1Mi per 1000 cached tokens

For most workloads, this is acceptable. High-throughput services may notice the impact.

**Q5: What happens if the control plane is down?**

**A:** Sidecars have a 30-second token cache. During this window, cached introspection results are used. After cache expiry, sidecars fail-closed (deny all requests) until the control plane recovers. This is intentional: availability is secondary to security in a Zero Trust model.

### Technical Questions

**Q6: Why not validate tokens in eBPF instead of the sidecar?**

**A:** eBPF has limited CPU budget and cannot parse complex JSON (JWT payload). eBPF can extract the token from HTTP headers and check signature validity, but full validation (claims, expiry, scopes) must happen in userspace (sidecar or control plane).

**Q7: How do you handle token rotation?**

**A:** Tokens are short-lived (5min TTL). No explicit rotation needed. For long-running operations (e.g., streaming), the agent must refresh tokens by calling `/oauth/token` again.

**Q8: Can agents call multiple MCP servers simultaneously?**

**A:** Yes, but each call requires a separate token exchange. Agent flow:
1. Get initial token (user input)
2. Exchange token for MCP-1 → Get token-1
3. Exchange token for MCP-2 → Get token-2
4. Call MCP-1 with token-1
5. Call MCP-2 with token-2

Each token is scoped to specific tools on a specific MCP server.

**Q9: How do you prevent token replay attacks?**

**A:**
- **Short TTL**: 5-minute expiry limits replay window
- **Nonce**: Token exchange tokens include a nonce (single-use)
- **Source validation**: Cilium identity validation ensures tokens originate from expected pods
- **Telemetry**: Correlates token usage with source pod; alerts on anomalies

**Q10: What's the performance impact of AI checks?**

**A:**
- **Embeddings**: +100-200ms
- **LLM verifier**: +1-2 seconds
- **Mitigation**: Use hybrid strategy (deterministic for low-risk, LLM for high-risk)
- **Caching**: Cache AI check results for (task, tool) pairs (1-hour TTL)

### Operational Questions

**Q11: How do you upgrade the system without downtime?**

**A:**
1. **Control plane**: Rolling update with 3+ replicas (Kubernetes default)
2. **Sidecars**: Update mutating webhook to inject new version; rolling restart workloads
3. **CRDs**: Use `kubectl apply --server-side` for non-breaking schema changes
4. **Database**: Use Liquibase/Flyway for schema migrations

Blue-green deployment is recommended for major version upgrades.

**Q12: How do you troubleshoot a token exchange failure?**

**A:**
1. Check sidecar logs: `kubectl logs <pod> -c zta-sidecar`
2. Check control plane logs: `kubectl logs -n zta-control-plane deployment/zta-auth-service`
3. Check Hubble flows: `hubble observe --pod <pod-name>`
4. Check telemetry: Query PostgreSQL `traces` table for user_input_id
5. Check AI pipeline: Verify LLM API is reachable

Runbook in §9.3 provides detailed steps.

**Q13: What's the disaster recovery plan?**

**A:**
- **PostgreSQL**: Automated backups to S3 (daily), 7-day retention
- **Keycloak**: Realm export (weekly), stored in S3
- **Vault**: Raft snapshots to S3 (every 6 hours)
- **GitOps**: Cluster rebuild from Git (infrastructure as code)

RTO: 4 hours, RPO: 24 hours (for database).

**Q14: How do you scale to 10,000 pods?**

**A:**
Use capacity planning formulas (§10.2.4):
- **Auth Service**: 40 replicas (500 TPS each → 20,000 TPS total)
- **AI Pipeline**: 200 replicas (50 checks/sec each → 10,000 checks/sec total)
- **PostgreSQL**: Vertical scaling (r5.8xlarge) + read replicas
- **Cluster**: 400 nodes (m5.2xlarge, 25 pods/node)

Estimated cost: ~$120k/month (AWS).

### Security Questions

**Q15: How do you prevent a compromised agent from stealing tokens?**

**A:**
Multiple layers:
1. **eBPF egress blocking**: Agent cannot send tokens to external endpoints
2. **Sidecar stripping**: Sidecar removes Authorization headers from non-control-plane requests
3. **Short TTL**: 5-minute expiry limits damage
4. **Telemetry alerts**: Anomaly detection on token reuse patterns

**Q16: What if an agent bypasses the sidecar (e.g., raw TCP)?**

**A:**
- **iptables redirect**: Init container configures iptables to force all traffic through sidecar
- **Cilium policy**: L4 policies block direct pod-to-pod communication (must go through sidecar ports)
- **Falco**: Runtime security detects suspicious network activity (e.g., raw sockets)

**Q17: How do you audit who accessed which tools?**

**A:**
Full audit trail in Telemetry Service (PostgreSQL `traces` table):
- User input (task)
- LLM calls (tool selections)
- Token issuance (app_id, timestamp)
- Token exchange (requested_tool, blocking_reason)
- MCP tool invocations (tool_name, args, result)

Grafana dashboard visualizes audit trail (§8.3).

---

## Appendix I: References & Further Reading

### Standards & RFCs

1. **OAuth 2.0 Token Exchange** (RFC 8693)  
   https://datatracker.ietf.org/doc/html/rfc8693  
   _Token exchange protocol used for delegation_

2. **JSON Web Token (JWT)** (RFC 7519)  
   https://datatracker.ietf.org/doc/html/rfc7519  
   _Token format for access tokens_

3. **OAuth 2.0** (RFC 6749)  
   https://datatracker.ietf.org/doc/html/rfc6749  
   _Authorization framework_

4. **Model Context Protocol (MCP)**  
   https://spec.modelcontextprotocol.io/  
   _Protocol for agent-to-tool communication_

### Kubernetes & Cloud Native

5. **Pod Security Standards**  
   https://kubernetes.io/docs/concepts/security/pod-security-standards/  
   _Security profiles for Kubernetes pods_

6. **Cilium Documentation**  
   https://docs.cilium.io/  
   _eBPF-based networking and security_

7. **Envoy Proxy Documentation**  
   https://www.envoyproxy.io/docs/  
   _High-performance proxy for sidecars_

8. **Kubernetes Operators**  
   https://kubernetes.io/docs/concepts/extend-kubernetes/operator/  
   _CRD and controller patterns_

### Security

9. **NIST Zero Trust Architecture** (SP 800-207)  
   https://csrc.nist.gov/publications/detail/sp/800-207/final  
   _Zero Trust principles and implementation_

10. **CIS Kubernetes Benchmark**  
    https://www.cisecurity.org/benchmark/kubernetes  
    _Security hardening guide_

11. **SPIFFE/SPIRE**  
    https://spiffe.io/  
    _Workload identity for microservices_

12. **Falco Rules**  
    https://falco.org/docs/rules/  
    _Runtime security rules_

### GitOps

13. **Argo CD Documentation**  
    https://argo-cd.readthedocs.io/  
    _GitOps continuous delivery_

14. **Flux CD Documentation**  
    https://fluxcd.io/docs/  
    _GitOps toolkit for Kubernetes_

### Observability

15. **Prometheus Best Practices**  
    https://prometheus.io/docs/practices/  
    _Metrics collection and alerting_

16. **Grafana Loki**  
    https://grafana.com/docs/loki/  
    _Log aggregation_

17. **OpenTelemetry**  
    https://opentelemetry.io/  
    _Distributed tracing_

### Books

18. **"Kubernetes Patterns"** by Ibryam & Huss  
    _Design patterns for cloud-native apps_

19. **"Zero Trust Networks"** by Gilman & Barth  
    _O'Reilly book on Zero Trust architecture_

20. **"Istio: Up and Running"** by Lee et al.  
    _Service mesh patterns (applicable to sidecars)_

---

## Appendix J: Document Revision History

| Version | Date | Changes | Authors |
|---------|------|---------|---------|
| v0.1 | 2025-01-10 | Initial draft: Requirements, architecture overview | Architecture Team |
| v0.2 | 2025-01-11 | Added component decomposition, sidecar design | Architecture Team |
| v0.3 | 2025-01-12 | Added network policies, eBPF programs | Network Team |
| v0.4 | 2025-01-12 | Added GitOps, mTLS, secrets management | Platform Team |
| v0.5 | 2025-01-13 | Added observability stack (Prometheus, Grafana, Loki) | SRE Team |
| v0.6 | 2025-01-14 | Added migration strategy, load testing | DevOps Team |
| v0.7 | 2025-01-14 | Added performance testing, capacity planning, HPA/VPA | Performance Team |
| v0.8 | 2025-01-15 | Added security hardening (Gatekeeper, Falco, Trivy) | Security Team |
| **v1.0** | **2025-01-15** | **Final review, appendices, quick start guide** | **All Teams** |

### Key Milestones

- **2025-01-10**: Kickoff meeting, requirements gathering
- **2025-01-11**: Architecture review, component design approved
- **2025-01-12**: Network and security design finalized
- **2025-01-13**: Operational model and observability defined
- **2025-01-14**: Performance and migration strategies approved
- **2025-01-15**: Document finalized, ready for implementation

### Contributors

- **Lead Architect**: Designed overall system architecture
- **Network Engineer**: Designed Cilium policies, eBPF programs
- **Security Engineer**: Designed threat model, security hardening
- **Platform Engineer**: Designed GitOps, CI/CD, secrets management
- **SRE**: Designed observability stack, runbooks, capacity planning
- **Performance Engineer**: Designed load testing, HPA/VPA configurations
- **DevOps Engineer**: Designed migration strategy, Helm charts

### Future Enhancements (Post-v1.0)

Planned for future versions:

- **v1.1**: Add service mesh (Istio/Linkerd) integration guide
- **v1.2**: Add multi-cluster federation (Cluster API)
- **v1.3**: Add cost optimization recommendations (Spot instances, autoscaling)
- **v1.4**: Add compliance automation (policy-as-code for SOC2/PCI-DSS)
- **v1.5**: Add advanced AI pipeline (model fine-tuning, A/B testing)

---



---

**END OF SPECIFICATIONS**

**Document Version:** v1.0  
**Last Updated:** 2025-01-15  
**Authors:** Senior Cloud & Kubernetes Architect Team  
**Status:** Implementation-Ready  
**Next Review:** After Phase 1 completion
