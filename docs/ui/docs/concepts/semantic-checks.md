---
id: semantic-checks
sidebar_position: 5
title: Semantic Checks
---

# Semantic Checks

Semantic checks use AI inference to validate that a requested tool actually matches the user's original intent. They go beyond rule-based validation to catch cases where a tool is technically permitted but semantically wrong for the request.

## The Problem Semantic Checks Solve

Consider a user who asks: *"Get my account balance."*

Deterministic checks would pass if `filesystem:read` was in the allowed tools list. But did the user intend to read files? Probably not. Semantic checks catch this discrepancy.

## AI_POWERED_TOOL_MATCH

**What it checks:** Does the requested tool semantically match the user's original task?

This check uses one of three matching strategies:

| Strategy | How it works | Latency | Accuracy |
|---|---|---|---|
| `embeddings` | Compares task embedding to tool description embedding | +100–200ms | Good |
| `llm_verifier` | Asks an LLM: "Does this tool match this task?" | +1–2s | High |
| `hybrid` | Embeddings first, LLM for borderline cases | variable | Highest |

The threshold and strategy are configured in the AI Pipeline Service (not yet exposed as a CRD field in the current release).

### Example

User task: *"Get the account summary and scheduled payments"*

Token exchange request: agent wants `filesystem:write`

**Semantic check result:** ❌ DENY — writing to a filesystem does not match retrieving account summaries.

Token exchange request: agent wants `banking:get_account_summary`

**Semantic check result:** ✅ PASS — getting an account summary matches the user's task.

## Enabling Semantic Checks

```yaml
spec:
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  - DETERMINISTIC_LLM_SELECTED_TOOLS
  - AI_POWERED_TOOL_MATCH            # add this for semantic validation
```

## Latency Trade-off

Semantic checks add significant latency to token exchange:
- Embeddings: ~100–200ms
- LLM verifier: ~1–2 seconds per tool check

Use semantic checks for:
- High-security workflows (financial, medical, file system access)
- Scenarios where agents interact with untrusted or dynamic MCP servers
- Regulatory contexts requiring intent audit trails

For low-latency workflows, use deterministic checks only and add semantic checks selectively.

## Caching

Results from semantic checks are cached by `(task, tool)` pair for 1 hour. For a given user task asking for the same tool, the AI inference runs only once.

## Current Status

The AI Pipeline Service that handles semantic checks is defined in the roadmap (see `contrib/wip/it1/SPECS.md`) but is not yet a separate microservice in the current Helm chart. In the current release, semantic check logic runs within the monolithic auth service.
