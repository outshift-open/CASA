---
id: install-runtime
sidebar_position: 2
title: Install Runtime
---

# Install the CASA Runtime

The CASA runtime is distributed as the `casa-runtime` Helm chart, published to GHCR as an OCI artifact. It bundles both the control-plane components and the sidecar via the `ext-auth-service` subchart.

## Install from GHCR (recommended)

First, create the namespace and enable Istio sidecar injection:

```bash
kubectl create namespace casa-dev
kubectl label namespace casa-dev istio-injection=enabled
```

> Without the `istio-injection=enabled` label, agent and MCP pods will not receive Istio sidecar proxies and CASA enforcement will not work.

Then install the chart.

At minimum you must supply the LLM endpoint credentials — everything else has a working default:

```bash
helm install casa-dev oci://ghcr.io/outshift-open/helm/casa-runtime \
  --version 0.1.17 \
  --namespace casa-dev \
  --set authService.openai.apiBaseUrl="https://your-llm-endpoint" \
  --set authService.openai.jwtToken="YOUR_PIPELINE_TOKEN" \
  --set authService.openai.llmApiBaseUrl="https://your-llm-endpoint" \
  --set authService.openai.llmApiKey="YOUR_LLM_KEY" \
  --set authService.openai.modelId="gpt-4o" \
  --set authService.openai.pipelineModelId="gpt-4o"
```

No `helm repo add` is needed — OCI charts are pulled directly. All images are public; no registry authentication is required.

> **Default passwords** `authService.database.password` and `authService.idp.adminPassword` default to `postgres`/`admin`. Override them for any non-local deployment — see [Production Configuration](#production-configuration).

## Install from source

```bash
# Clone the repo, then create the namespace:
kubectl create namespace casa-dev
kubectl label namespace casa-dev istio-injection=enabled

helm dependency build deployments/helm/casa-runtime/
helm install casa-dev deployments/helm/casa-runtime/ \
  --namespace casa-dev
```

`helm dependency build` is required to download the sidecar subchart before the first install from source.

## What gets installed

The chart deploys the full control plane plus the sidecar in a single release:

| Component | Description |
|---|---|
| `casa-dev-auth-service` | FastAPI authorization server |
| `casa-dev-ui-explorer` | CASA Explorer web UI |
| `casa-dev-keycloak` | Keycloak IdP (pre-configured) |
| `casa-dev-postgres-auth` | PostgreSQL for the auth service |
| `casa-dev-postgres-keycloak` | PostgreSQL for Keycloak |
| `casa-dev-operator` | Kubernetes operator (reconciles `MultiAgentSystem` CRDs) |
| `casa-dev-sidecar-*` | Ext-auth service, otel-collector, Jaeger, eBPF instrumentation |

Wait for all pods to be ready:

```bash
kubectl -n casa-dev wait --for=condition=ready pod --all --timeout=300s
```

## Production Configuration

For production deployments, create a `values-prod.yaml` that configures credentials, the LLM backend, and ingress.

### Credentials & LLM backend

CASA requires credentials for the PostgreSQL database, the Keycloak admin account, and an OpenAI-compatible LLM endpoint. The auth service uses **two OpenAI client instances** internally — both for the authorization pipeline, not for the demo agents:

- **`apiBaseUrl` / `jwtToken`** — used by the LLM verifier and hybrid tool matcher (bearer-token auth)
- **`llmApiBaseUrl` / `llmApiKey`** — used by the task extractor and tool matcher (API-key auth)

In practice both pairs point to the same endpoint. They exist as separate config because the pipeline components were built with different OpenAI client setups:

```yaml
authService:
  database:
    password: "CHANGE_ME"
  idp:
    adminPassword: "CHANGE_ME"
  openai:
    apiBaseUrl: "https://your-litellm-or-openai-endpoint"     # pipeline LLM verifier
    jwtToken: "CHANGE_ME"                                      # bearer token for above
    llmApiBaseUrl: "https://your-litellm-or-openai-endpoint"  # pipeline task extractor
    llmApiKey: "CHANGE_ME"                                     # API key for above
    modelId: "bedrock/global.anthropic.claude-sonnet-4-6"     # model for both pipeline clients
    pipelineModelId: "azure/gpt-4o"                           # model for embedding/tool matching
```

> All six `openai.*` fields are required — the auth service will start but authorization checks will fail silently if any are empty.

### Ingress

Each component exposes an `ingress` block. Set `className`, `apiDomainName`, and `domainPrefix` — the resulting hostname is `<domainPrefix>.<apiDomainName>`. Use `annotations` for cert-manager or any other ingress annotation:

```yaml
authService:
  ingress:
    enabled: true
    className: "nginx-internal"
    apiDomainName: "dev.eticloud.io"
    domainPrefix: "casa-auth"        # → casa-auth.dev.eticloud.io
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt

uiExplorer:
  ingress:
    enabled: true
    className: "nginx-internal"
    apiDomainName: "dev.eticloud.io"
    domainPrefix: "casa-explorer"    # → casa-explorer.dev.eticloud.io
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt

keycloak:
  hostname: "casa-keycloak.dev.eticloud.io"
  hostnamePort: 443
  ingress:
    enabled: true
    className: "nginx-internal"
    apiDomainName: "dev.eticloud.io"
    domainPrefix: "casa-keycloak"    # → casa-keycloak.dev.eticloud.io
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt
```

> `keycloak.hostname` must match the ingress hostname exactly — Keycloak uses it to build redirect URIs.

### Other common overrides

```yaml
authService:
  replicaCount: 3

postgresAuth:
  persistence:
    enabled: false   # when using an external PostgreSQL instance

postgresKeycloak:
  persistence:
    enabled: false   # when using an external PostgreSQL instance

sidecar:
  enabled: true      # deploy the ext-auth-service subchart
```

### Full example values file

```yaml
# values-prod.yaml
authService:
  replicaCount: 3
  database:
    password: "CHANGE_ME"
  idp:
    adminPassword: "CHANGE_ME"
  openai:
    apiBaseUrl: "https://your-litellm-or-openai-endpoint"     # pipeline endpoint
    jwtToken: "CHANGE_ME"                                      # bearer token for pipeline
    llmApiBaseUrl: "https://your-litellm-or-openai-endpoint"  # agent-facing endpoint
    llmApiKey: "CHANGE_ME"                                     # key for agent-facing endpoint
    modelId: "bedrock/global.anthropic.claude-sonnet-4-6"     # model for authorization pipeline
    pipelineModelId: "azure/gpt-4o"                           # model for embedding/tool matching
  ingress:
    enabled: true
    className: "nginx-internal"
    apiDomainName: "dev.eticloud.io"
    domainPrefix: "casa-auth"
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt

uiExplorer:
  ingress:
    enabled: true
    className: "nginx-internal"
    apiDomainName: "dev.eticloud.io"
    domainPrefix: "casa-explorer"
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt

keycloak:
  hostname: "casa-keycloak.dev.eticloud.io"
  hostnamePort: 443
  ingress:
    enabled: true
    className: "nginx-internal"
    apiDomainName: "dev.eticloud.io"
    domainPrefix: "casa-keycloak"
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt

postgresAuth:
  persistence:
    enabled: false

postgresKeycloak:
  persistence:
    enabled: false

sidecar:
  enabled: true
```

Install with the custom values:

```bash
kubectl create namespace casa-dev
kubectl label namespace casa-dev istio-injection=enabled

helm install casa-dev oci://ghcr.io/outshift-open/helm/casa-runtime \
  --version 0.1.17 \
  --namespace casa-dev \
  -f values-prod.yaml
```

## Verify the Installation

Check the auth service health:

```bash
kubectl -n casa-dev port-forward svc/casa-dev-auth-service 8000:8000 &
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

Access the UI:

```bash
kubectl -n casa-dev port-forward svc/casa-dev-ui-explorer 8080:80 &
# Open http://localhost:8080 in your browser
```

## Apply CRDs

CRDs are included in the Helm chart and installed automatically. Verify they are present:

```bash
kubectl get crd | grep casa.io
# multiagentsystems.casa.io
# casapolicies.casa.io
```

## Next Step

[Install the Demo MAS →](demo-mas.md)

Or if you're deploying your own MAS, go to [Concepts — Multi-Agent Systems](/concepts/mas).
