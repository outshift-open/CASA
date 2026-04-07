---
id: ebpf
sidebar_position: 4
title: eBPF Enforcement
---

# eBPF Enforcement

ZTA uses eBPF (via Cilium) for L3/L4 network enforcement and JWT observability. This is the lowest-level enforcement layer and operates at the kernel level, before any userspace process is involved.

## What eBPF Handles

| Capability | eBPF | Sidecar | Control Plane |
|---|---|---|---|
| Deny-by-default networking | ✅ | — | — |
| Identity-based allow-lists | ✅ | — | — |
| LLM endpoint restriction (FQDN) | ✅ | — | — |
| JWT extraction from HTTP headers | ✅ | ✅ | — |
| JWT signature fast-path check | ⚠️ (experimental) | ✅ | ✅ |
| Token introspection (full) | — | ✅ | ✅ |
| Token exchange | — | ✅ | ✅ |
| Protocol enforcement (MCP/A2A) | — | ✅ | — |
| L7 request/response logging | — | ✅ | — |
| Flow logging | ✅ (Hubble) | — | — |

⚠️ = partial or experimental

## Network Policies

Cilium enforces network policies based on **pod identity**, not IP addresses. This means policies survive pod restarts and reschedules without requiring IP-based rules.

### Deny-by-default

All traffic in MAS namespaces is denied by default. Allowed flows must be explicitly declared:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny-all
  namespace: production-mas
spec:
  endpointSelector: {}
  ingress: []
  egress: []
```

### Allow specific flows

```yaml
# Allow agent → MCP server (MCP protocol paths only)
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
          path: "/mcp/*"
        - method: "GET"
          path: "/mcp/*"
```

### LLM endpoint restriction

Agents are restricted to a single approved external LLM endpoint using Cilium's FQDN-based policies:

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
    - matchPattern: "api.openai.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
```

Cilium's DNS proxy intercepts DNS queries and only resolves FQDNs in the allow-list. All other external destinations are dropped.

## ZTAPolicy CRD

The `ZTAPolicy` CRD provides a Kubernetes-native way to declare per-workload network policies. The ZTA operator reconciles these into `CiliumNetworkPolicy` resources automatically:

```yaml
apiVersion: zta.io/v1alpha1
kind: ZTAPolicy
metadata:
  name: agent-policy
  namespace: production-mas
spec:
  targetRef:
    kind: Deployment
    name: orchestrator-agent
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

## JWT Observability

Custom eBPF programs can extract JWT tokens from HTTP Authorization headers at the kernel level. This provides:

- **Token flow logging** — which pods are sending/receiving tokens, without logging the token itself (SHA256 hash only)
- **Exfiltration detection** — alert when a token appears on an unexpected destination
- **Count statistics** — token issuance rates per pod, per namespace

Full JWT validation (claims, expiry, scopes) is **not** done in eBPF — the complexity limits and instruction count limits make full validation infeasible. eBPF handles fast-path presence checking only; the sidecar does full validation.

## Observability Stack

Cilium's Hubble component provides:
- Real-time flow logs (source/destination pod, protocol, verdict)
- L7 HTTP visibility (method, path, status code)
- Network policy verdict tracking (allowed/denied per policy)
- Service dependency graph

Hubble flows can be exported to the ZTA Telemetry Service for correlation with token events.
