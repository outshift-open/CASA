---
id: runtime
sidebar_position: 2
title: Runtime
---

# Runtime

The CASA runtime is the authoritative source for identity, policy, and authorization decisions. It runs in a dedicated Kubernetes namespace (`casa-runtime`) and is deployed via the `casa-runtime` Helm chart.

## Current Architecture

The current release deploys a **monolithic auth service** — a single FastAPI application that handles token issuance, token exchange, token introspection, and MAS lifecycle management. This is intentional for the PoC/development phase.

The production architecture decomposes this into separate microservices. That decomposition is on the roadmap.

## Components

### Auth Service

The core of the runtime. Implemented in Python (FastAPI), backed by PostgreSQL.

**Endpoints:**

- `POST /oauth/token` — issues an initial token for a user input (client credentials flow)
- `POST /oauth/token/exchange` — exchanges a token for a delegated, scope-limited token; runs tool checks
- `POST /oauth/introspect` — validates a token and returns its claims
- `GET/POST /apps` — application registration and management
- `GET/POST /mas` — Multi-Agent System management

**Token exchange flow** (simplified):

1. Agent requests token exchange for tool `filesystem:read`
2. Auth Service checks: does the MAS have `DETERMINISTIC_TOOL_SELECTED` enabled? If so, is the tool in the token's allowed list?
3. If semantic checks are enabled: does the tool match the embeddings/LLM-verified intent?
4. If all checks pass: issue a new token scoped to `call-tools` with `tools=[filesystem:read]`
5. If any check fails: reject with 403

### Keycloak IdP

CASA uses a custom Keycloak image that includes the POIT HTTP-header protocol mapper. Keycloak handles:

- Token cryptography (signing, verification)
- Realm management (one realm per MAS in the current design)
- Client credential management

The custom image is published at `ghcr.io/outshift-open/CASA-keycloak`.


### PostgreSQL

Two PostgreSQL instances are bundled:

- `postgres-auth` — stores application registrations, MAS configuration, user inputs, tool metadata
- `postgres-keycloak` — Keycloak's own storage

Both can be replaced with externally managed PostgreSQL by setting `postgresAuth.enabled: false` / `postgresKeycloak.enabled: false` in `values.yaml`.

### Explorer UI

A React-based exploration and debug UI for:

- Browsing token events and tool call decisions in real time
- Inspecting token exchange traces correlated with user prompts
- Viewing registered MAS applications and their status

The UI connects to the auth service via an Nginx reverse proxy (when `uiExplorer.nginx.apiProxyEnabled: true`).

### Traces

The Traces component records all domain events and correlates them with eBPF flow data from the kernel layer:

- **State persistence** — stores token issuance, exchange, introspection, and tool check records in PostgreSQL
- **eBPF instrumentation** — receives JWT/flow events from the eBPF layer and correlates them with token metadata
- **Query API** — exposes trace records via `/trace`, consumed by the Explorer UI

See [Traces](traces.md) for full details.

## High Availability

The current Helm chart deploys single replicas. The auth service is stateless (state lives in PostgreSQL) and can be horizontally scaled by increasing `authService.replicaCount`.

Full HA configuration (including Keycloak clustering, PostgreSQL replication) is out of scope for the current release.

## Namespace Isolation

The runtime namespace (`casa-runtime`) should have network policies that:

- Allow inbound connections from MAS namespaces (for sidecar token operations)
- Deny all other inbound traffic
- Allow outbound to PostgreSQL and Keycloak only

Example `CASAPolicy` configuration is provided in the [Cilium deployment guide](/deployment-modes/cilium).
