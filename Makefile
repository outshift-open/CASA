# Check Make version (we need at least GNU Make 3.82)
ifeq ($(filter undefine,$(value .FEATURES)),)
$(error Unsupported Make version. \
    Make $(MAKE_VERSION) detected; please use GNU Make 3.82 or above.)
endif

# Parameters
PYTHON_VERSION = 3.12

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
