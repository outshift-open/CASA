# CASA Documentation Strategy

This document defines the information architecture and content decisions for the CASA project documentation. It is intended for contributors and maintainers, not end users.

---

## 1. Documentation Strategy

### Target Audiences

| Audience | Goal | Entry Point |
|---|---|---|
| Platform engineers / DevOps | Deploy CASA control plane into a K8s cluster | README → Installation |
| MAS application developers | Register and configure a Multi-Agent System | README → Concepts → CRDs |
| Security engineers | Understand trust model, policy checks, enforcement layers | Architecture → Concepts |
| OSS contributors | Understand codebase and contribute | Contributing |

### What Belongs in the README

- One-line description + badges
- Why CASA exists (problem statement, max 3 paragraphs)
- High-level architecture diagram (single Mermaid diagram)
- Core concept definitions (one paragraph each, no deep internals)
- Quick start (Helm install, minimal steps)
- Repository structure table
- Project status / maturity disclaimer
- Pointers to docs portal, CONTRIBUTING, LICENSE

### What Belongs in the Docs Portal

- Deep architecture explanations (control plane components, sidecar internals, eBPF enforcement)
- Full configuration reference (all Helm values, CRD fields)
- Deployment mode guides (Istio vs Cilium)
- Concept deep-dives (token flow, tool checks, MAS model)
- Demo walkthrough with expected outputs
- Operations guides (upgrade, troubleshooting)
- Contributing guide

### What Stays Out of v1 Docs

- Production HA deployment guide (current chart is single-replica PoC)
- Redis, telemetry service, AI pipeline service (not yet in the chart)
- SDK / API reference (auto-generated from code, out of scope for now)
- Performance tuning

---

## 2. Information Architecture

### Navigation Structure

```
docs/
├── Overview                        ← brief orientation, links to sections
├── Architecture
│   ├── Overview                    ← global diagram + component summary
│   ├── Control Plane               ← auth service, Keycloak, PostgreSQL, UI Explorer
│   ├── CASA Sidecar                 ← Envoy-based, inbound/outbound, iptables, ext-authz
│   └── eBPF Enforcement            ← Cilium L3/L4, JWT extraction, observability
├── Concepts
│   ├── Multi-Agent Systems         ← MAS model, app types (agent, client, mcp_server)
│   ├── CRDs                        ← MultiAgentSystem, CASAPolicy
│   ├── Token Flow                  ← OAuth2 client credentials, token exchange, introspection
│   ├── Deterministic Checks        ← DETERMINISTIC_TOOL_SELECTED, DETERMINISTIC_LLM_SELECTED_TOOLS
│   └── Semantic Checks             ← AI_POWERED_TOOL_MATCH, embeddings, LLM verifier
├── Installation
│   ├── Prerequisites               ← kubectl, helm, cluster requirements
│   ├── Control Plane               ← helm install casa-control-plane
│   └── Demo MAS                    ← helm install casa-mas
├── Configuration
│   ├── Control Plane Values        ← values.yaml field reference
│   ├── Demo MAS Values             ← values.yaml field reference
│   └── CRDs Reference              ← field-by-field for MultiAgentSystem and CASAPolicy
├── Deployment Modes
│   ├── Istio                       ← ext-authz middleware, namespace labeling, OTEL
│   └── Cilium                      ← CiliumNetworkPolicy, eBPF programs, Hubble
├── Demo Walkthrough                ← end-to-end scenario with expected output
├── Operations
│   ├── Troubleshooting             ← common issues, logs to check, error messages
│   └── Upgrade                     ← chart upgrade, CRD migration, rolling restarts
└── Contributing                    ← how to set up dev env, PR process, code style
```

### Page Hierarchy Rules

- Maximum 2 levels deep in sidebar
- Architecture and Concepts pages are reference material; they should be readable independently
- Installation pages are task-oriented (ordered steps)
- Configuration pages are reference-oriented (tables with field descriptions)

---

## 3. Packaging and Configuration Decisions

### Control Plane Chart (`casa-control-plane`)

**Present as:** A self-contained Helm chart that deploys the CASA control plane. All dependencies (PostgreSQL for auth, PostgreSQL for Keycloak, Keycloak) are bundled by default and can be disabled to use externally managed services.

**Dependency handling:**
- `postgresAuth.enabled` / `postgresKeycloak.enabled` — set to `false` to use an external Postgres
- `keycloak.enabled` — set to `false` to use an external Keycloak (or future OIDC provider)
- Ingress disabled by default; enable and set `apiDomainName` for external access

**Key config groups:**
- `authService.*` — the identity/token server (image, replicas, database connection, IdP URL, ingress)
- `uiExplorer.*` — the admin UI (image, ingress, API proxy toggle)
- `postgresAuth.*` / `postgresKeycloak.*` — bundled PostgreSQL instances
- `keycloak.*` — bundled Keycloak IdP

**What to document vs omit:**
- Document all top-level keys with their defaults and purpose
- Omit internal helpers and template internals
- Note that `authorizationServer` in MultiAgentSystem CRD is transitional (scheduled for removal)

### Demo MAS Chart (`casa-mas`)

**Present as:** A minimal reference deployment of a Multi-Agent System (one agent + one MCP server) used to demonstrate CASA enforcement. Not production-ready; intended for learning and testing.

**Key config:**
- `agent.mcp_server_url` — MCP server URL the agent will call
- `agent.secret.openai_api_base` + `agent.secret.openai_api_key` — LLM endpoint config
- Images are currently in a private ECR registry; users need to provide their own images or build from source in `demo/src/agent/` and `demo/src/mcp/`

### Istio vs Cilium Documentation Strategy

Both modes are first-class. Present them as two deployment options:

| | Istio Mode | Cilium Mode |
|---|---|---|
| Sidecar injection | Istio automatic injection (`istio-injection=enabled` label) | Custom mutating webhook |
| L7 enforcement | `ext_authz_middleware` (Go service) via Envoy ext_authz filter | CASA sidecar (Envoy + Lua filters) |
| L3/L4 enforcement | Istio NetworkPolicy (limited) | CiliumNetworkPolicy (recommended) |
| Observability | OpenTelemetry + Jaeger (via OTEL collector) | Hubble + Prometheus |
| Current status | Used in existing deployments | Described in SPECS, roadmap |

**Istio mode** is the currently deployed approach (evidenced by `docs/dev/sidecar.md` and `ext_authz_middleware/`). Lead with it in the deployment modes section.

**Cilium mode** is the target architecture per SPECS.md — document it as the production recommendation.

---

## 4. Config Taxonomy

### Platform Config (cluster-level, set once)

Controls infrastructure concerns:
- Database connection (host, port, credentials)
- IdP / Keycloak configuration
- Ingress class and domain names
- Resource limits and replica counts
- Storage class for persistence

### App Config (per-MAS deployment)

Configures the MAS workloads:
- Agent image, port, MCP server URL
- MCP server image, port
- Namespace

### Policy Config (CRD-driven, per-workload)

Defines Zero Trust enforcement rules:
- `MultiAgentSystem` — which apps are in the system, which tool checks are enabled
- `CASAPolicy` — per-workload allowed protocols, allowed endpoints, LLM endpoint

### Integration Config (external system references)

Points CASA at external services:
- LLM endpoint FQDN (OpenAI-compatible API)
- External Keycloak URL (when not using bundled Keycloak)
- External PostgreSQL DSN

---

## 5. Diagram Plan

### Primary Diagram — Global Architecture (in README + Architecture Overview page)

Single Mermaid diagram showing:
- Kubernetes cluster boundary
- Control plane namespace: Auth Service, Keycloak, PostgreSQL, UI Explorer
- MAS namespace: client pod, agent pod, MCP server pod, each with sidecar
- eBPF/Cilium enforcement layer
- External LLM endpoint
- Token exchange flow (simple arrows, not full sequence)

**Rule:** Keep it high-level enough to be understood in 30 seconds. Do not show internal service decomposition.

### Optional Diagram — Token Flow Sequence (in `concepts/token-flow.md` only)

Mermaid sequence diagram showing:
1. User submits prompt → client sidecar requests token from control plane
2. Agent receives request → sidecar exchanges token for LLM-scoped token
3. Agent calls LLM → eBPF validates token, forwards
4. Agent requests MCP token → control plane runs tool checks
5. Agent calls MCP server → MCP sidecar introspects token, forwards

No other diagrams needed for v1.

---

## 6. README Plan

### Sections (in order)

1. Badges (existing pytest + pre-commit CI badges)
2. `# CASA — Continuous Agent Semantic Authorization`
3. One-sentence description
4. `## Why CASA` — problem statement (3 short paragraphs)
5. `## Architecture` — Mermaid diagram + brief component list
6. `## Core Concepts` — 6 definitions (Control Plane, MAS, CASA Sidecar, MultiAgentSystem CRD, Deterministic Checks, Semantic Checks)
7. `## Quick Start` — 5-step Helm deployment
8. `## Repository Structure` — directory table
9. `## Project Status` — alpha disclaimer
10. `## Contributing` — pointer to CONTRIBUTING
11. `## License` — Apache 2.0 note

### Tone Guidelines

- Write for a senior engineer who has never heard of CASA before
- Lead with "what it does" not "how it works"
- Be direct; no buzzword stacking
- Avoid: "revolutionary", "seamlessly", "powerful", "leverage"
- Prefer: concrete nouns, active verbs, present tense
- Keep Quick Start to ≤10 commands

---

## 7. Docs Portal Decision — Docusaurus

**Selected: Docusaurus v3 (classic preset)**

**Rationale:**

| Factor | Docusaurus | Docsify |
|---|---|---|
| Navigation complexity | Handles multi-level sidebar well | Flat sidebar, gets unwieldy |
| Versioning | Built-in versioning (critical for v1alpha1 CRDs) | No versioning |
| Build output | Static HTML (deployable anywhere) | Runtime JS (needs server or CDN) |
| Search | Algolia DocSearch integration | Limited |
| OSS ecosystem fit | Used by React, Jest, Babel, Docusaurus itself | Smaller ecosystem |
| MDX support | Yes (rich interactive content) | No |
| Local dev | `npm start` with hot reload | Simple but limited |
| Future scalability | Version branches, i18n, plugin ecosystem | Harder to grow |

Docsify would be simpler for a single-page quick-reference. CASA has ~20 doc pages with distinct sections and will add versioning as the CRD API matures. Docusaurus is the right long-term choice.

**Local run:** `cd docs/ui && npm install && npm start`
**Build:** `cd docs/ui && npm run build` (outputs to `docs/ui/build/`)
**Deploy:** Drop `docs/ui/build/` into any static host (GitHub Pages, Netlify, S3)
