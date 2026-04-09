---
id: overview
slug: /
sidebar_position: 1
title: Overview
---

# ZTA — Zero Trust for Multi-Agent Systems

ZTA is a cloud-native Kubernetes platform that enforces Zero Trust authorization for Multi-Agent Systems (MAS) without requiring code changes in the agents or MCP servers.

## What problem does it solve?

AI applications increasingly delegate work to autonomous agents. Those agents call tools, invoke other agents, and access external services — often in combinations that could not have been anticipated when the system was designed.

Standard access control mechanisms (RBAC, OAuth scopes, API keys) are not built for this. They control *who* can call *what*, but not *why*. An agent that has been granted access to a filesystem tool can use that tool for any purpose — including purposes the user never intended.

ZTA adds **intent-scoped authorization**: every tool call is validated against the original user prompt. If the action does not match the intent, it is blocked before the tool executes — at the network level, not inside the application.

## Key properties

- **No code changes required** — enforcement is handled by sidecars and eBPF, not the application
- **Kubernetes-native** — deploy via Helm, configure via CRDs
- **Graduated policy checks** — from fast deterministic validation to AI-powered intent matching
- **Flexible dataplane** — works with Istio (current); Cilium eBPF support is on the roadmap

## Where to go next

- **New to ZTA?** Start with [Core Concepts — Multi-Agent Systems](/concepts/mas)
- **Ready to deploy?** Go to [Installation — Prerequisites](/installation/prerequisites)
- **Want to understand the design?** Read [Architecture Overview](/architecture/overview)
