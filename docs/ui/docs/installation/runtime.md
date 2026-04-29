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

Then install the chart:

```bash
helm install casa-dev oci://ghcr.io/outshift-open/helm/casa-runtime \
  --version 0.1.17 \
  --namespace casa-dev
```

No `helm repo add` is needed — OCI charts are pulled directly.

> **Private registry:** Until the packages are made public, authenticate first:
> ```bash
> helm registry login ghcr.io -u <github-username> --password <PAT>
> ```
> The PAT needs at minimum the `read:packages` scope.
>
> Create an `imagePullSecret` in **two namespaces** — `casa-dev` for pod image pulls, and
> `istio-system` for Wasm plugin pulls (Envoy fetches Wasm OCI images via Istiod, which reads
> pull credentials from `istio-system`):
> ```bash
> # App namespace — used by Kubernetes to pull container images
> kubectl create secret docker-registry regcred \
>   -n casa-dev \
>   --docker-server=ghcr.io \
>   --docker-username=<github-username> \
>   --docker-password=<PAT>
>
> # Istio namespace — used by Envoy/Istiod to pull Wasm OCI plugins
> kubectl create secret docker-registry regcred \
>   -n istio-system \
>   --docker-server=ghcr.io \
>   --docker-username=<github-username> \
>   --docker-password=<PAT>
> ```
>
> > **Why two namespaces?** The `llm_proxy_plugin` and `traceparent_injector_plugin` are
> > deployed as Istio `WasmPlugin` resources. If Istiod cannot authenticate the OCI pull from
> > `istio-system`, Envoy applies a **deny-all RBAC filter** and every proxied request returns
> > `403 Forbidden` — before CASA has a chance to evaluate it.
> >
> > Also pass the secret name to the chart so it is set on the `WasmPlugin` resources:
> > ```bash
> > --set sidecar.llm_proxy.image.pullSecret=regcred \
> > --set sidecar.traceparent_injector.image.pullSecret=regcred
> > ```

## Install from source

```bash
# Clone the repo, then:
helm dependency build deployments/helm/casa-runtime/
helm install casa-dev deployments/helm/casa-runtime/ \
  --namespace casa-dev \
  --create-namespace
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

CASA requires credentials for the PostgreSQL database, the Keycloak admin account, and an OpenAI-compatible LLM endpoint (used both for authorization pipeline embeddings and for agent-facing inference):

```yaml
authService:
  database:
    password: "CHANGE_ME"
  idp:
    adminPassword: "CHANGE_ME"
  openai:
    apiBaseUrl: "https://your-litellm-or-openai-endpoint"
    jwtToken: "CHANGE_ME"           # bearer token for the embedding/pipeline endpoint
    llmApiBaseUrl: "https://your-litellm-or-openai-endpoint"
    llmApiKey: "CHANGE_ME"
    modelId: "bedrock/global.anthropic.claude-sonnet-4-6"
    pipelineModelId: "azure/gpt-4o"
```

> `modelId` is the model used for the AI-powered authorization pipeline. `pipelineModelId` is the model used for embedding-based tool matching. Both values accept any model identifier supported by your LLM endpoint (OpenAI, LiteLLM proxy, Bedrock, etc.).

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
    apiBaseUrl: "https://your-litellm-or-openai-endpoint"
    jwtToken: "CHANGE_ME"
    llmApiBaseUrl: "https://your-litellm-or-openai-endpoint"
    llmApiKey: "CHANGE_ME"
    modelId: "bedrock/global.anthropic.claude-sonnet-4-6"
    pipelineModelId: "azure/gpt-4o"
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
helm install casa-dev oci://ghcr.io/outshift-open/helm/casa-runtime \
  --version 0.1.17 \
  --namespace casa-dev \
  --create-namespace \
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
