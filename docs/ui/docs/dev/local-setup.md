---
id: local-setup
sidebar_position: 1
title: Local Standalone Setup
slug: /dev/local-setup
---

# Local Standalone Setup

`scripts/dev/local-setup-standalone.sh` bootstraps a full CASA stack on a local Minikube cluster in a single command. It builds all images from source, deploys the control plane and demo agents via Helm, sets up Istio, and starts port-forwards so every service is reachable immediately.

No external YAML files are needed — all Helm values are inlined in the script.

## Prerequisites

Install the required CLI tools:

```bash
brew install minikube istioctl helm kubectl crane
```

Docker Desktop (or equivalent) must be running before you start.

## Environment Variables

Export these before running the script.

### Required

| Variable | Description |
|---|---|
| `CASA_LLM_HOST` | Hostname of the OpenAI-compatible LLM API (e.g. `litellm.example.com`) |
| `CASA_LLM_API_KEY` | API key used for both the auth service LLM calls and the demo agents |

### Optional

| Variable | Default | Description |
|---|---|---|
| `CASA_LLM_MODEL_ID` | `bedrock/global.anthropic.claude-sonnet-4-6` | Model used for auth-check semantic verification |

The script derives `http://${CASA_LLM_HOST}` for all helm parameters that expect the full base URL.

## Usage

```bash
export CASA_LLM_HOST=your-llm-host.example.com
export CASA_LLM_API_KEY=your-api-key

# Install / upgrade
bash scripts/dev/local-setup-standalone.sh

# Wipe all data and reinstall from scratch
bash scripts/dev/local-setup-standalone.sh reset
```

## What the Script Does

| Step | Action |
|---|---|
| 1 | Starts Minikube (docker driver, 7 GB RAM, 6 CPUs); enables `registry` and `ingress` addons |
| 2 | Installs Istio with the minimal profile |
| 3 | Creates the `casa-dev` namespace with Istio injection enabled |
| 4 | Builds all Docker images locally (control plane, sidecars, demo agents, UIs) and pushes Wasm plugins to the in-cluster registry |
| 5 | Installs/upgrades the `casa-runtime` Helm chart (`casa-dev` release) including the sidecar subchart |
| 6 | Installs/upgrades the demo agents Helm chart (`casa-demo` release) |
| 7 | Waits for all pods to reach the `Ready` state |
| 8 | Starts port-forwards and patches `/etc/hosts` for ingress hostnames |

## Services After Setup

| Service | Address |
|---|---|
| Auth server API | `http://localhost:8000` (Swagger: `/docs`) |
| Keycloak | `http://localhost:8080` |
| Jaeger traces | `http://localhost:16686` |
| Explorer UI | `http://explorer.casa.outshift.ai` |
| Safe chat UI | `http://chat-safe.casa.outshift.ai` |
| Compromised chat UI | `http://chat-compromised.casa.outshift.ai` |

## Reset Mode

The `reset` argument strips MAS finalizers, uninstalls both Helm releases, and deletes all PVCs before re-running the full install. Use it when you want a clean slate without tearing down Minikube itself:

```bash
bash scripts/dev/local-setup-standalone.sh reset
```

To fully tear down the cluster, run `minikube delete`.
