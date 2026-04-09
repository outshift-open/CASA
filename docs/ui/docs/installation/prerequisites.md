---
id: prerequisites
sidebar_position: 1
title: Prerequisites
---

# Prerequisites

Before installing ZTA, ensure the following are in place.

## Kubernetes Cluster

- **Version:** Kubernetes 1.26+
- **Tested on:** kind, EKS, GKE, AKS
- **Node requirements:** At least 2 nodes with 4 CPU / 8 GB RAM each for the control plane + a demo MAS

## CLI Tools

| Tool | Version | Purpose |
|---|---|---|
| `kubectl` | 1.26+ | Apply manifests and interact with the cluster |
| `helm` | 3.10+ | Install ZTA charts |

## Dataplane

ZTA requires one of the following dataplanes to be installed and operational in your cluster.

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

The ZTA control plane images are published to GitHub Container Registry (GHCR):

- `ghcr.io/cisco-eti/identity-auth-server` — auth service
- `ghcr.io/cisco-eti/identity-auth-server-ui` — UI explorer
- `ghcr.io/cisco-eti/identity-auth-server-keycloak` — custom Keycloak image

These images are public. No registry authentication is required.

> **Note:** The demo MAS chart (`zta-mas`) uses private ECR images by default. To use the demo chart, you must either build your own images from `demo/k8s/agent/` and `demo/k8s/mcp/`, or use the images from a registry you control. Update `demo/k8s/helm/values.yaml` with your registry and image paths.

## Storage

The control plane requires persistent volumes for PostgreSQL. Your cluster must have a default StorageClass that supports `ReadWriteOnce` volumes, or you must specify a `storageClass` in the Helm values.

Check the default StorageClass:

```bash
kubectl get storageclass
```

## Next Step

[Install the Control Plane →](control-plane.md)
