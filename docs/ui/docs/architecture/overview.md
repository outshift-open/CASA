---
id: architecture-overview
sidebar_position: 1
title: Architecture Overview
---

# Architecture Overview

CASA has two main layers: a **control plane** that manages identity and policy, and a **data plane** that enforces those policies at runtime.

## Global Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#f0fdf4', 'edgeLabelBackground': '#f0fdf4'}}}%%
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "casa-control-plane"
            AUTH["Auth Service\n(Token Issuance & Exchange)"]
            KC["Keycloak IdP"]
            PG[("PostgreSQL")]
            UI["CASA Explorer UI"]
            AUTH --> KC
            AUTH --> PG
            UI --> AUTH
        end

        subgraph "mas-namespace"
            subgraph "Client Pod"
                CL["Client App"]
                CLS["CASA Sidecar"]
                CL -.->|intercepted| CLS
            end
            subgraph "Agent Pod"
                AG["Agent"]
                AGS["CASA Sidecar"]
                AG -.->|intercepted| AGS
            end
            subgraph "MCP Server Pod"
                MCP["MCP Server"]
                MCPS["CASA Sidecar"]
                MCP -.->|intercepted| MCPS
            end
            CLS -->|"MCP/A2A"| AGS
            AGS -->|"MCP"| MCPS
        end

        EBPF["eBPF\n(L4/L7 enforcement\nJWT extraction)"]
        EBPF -.->|enforces| CLS
        EBPF -.->|enforces| AGS
        EBPF -.->|enforces| MCPS
    end

    CLS & AGS & MCPS -->|"Token ops"| AUTH
    AGS -->|"LLM calls"| LLM["External LLM\n(OpenAI-compatible)"]

    style AUTH fill:#134e4a,stroke:#4ecdc4,color:#f1f5f9
    style KC   fill:#451a03,stroke:#fbbf24,color:#f1f5f9
    style PG   fill:#1e3a5f,stroke:#60a5fa,color:#f1f5f9
    style UI   fill:#064e3b,stroke:#34d399,color:#f1f5f9
    style CL   fill:#1e293b,stroke:#475569,color:#cbd5e1
    style CLS  fill:#1a2e05,stroke:#84cc16,color:#f1f5f9
    style AG   fill:#1e293b,stroke:#475569,color:#cbd5e1
    style AGS  fill:#1a2e05,stroke:#84cc16,color:#f1f5f9
    style MCP  fill:#1e293b,stroke:#475569,color:#cbd5e1
    style MCPS fill:#1a2e05,stroke:#84cc16,color:#f1f5f9
    style EBPF fill:#450a0a,stroke:#ff6b6b,color:#f1f5f9
    style LLM  fill:#422006,stroke:#ffe66d,color:#f1f5f9
```

### Components

![CASA Components](/img/components.png)

## Component Summary

### Control Plane

The control plane runs in the `casa-control-plane` namespace and handles:

- **Token issuance** — OAuth2 client credentials flow (initial token for user input)
- **Token exchange** — RFC 8693 token exchange for delegated, scope-limited tokens
- **Token introspection** — validates tokens presented by sidecars
- **Tool check orchestration** — runs deterministic and/or AI-powered checks on token exchange requests
- **MAS lifecycle management** — reads `MultiAgentSystem` and `CASAPolicy` CRDs, reconciles application state

See [Control Plane](control-plane.md) for full details.

### CASA Sidecar

Every pod in a CASA-managed namespace gets an Envoy-based sidecar injected automatically. The sidecar:

- Intercepts all inbound and outbound HTTP traffic via iptables rules
- On **egress**: requests or exchanges tokens, injects `Authorization` header
- On **ingress**: introspects presented tokens, allows or denies the request
- Caches introspection results (30s TTL) to reduce control plane load
- Enforces protocol restrictions (MCP, A2A only — no arbitrary HTTP)

See [CASA Sidecar](sidecar.md) for full details.

### eBPF Enforcement Layer

The eBPF enforcement layer operates at the kernel level on eBPF-enabled Kubernetes nodes (kernel 5.8+), independently of the CNI. It provides:

- **Deny-by-default** — traffic enforcement via eBPF programs or network policy
- **LLM endpoint restriction** — agents can only reach a single approved external FQDN
- **JWT extraction** — eBPF programs extract and hash JWTs from HTTP headers for observability
- **Flow logging** — real-time flow logs correlated with token metadata

In Istio mode, eBPF enforcement uses the node kernel and is available when nodes have eBPF enabled. The [Cilium deployment mode](/deployment-modes/cilium) (roadmap) provides a fully integrated eBPF + sidecar solution via the Cilium daemonset.

See [eBPF Enforcement](ebpf.md) for full details.

## Deployment Modes

CASA supports two dataplane options:

| Mode | Sidecar Injection | L7 Enforcement | L4/L7 + eBPF | Status |
|---|---|---|---|---|
| **Istio** | Istio automatic injection | `ext_authz_middleware` (Go) | eBPF (node kernel) | Current |
| **Cilium** | Node-level daemonset | CASA sidecar (Envoy + Lua) | CASAPolicy + eBPF (integrated) | Coming soon (Roadmap) |

See [Deployment Modes](/deployment-modes/istio) for setup guides.

## Trust Model

CASA operates on a layered trust model:

1. **eBPF / L4-L7** — deny by default; only known endpoints may communicate
2. **Sidecar / L7** — every request must carry a valid, non-expired token with correct scope
3. **Control plane** — token exchange validates that the requested tool matches the original user intent

No layer alone is sufficient. Compromise requires breaking all three.
