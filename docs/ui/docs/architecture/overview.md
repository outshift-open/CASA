---
id: architecture-overview
sidebar_position: 1
title: Architecture Overview
---

# Architecture Overview

ZTA has two main layers: a **control plane** that manages identity and policy, and a **data plane** that enforces those policies at runtime.

## Global Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "zta-control-plane namespace"
            AUTH["Auth Service\n(Token Issuance & Exchange)"]
            KC["Keycloak IdP"]
            PG[("PostgreSQL")]
            UI["ZTA Explorer UI"]
            AUTH --> KC
            AUTH --> PG
            UI --> AUTH
        end

        subgraph "mas-namespace (your application)"
            subgraph "Client Pod"
                CL["Client App"]
                CLS["ZTA Sidecar"]
                CL -.->|"traffic intercepted"| CLS
            end
            subgraph "Agent Pod"
                AG["Agent"]
                AGS["ZTA Sidecar"]
                AG -.->|"traffic intercepted"| AGS
            end
            subgraph "MCP Server Pod"
                MCP["MCP Server"]
                MCPS["ZTA Sidecar"]
                MCP -.->|"traffic intercepted"| MCPS
            end
            CLS -->|"MCP / A2A"| AGS
            AGS -->|"MCP"| MCPS
        end

        EBPF["Cilium eBPF\n(L3/L4 network enforcement\nJWT extraction & observability)"]
        EBPF -.->|"enforces"| CLS
        EBPF -.->|"enforces"| AGS
        EBPF -.->|"enforces"| MCPS
    end

    CLS & AGS & MCPS -->|"Token ops (token request, exchange, introspection)"| AUTH
    AGS -->|"LLM calls (token-gated)"| LLM["External LLM\n(OpenAI-compatible)"]

    style AUTH fill:#4ecdc4,color:#000
    style EBPF fill:#ff6b6b,color:#fff
    style LLM fill:#ffe66d,color:#000
```

## Component Summary

### Control Plane

The control plane runs in the `zta-control-plane` namespace and handles:

- **Token issuance** — OAuth2 client credentials flow (initial token for user input)
- **Token exchange** — RFC 8693 token exchange for delegated, scope-limited tokens
- **Token introspection** — validates tokens presented by sidecars
- **Tool check orchestration** — runs deterministic and/or AI-powered checks on token exchange requests
- **MAS lifecycle management** — reads `MultiAgentSystem` and `ZTAPolicy` CRDs, reconciles application state

See [Control Plane](control-plane.md) for full details.

### ZTA Sidecar

Every pod in a ZTA-managed namespace gets an Envoy-based sidecar injected automatically. The sidecar:

- Intercepts all inbound and outbound HTTP traffic via iptables rules
- On **egress**: requests or exchanges tokens, injects `Authorization` header
- On **ingress**: introspects presented tokens, allows or denies the request
- Caches introspection results (30s TTL) to reduce control plane load
- Enforces protocol restrictions (MCP, A2A only — no arbitrary HTTP)

See [ZTA Sidecar](sidecar.md) for full details.

### eBPF Enforcement Layer

Cilium provides L3/L4 network enforcement using identity-based (not IP-based) policies. At this layer:

- **Deny-by-default** — all traffic is dropped unless explicitly allowed by a `CiliumNetworkPolicy`
- **LLM endpoint restriction** — agents can only reach a single approved external FQDN
- **JWT extraction** — custom eBPF programs extract and hash JWTs from HTTP headers for observability
- **Flow logging** — Hubble provides real-time flow logs correlated with token metadata

See [eBPF Enforcement](ebpf.md) for full details.

## Deployment Modes

ZTA supports two dataplane options:

| Mode | Sidecar Injection | L7 Enforcement | L3/L4 Enforcement | Status |
|---|---|---|---|---|
| **Istio** | Istio automatic injection | `ext_authz_middleware` (Go) | Istio NetworkPolicy | Current deployments |
| **Cilium** | Custom mutating webhook | ZTA sidecar (Envoy + Lua) | CiliumNetworkPolicy | Recommended for production |

See [Deployment Modes](/deployment-modes/istio) for setup guides.

## Trust Model

ZTA operates on a layered trust model:

1. **eBPF / L3-L4** — deny by default; only known endpoints may communicate
2. **Sidecar / L7** — every request must carry a valid, non-expired token with correct scope
3. **Control plane** — token exchange validates that the requested tool matches the original user intent

No layer alone is sufficient. Compromise requires breaking all three.
