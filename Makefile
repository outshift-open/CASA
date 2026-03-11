# Check Make version (we need at least GNU Make 3.82)
ifeq ($(filter undefine,$(value .FEATURES)),)
$(error Unsupported Make version. \
    Make $(MAKE_VERSION) detected; please use GNU Make 3.82 or above.)
endif

# Parameters
PYTHON_VERSION = 3.12

# Helm parameters (override with make helm-install HELM_RELEASE=my-release HELM_NAMESPACE=my-ns)
HELM_CHART     = deployments/k8s/helm/zta-control-plane
HELM_RELEASE  ?= zta-poc
HELM_NAMESPACE ?= zta-dev

# Strict and safe set of defaults for Makefile
# see: https://tech.davis-hansson.com/p/make/
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
.RECIPEPREFIX = >

YELLOW := \033[1;33m
GREEN := \033[0;32m
RED := \033[0;31m
NOCOLOR := \033[0m

.DEFAULT_GOAL:=help

ifdef OS
  ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    ifeq ($(shell where nvidia-smi),)
      HAS_CUDA := No
    else
      HAS_CUDA := Yes
    endif
  else
    DETECTED_OS := Unknown
  endif
else
  DETECTED_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
  ifeq ($(DETECTED_OS), Darwin)
    HAS_CUDA := No
  else
    ifeq ($(shell which nvidia-smi),)
      HAS_CUDA := No
    else
      HAS_CUDA := Yes
    endif
  endif
endif

ifeq ($(DETECTED_OS), Windows)
  VENV_ACTIVATE = .venv/Scripts/Activate.ps1
else
  VENV_ACTIVATE = set +u; source .venv/bin/activate ; set -u;
endif

## Internal targets ##

# Delete and re-create the virtual environment.
_clean-env:
> @printf "$(YELLOW)Removing the virtual environment$(NOCOLOR)\n"
> rm -rf .venv
> rm -f uv.lock
> uv venv --python $(PYTHON_VERSION)
.PHONY: _clean-env

## Main targets ##

help: # Show the help for each of the Makefile recipes.
> @grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | \
  while read -r l; do \
    printf "$(GREEN)$$(echo $$l | cut -f 1 -d':')$(NOCOLOR):$$(echo $$l | cut -f 2- -d'#')\n"; \
  done
.PHONY: help

init: _clean-env update # Initialize the virtual environment.
> @printf "$(YELLOW)Initializing the environment$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> if [ -d ".git" ]; then \
    pre-commit install; \
  else \
    printf "$(YELLOW)Warning: git repository not found!$(NOCOLOR)\n"; \
    read -p "Should we run git init? [y/N]" ans; \
    if [ "$$ans" == "y" ] || [ "$$ans" == "Y" ]; then \
      git init; \
      git branch -m main; \
      git add .; \
      git commit -m "Initial commit"; \
      printf "$(YELLOW)Installing pre-commit hooks.$(NOCOLOR)\n"; \
      pre-commit install; \
    else \
      printf "$(YELLOW)\nPlease don't forget to install pre-commit hooks manually.$(NOCOLOR)\n"; \
      printf "Once the git repo is created, (e.g. after git init), run the\n"; \
      printf "following command at the root folder of the repo:\n"; \
      printf "$(GREEN)pre-commit install$(NOCOLOR)\n"; \
    fi; \
  fi;
.PHONY: init

update: pyproject.toml # Update the conda environment after changes to dependencies.
> @printf "$(YELLOW)Updating the virtual environment$(NOCOLOR)\n"
> rm -rf uv.lock  # Removing the lock file make uv slower, but avoids certain corner cases.
> uv sync --extra dev
.PHONY: update

clean: _clean-env update # Clean up the dist folder and the re-create the virtual environment.
> rm -rf dist/
.PHONY: clean

check: # Run all the pre-commit checks on the repo.
> @printf "$(YELLOW)Running code checkers$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> pre-commit run --all-files
.PHONY: check

build: update # Build the package. The Wheel file will be written in the dist folder.
> @printf "$(YELLOW)Running Python build$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> uv build  # use uv for faster builds
.PHONY: build

test: # Run all unit tests.
> @printf "$(YELLOW)Running Pytest$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> pytest
.PHONY: test

test-integration: # Run only integration tests.
> @printf "$(YELLOW)Running integration tests$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> pytest test/integration/ -m integration
.PHONY: test-integration

auth-server-run:
> source .venv/bin/activate
> uvicorn identity_auth_server.api.app:app --reload
.PHONY: auth-server-run

docker-build: # Build the Docker image.
> @printf "$(YELLOW)Building Docker image$(NOCOLOR)\n"
> docker build -f deployments/docker/Dockerfile -t identity-auth-server .
.PHONY: docker-build

docker-run: # Run the application using Docker Compose.
> @printf "$(YELLOW)Starting application with Docker Compose$(NOCOLOR)\n"
> cd deployments/docker-compose && docker compose up --build -d
.PHONY: docker-run

docker-stop: # Stop the Docker Compose services.
> @printf "$(YELLOW)Stopping Docker Compose services$(NOCOLOR)\n"
> cd deployments/docker-compose && docker compose down
.PHONY: docker-stop

keycloak-run:
> @printf "$(YELLOW)Starting Keycloak with Docker Compose$(NOCOLOR)\n"
> docker compose -f deployments/docker-compose/docker-compose.keycloak.yml up -d
.PHONY: keycloak-run

keycloak-stop:
> @printf "$(YELLOW)Stopping Keycloak$(NOCOLOR)\n"
> docker compose -f deployments/docker-compose/docker-compose.keycloak.yml down
.PHONY: keycloak-stop

demo-run:
> @printf "$(YELLOW)Starting the demo agents and LiteLLM with Docker Compose$(NOCOLOR)\n"
> docker compose -f deployments/docker-compose/docker-compose.demo.yml up -d
.PHONY: demo-run

demo-stop:
> @printf "$(YELLOW)Stopping the demo agents and LiteLLM$(NOCOLOR)\n"
> docker compose -f deployments/docker-compose/docker-compose.demo.yml down
.PHONY: demo-stop

ui-run: # Run the ZTA Explorer UI using Docker Compose.
> @printf "$(YELLOW)Starting ZTA Explorer UI with Docker Compose$(NOCOLOR)\n"
> cd deployments/docker-compose && docker compose -f docker-compose.ui.yml up --build -d
.PHONY: ui-run

ui-stop: # Stop the ZTA Explorer UI.
> @printf "$(YELLOW)Stopping ZTA Explorer UI$(NOCOLOR)\n"
> cd deployments/docker-compose && docker compose -f docker-compose.ui.yml down
.PHONY: ui-stop

generate-sdk:
> @printf "$(YELLOW)Generating the Python SDK for the Auth Server$(NOCOLOR)\n"
> @printf "$(YELLOW)Make sure the auth server is running first$(NOCOLOR)\n"
> curl -o openapi.json http://localhost:8000/openapi.json
> docker run --rm -v $(PWD):/local openapitools/openapi-generator-cli generate -i /local/openapi.json -g python -o /local/sdk --additional-properties=packageName=identity_auth_sdk
> rm openapi.json
.PHONY: generate-sdk

demo-data: # Create demo data in the backend (requires backend to be running).
> @printf "$(YELLOW)Creating demo data$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> python scripts/create_demo_data.py --verbose
.PHONY: demo-data

demo-data-dry-run: # Preview demo data that would be created without actually creating it.
> @printf "$(YELLOW)Running demo data generator in dry-run mode$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> python scripts/create_demo_data.py --dry-run
.PHONY: demo-data-dry-run

demo-data-clear: # Clear all existing data (does NOT recreate demo data).
> @printf "$(YELLOW)Clearing existing data$(NOCOLOR)\n"
> @printf "$(RED)WARNING: This will delete ALL existing data!$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> python scripts/create_demo_data.py --clear --verbose
.PHONY: demo-data-clear

demo-data-reset: # Clear all existing data and create fresh demo data.
> @printf "$(YELLOW)Resetting data: clearing and recreating$(NOCOLOR)\n"
> @printf "$(RED)WARNING: This will delete ALL existing data!$(NOCOLOR)\n"
> $(VENV_ACTIVATE)
> python scripts/create_demo_data.py --clear --verbose && python scripts/create_demo_data.py --verbose
.PHONY: demo-data-reset

helm-lint: # Lint the ZTA control-plane Helm chart.
> @printf "$(YELLOW)Linting Helm chart: $(HELM_CHART)$(NOCOLOR)\n"
> helm lint $(HELM_CHART)
.PHONY: helm-lint

helm-template: # Render Helm templates to stdout (dry-run).
> @printf "$(YELLOW)Rendering Helm templates (release=$(HELM_RELEASE), namespace=$(HELM_NAMESPACE))$(NOCOLOR)\n"
> helm template $(HELM_RELEASE) $(HELM_CHART) --namespace $(HELM_NAMESPACE)
.PHONY: helm-template

helm-install: # Install the ZTA control-plane chart (creates namespace if missing).
> @printf "$(YELLOW)Installing Helm release $(HELM_RELEASE) in namespace $(HELM_NAMESPACE)$(NOCOLOR)\n"
> helm install $(HELM_RELEASE) $(HELM_CHART) \
    --namespace $(HELM_NAMESPACE) \
    --create-namespace
.PHONY: helm-install

helm-upgrade: # Upgrade (or install) the ZTA control-plane chart.
> @printf "$(YELLOW)Upgrading Helm release $(HELM_RELEASE) in namespace $(HELM_NAMESPACE)$(NOCOLOR)\n"
> helm upgrade --install $(HELM_RELEASE) $(HELM_CHART) \
    --namespace $(HELM_NAMESPACE) \
    --create-namespace
.PHONY: helm-upgrade

helm-uninstall: # Uninstall the ZTA control-plane Helm release.
> @printf "$(RED)Uninstalling Helm release $(HELM_RELEASE) from namespace $(HELM_NAMESPACE)$(NOCOLOR)\n"
> helm uninstall $(HELM_RELEASE) --namespace $(HELM_NAMESPACE)
.PHONY: helm-uninstall

helm-status: # Show status of the ZTA control-plane Helm release.
> helm status $(HELM_RELEASE) --namespace $(HELM_NAMESPACE)
.PHONY: helm-status
