---
id: prerequisites
sidebar_position: 1
title: Prerequisites
---

# Prerequisites

Before installing CASA, ensure the following are in place.

## Kubernetes Cluster

- **Version:** Kubernetes 1.26+
- **Tested on:** kind, EKS, GKE, AKS
- **Node requirements:** At least 2 nodes with 4 CPU / 8 GB RAM each for the runtime + a demo MAS

## CLI Tools

| Tool         | Version | Purpose                                       |
| ------------ | ------- | --------------------------------------------- |
| `kubectl`    | 1.26+   | Apply manifests and interact with the cluster |
| `helm`       | 3.10+   | Install CASA charts                           |
| `istioctl`   | 1.17+   | Install and verify Istio                      |

## Dataplane

CASA requires one of the following dataplanes to be installed and operational in your cluster.

### Istio (for Istio deployment mode)

This is the **currently supported** dataplane.

Install Istio using the Istio CLI:

```bash
istioctl install --set profile=default -y
istioctl verify-install
```

Minimum version: Istio 1.17

### Cilium (for Cilium deployment mode)

> **Note: Cilium support is coming soon.** The instructions below document the planned setup. Cilium deployment mode is not yet available; use Istio for the current release.

Install Cilium using the Helm chart:

```bash
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --version 1.14.0 \
  --namespace kube-system \
  --set kubeProxyReplacement=true
```

Verify Cilium is ready:

```bash
cilium status --wait
```

Minimum version: Cilium 1.14

## Container Registry Access

All CASA runtime images are published publicly to GitHub Container Registry (GHCR) on every push to `main`:

| Image | GHCR path |
|---|---|
| Auth service | `ghcr.io/outshift-open/outshift-casa/casa-auth-server` |
| UI Explorer | `ghcr.io/outshift-open/outshift-casa/casa-auth-server-ui` |
| Keycloak | `ghcr.io/outshift-open/outshift-casa/casa-auth-server-keycloak` |
| Operator | `ghcr.io/outshift-open/outshift-casa/casa-operator` |
| Ext-auth service | `ghcr.io/outshift-open/outshift-casa/ext_auth_service` |
| LLM proxy (Wasm) | `ghcr.io/outshift-open/outshift-casa/llm_proxy_plugin` |
| Traceparent injector (Wasm) | `ghcr.io/outshift-open/outshift-casa/traceparent_injector_plugin` |

No authentication is required to pull these images.

Helm charts are also published publicly to GHCR as OCI artifacts:

```bash
# Install from GHCR directly (no helm repo add required)
helm install casa-dev oci://ghcr.io/outshift-open/helm/casa-runtime --version <version>
```

## Storage

The runtime requires persistent volumes for PostgreSQL. Your cluster must have a default StorageClass that supports `ReadWriteOnce` volumes, or you must specify a `storageClass` in the Helm values.

Check the default StorageClass:

```bash
kubectl get storageclass
```

## Next Step

[Install the Runtime →](runtime.md)
