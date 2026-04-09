---
id: istio
sidebar_position: 1
title: Istio Deployment Mode
---

# Istio Deployment Mode

In Istio mode, ZTA uses Istio's sidecar injection to intercept traffic, and a custom Go ext-authz middleware to handle token operations.

This is the **currently deployed mode** for existing ZTA cluster environments.

## How It Works

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'background': '#0f172a', 'edgeLabelBackground': '#0f172a'}}}%%
graph LR
    Application --> Envoy["Envoy (Istio sidecar)"]
    Envoy --> ext_authz["ext_authz_middleware (Go gRPC)"]
    ext_authz --> ZTA["ZTA Control Plane"]

    style Application fill:#1e293b,stroke:#475569,color:#cbd5e1
    style Envoy fill:#1a2e05,stroke:#84cc16,color:#f1f5f9
    style ext_authz fill:#1a2e05,stroke:#84cc16,color:#f1f5f9
    style ZTA fill:#134e4a,stroke:#4ecdc4,color:#f1f5f9
```

> **eBPF support:** When Kubernetes nodes have eBPF enabled (kernel 5.8+), eBPF programs can run alongside Istio for JWT extraction and L4 enforcement — no Cilium required. See [eBPF Enforcement](/architecture/ebpf) for details.

1. Istio's sidecar injector automatically adds an Envoy proxy to each pod in labeled namespaces
2. Envoy's `ext_authz` filter sends every request to the `ext_authz_middleware` service for authorization
3. The middleware performs token operations (generation, validation) by calling the ZTA auth service
4. Telemetry and traces are surfaced in the **ZTA Explorer UI**

## Prerequisites

- Istio 1.17+ installed in your cluster
- ZTA control plane installed via the `zta-control-plane` Helm chart (includes ext_authz_middleware and all subcharts)

## Step 1: Label the Namespace

Enable Istio injection for your MAS namespace:

```bash
kubectl label namespace your-mas-namespace istio-injection=enabled
```

> Use a unique namespace name — do not use `zta-sidecar` if other teams are sharing the cluster.

## Step 2: Deploy the Demo MAS

```bash
cd demo/k8s/helm
helm install zta-mas -f values.yaml . --namespace your-mas-namespace
```

## Step 3: Verify

Test the end-to-end flow:

```bash
kubectl -n your-mas-namespace exec -it \
  $(kubectl -n your-mas-namespace get pods -o custom-columns=NAME:.metadata.name --no-headers | grep client) \
  -- wget -qO- \
  --header 'content-type: application/json' \
  --post-data '{"content": "Get the account summary and scheduled payments"}' \
  http://zta-demo-agent:8082/chat
```

Then open the ZTA Explorer UI to view the resulting token events and tool check decisions:

```bash
kubectl -n zta-control-plane port-forward svc/zta-ui-explorer 8080:80
# Open http://localhost:8080
```

## How the ext-authz Middleware Works

The middleware (`ext_authz_middleware/main.go`) implements the Envoy External Authorization API (gRPC):

1. **First request in a trace** (identified by `traceparent` header):
   - Generates a new user input token by calling the ZTA auth service
   - Stores the mapping between the trace ID and the user input ID
2. **Subsequent requests in the same trace:**
   - Performs token-based access control (TBAC) verification
   - Returns ALLOW or DENY to Envoy

The `traceparent` header follows the [W3C Trace Context](https://www.w3.org/TR/trace-context/) format: `{VERSION}-{TRACE_ID}-{SPAN_ID}-{FLAGS}`.

## Comparison with Cilium Mode (Roadmap)

| | Istio Mode | Cilium Mode |
|---|---|---|
| Sidecar | Istio Envoy | Custom ZTA Envoy |
| Injection | Istio automatic injection | Node-level daemonset |
| Auth enforcement | ext_authz_middleware (Go) | ZTA sidecar Lua filter |
| L4/L7 + eBPF | eBPF (node kernel) | ZTAPolicy + eBPF (integrated) |
| Observability | ZTA Explorer UI | ZTA Explorer UI |
| Status | Current | Coming soon (Roadmap) |
