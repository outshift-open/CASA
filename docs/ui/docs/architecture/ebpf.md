---
id: ebpf
sidebar_position: 4
title: eBPF Enforcement
---

# eBPF Enforcement

CASA uses eBPF for L4/L7 network enforcement and JWT observability. eBPF programs run at the kernel level on any Kubernetes node with eBPF enabled (kernel 5.8+), independently of the CNI.

In the current **Istio deployment**, eBPF enforcement uses the node kernel directly. The planned **[Cilium deployment mode](/deployment-modes/cilium)** (roadmap) provides a more integrated experience: Cilium's daemonset manages both the CNI and the eBPF programs. Observability and tracing are provided by the **CASA Explorer UI** in both modes.

## What eBPF Handles

| Capability                       | eBPF                  | Sidecar | Runtime |
| -------------------------------- | --------------------- | ------- | ------------- |
| Deny-by-default networking       | ✅                    | —       | —             |
| Identity-based allow-lists       | ✅                    | —       | —             |
| LLM endpoint restriction (FQDN)  | ✅                    | —       | —             |
| JWT extraction from HTTP headers | ✅                    | ✅      | —             |
| JWT signature fast-path check    | ⚠️ (experimental)     | ✅      | ✅            |
| Token introspection (full)       | —                     | ✅      | ✅            |
| Token exchange                   | —                     | ✅      | ✅            |
| Protocol enforcement (MCP/A2A)   | —                     | ✅      | —             |
| L7 request/response logging      | —                     | ✅      | —             |
| Flow logging                     | ✅ (CASA Explorer UI) | —       | —             |

⚠️ = partial or experimental

## Network Policies

CASA enforces network policies based on **workload identity**, not IP addresses. Policies survive pod restarts and reschedules without requiring IP-based rules.

Network policies are declared using the `CASAPolicy` CRD. See [CASAPolicy CRD](#casapolicy-crd) below.

### Deny-by-default

All traffic in MAS namespaces is denied by default. Allowed flows are declared explicitly in a `CASAPolicy`:

```yaml
apiVersion: casa.io/v1alpha1
kind: CASAPolicy
metadata:
    name: agent-policy
    namespace: production-mas
spec:
    targetRef:
        kind: Deployment
        name: my-agent
    allowedProtocols:
        - mcp
        - a2a
    allowedEndpoints:
        - name: my-mcp-server
          namespace: production-mas
          port: 8080
        - name: casa-auth-service
          namespace: casa-runtime
          port: 8443
```

### LLM endpoint restriction

Agents are restricted to a single approved external LLM FQDN via the `llmEndpoint` field:

```yaml
apiVersion: casa.io/v1alpha1
kind: CASAPolicy
metadata:
    name: agent-policy
    namespace: production-mas
spec:
    targetRef:
        kind: Deployment
        name: my-agent
    llmEndpoint:
        fqdn: api.openai.com
        port: 443
```

Only the declared FQDN is reachable. All other external destinations are dropped.

## CASAPolicy CRD

:::caution In Development
`CASAPolicy` is currently in development and not yet available in the stable release. See [Concepts — CRDs](/concepts/crds) for full details.
:::

The `CASAPolicy` CRD provides a Kubernetes-native way to declare per-workload network policies. The CASA operator reconciles these into network enforcement policies automatically:

```yaml
apiVersion: casa.io/v1alpha1
kind: CASAPolicy
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
        - name: casa-auth-service
          namespace: casa-runtime
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

:::info Roadmap
Deeper eBPF flow observability (token-correlated flow logs) is available in the planned Cilium deployment mode.
:::

Observability and tracing for both deployment modes are provided by the **CASA Explorer UI**, which surfaces:

- Real-time token event logs (issuance, exchange, introspection)
- Tool check decisions and denial reasons
- Per-MAS telemetry traces correlated with user prompts
- Network flow verdicts (ALLOWED / DENIED) correlated with token metadata
