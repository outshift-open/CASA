---
id: overview
slug: /overview
sidebar_position: 1
title: Overview
---

# CASA — Continuous Agent Semantic Authorization

CASA is a cloud-native Kubernetes platform that enforces intent-aware authorization for Multi-Agent Systems (MAS) at runtime - without requiring code changes to agents, tools or MCP servers.

## What problem does it solve?

With the rise of multi-agent systems and cross-vendor ecosystems, runtime authorization is required to maintain control over agent actions. AI systems are rapidly evolving into multi-agent systems where autonomous agents dynamically execute tasks across tools and services. Those agents call tools, invoke other agents, and access external service.These interactions are composed dynamically at runtime making it impossible to predefine all allowed behaviors.

Standard access control mechanisms (RBAC, OAuth scopes, API keys) are not built for this. They authorize access (who can call what), but cannot govern intent (why an action is being taken). An agent that has been granted access to a filesystem tool can use that tool for any purpose — including purposes the user never intended.

CASA introduces intent-scoped authorization - evaluating every action against user prompt, task context, and policy constraints. If the action does not match the intent, it is blocked before the tool executes — at the network level, not inside the application.

## Key capabilities

- **Adopt instantly with no code changes** — enforcement runs via sidecars and eBPF, fully decoupled from application logic
- **Kubernetes-native** — deploy via Helm, configure via CRDs
- **Graduated policy checks** — from fast deterministic validation to AI-powered intent matching
- **Flexible enforcement layer** — integrates with existing service mesh and networking stacks, with deeper eBPF-based enforcement for advanced control
- **Full observability** - every decision is logged and traceable, enabling audit and policy validation.

## Where to go next

- **Want to understand the design?** Read [Architecture Overview](/architecture/architecture-overview)
- **Ready to deploy?** Go to [Installation — Prerequisites](/installation/prerequisites)
