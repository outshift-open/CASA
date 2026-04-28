---
id: explorer-ui
sidebar_position: 2
title: Explorer UI
---

# Explorer UI

The Explorer UI is a read-only observability UI for browsing token events, tool check decisions, and authorization traces. It does not manage or modify any configuration.

## Dashboard

Overview of all configured Multi-Agent Systems, application counts, tool call decisions (approved vs. blocked), and block reasons.

![Dashboard](/img/screens/dashboard.png)

## MAS Details — Info

Per-MAS configuration: MAS ID, registered agents/clients/MCP servers, scopes, and enabled authorization checks.

![MAS Details — Info](/img/screens/mas-info.png)

## MAS Details — Applications

Interactive graph view of the applications within a MAS (agents, clients, MCP servers) and their relationships.

![MAS Details — Applications](/img/screens/mas-tree.png)

## MAS Details — Traces

Token-level trace for each user session: token issuance, LLM selection events, and per-tool ALLOW/BLOCK decisions with check details.

![MAS Details — Traces](/img/screens/mas-traces.png)
