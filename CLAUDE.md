# CASA — Continuous Agent Semantic Authorization

Python FastAPI auth/authorization server for intent-scoped continuous semantic authorization of Multi-Agent Systems (MAS). Deployed on Kubernetes with Keycloak, PostgreSQL, Envoy sidecars, and Cilium eBPF enforcement.

## Tech Stack

- **Backend**: Python 3.12+, FastAPI, SQLModel, SQLAlchemy, Keycloak (python-keycloak), PyJWT
- **Frontend**: React + TypeScript + Vite + Tailwind (`casa-explorer-ui/`)
- **Package manager**: `uv` (Python), `yarn` (frontend)
- **Linting/formatting**: `ruff` (lint + format), `mypy` (types), `shellcheck`
- **Pre-commit hooks**: enforced on commit and push; run `make check` to run manually

## Key Commands

```bash
make init              # Create venv, install deps, set up pre-commit hooks
make update            # Sync deps after pyproject.toml changes (runs uv sync --extra dev)
make test              # Run unit tests (pytest, excludes integration by default)
make test-integration  # Run integration tests (require live services)
make check             # Run all pre-commit checks (ruff, mypy, shellcheck, etc.)
make auth-server-run   # Start auth server locally (uvicorn, --reload, port 8000)
make docker-run        # Start full stack via Docker Compose
make docker-stop       # Stop Docker Compose stack
make keycloak-run      # Start Keycloak only (docker-compose.keycloak.yml)
make demo-run          # Start demo agents + LiteLLM
make ui-run            # Start CASA Explorer UI (docker-compose.ui.yml)
make demo-data         # Seed demo data (requires running backend)
make demo-data-reset   # Clear + reseed demo data
make generate-sdk      # Regenerate sdk/go/ from running server's OpenAPI spec (:8000)
```

## Gotchas

- **macOS**: system `make` is 3.81 (too old); use `gmake` instead of `make`
- **Python package name**: import as `casa_auth_server`, not `casa`
- `operator/` is Go, `sidecar/ext_auth/` is Go, `sidecar/llm_proxy/` and `sidecar/traceparent_injector/` are Rust — not Python

## Project Layout

```
src/casa_auth_server/   # Main Python package (casa_auth_server)
  api/                      # FastAPI app; routes: app, authorization, k8s, k8s_crd,
                            #   multi_agent_system, scope, trace, user_input
  core/                     # Business logic, repositories, IDP client
  services/                 # Service layer
  database/                 # SQLModel models, DB setup, Alembic migrations
  checks/                   # Authorization check logic
  k8s/                      # Kubernetes CRD types, service, repository
  pipelines/                # AI matching pipelines (task_tool_matcher: embeddings, LLM, hybrid)
  telemetry/                # OpenTelemetry integration
  thirdparty/               # Keycloak, external IdP wrappers
operator/                   # Go Kubernetes operator (reconciles MultiAgentSystem CRDs)
sidecar/                    # Envoy filter plugins (Go + Rust)
  ext_auth/                 # Go ext-authz service
  llm_proxy/                # Rust Wasm LLM proxy filter
  traceparent_injector/     # Rust Wasm traceparent filter
casa-explorer-ui/           # React/TypeScript observability UI — read-only (yarn)
sdk/go/                     # Generated Go SDK (do not edit directly)
demo/
  chat-ui/                  # React demo chat UI
  k8s/                      # Helm chart for demo MAS
deployments/
  docker/                   # Dockerfiles for all components
  docker-compose/           # docker-compose.yml, keycloak, demo, ui variants
  helm/                     # Helm charts: casa-runtime, sidecar
test/                       # Test stubs (no unit tests yet; integration/ and pipelines/ have structure)
docs/
  dev/                      # Internal developer notes, sequence diagrams, deployment guide
  dev/specs/                # WIP architecture specs and diagrams
  diagrams/                 # Architecture diagrams (drawio + png)
  screens/                  # UI screenshots
  ui/                       # Docusaurus 3.6 public docs site
scripts/                    # generate_sdk.sh (regenerates sdk/go/ from running server)
```

## Code Conventions

- Line length: 120 characters (`ruff` enforced)
- Docstrings: Google style (`ruff` pydocstyle convention)
- `__init__.py` files exempt from missing docstrings (D104), unused imports (F401, F403)
- `sdk/` directory is generated — excluded from all linters/formatters
- `demo/` excluded from pre-commit hooks

## Testing

- `pytest` config in `pyproject.toml`; tests live in `test/`
- Default run skips integration tests: `pytest` = unit tests only
- Integration tests tagged `@pytest.mark.integration`; run with `make test-integration`
- Integration tests require live Keycloak + PostgreSQL

## Environment

- Copy `.env.example` to `.env` before running locally (if present)
- Auth server runs on port 8000 by default
- SDK is generated from `http://localhost:8000/openapi.json` via `make generate-sdk`

## Docs Portal (docs/ui — Docusaurus 3.6)

- URL routing uses **file paths**, not `id` frontmatter — `id` is sidebar-reference only
- `src/pages/index.js` owns `/`; any doc with `slug: /` is silently overridden — use `slug: /overview` etc.
- Mermaid diagrams render with a yellow canvas by default; add `%%{init: {'theme': 'base', 'themeVariables': {'background': '#f0fdf4', 'edgeLabelBackground': '#f0fdf4'}}}%%` to override
- Mermaid sequence diagram arrow labels (`signalTextColor`) default to light — set to `#1e293b` for light backgrounds
