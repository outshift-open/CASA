---
id: contributing
sidebar_position: 1
title: Contributing
slug: /contributing
---

# Contributing to CASA

Thank you for considering a contribution. This guide explains how to set up a development environment and submit changes.

## Getting Started

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — Python package manager
- Docker (for running tests that require PostgreSQL or Keycloak)
- `kubectl` and `helm` (for Kubernetes-related contributions)
- Node.js 18+ (for UI contributions)

### Clone and Initialize

```bash
git clone https://github.com/cisco-eti/identity-auth-server.git
cd identity-auth-server
make init
```

`make init` creates a Python virtual environment, installs all dependencies (including dev tools), and sets up pre-commit hooks.

### Set Up Environment

```bash
cp .env.sample .env
# Edit .env with your local configuration
```

### Run the Auth Service Locally

```bash
# Start PostgreSQL and Keycloak via Docker Compose
make keycloak-run

# Start the auth service with hot reload
make auth-server-run
```

The API is available at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

## Development Workflow

### Running Tests

```bash
# Unit tests (fast, no database required)
make test

# Integration tests (requires PostgreSQL + Keycloak running)
make test-integration

# All tests
make test && make test-integration
```

### Code Quality

All code changes must pass:

```bash
make check   # runs ruff (lint + format) and mypy (type checking)
```

Pre-commit hooks run these checks automatically on every commit. If you want to run them manually:

```bash
pre-commit run --all-files
```

### Helm Chart Changes

After changing Helm templates or values:

```bash
# Lint the chart
make helm-lint

# Render templates to review output
make helm-template
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes with appropriate tests
4. Run `make check` and `make test` to verify
5. Open a pull request against `main`

### Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Write a clear PR description explaining _what_ and _why_
- Reference any related issues
- Ensure all CI checks pass

### Commit Style

Use conventional commit messages:

```
feat: add semantic check result caching
fix: correct token TTL calculation for refresh
docs: add Cilium deployment mode guide
chore: update dependencies
```

## Repository Structure

| Area | Location | Notes |
|---|---|---|
| Auth service source | `src/identity_auth_server/` | Python / FastAPI |
| Auth service tests | `test/` | pytest; unit + integration |
| Control plane Helm chart | `deployments/helm/casa-control-plane/` | Helm v3 |
| Demo MAS Helm chart | `demo/k8s/helm/` | Helm v3 |
| Demo agent | `demo/src/agent/` | Python |
| Demo MCP server | `demo/src/mcp/` | Python |
| Demo client UI | `demo/src/client/` | React |
| ext-authz middleware | `ext_authz_middleware/` | Go |
| CASA Explorer UI | `casa-explorer-ui/` | React |
| Documentation | `docs/ui/` | Docusaurus |
| Architecture specs | `contrib/wip/it1/` | Internal reference |

## Reporting Issues

Please use [GitHub Issues](https://github.com/cisco-eti/identity-auth-server/issues) to report bugs or request features.

For security vulnerabilities, do not open a public issue. Contact the maintainers directly via the repository security advisory process.

## License

By contributing to CASA, you agree that your contributions will be licensed under the Apache 2.0 License.
