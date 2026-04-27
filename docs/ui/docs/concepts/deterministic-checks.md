---
id: deterministic-checks
sidebar_position: 4
title: Deterministic Checks
---

# Deterministic Checks

Deterministic checks are rule-based validations that run synchronously during token exchange. They are fast, require no AI inference, and cover the majority of policy enforcement needs.

## Available Checks

### DETERMINISTIC_TOOL_SELECTED

**What it checks:** Is the requested tool present in the token's `tools` claim?

When an agent first receives a user input token (T1), that token encodes which tools the agent is allowed to use for this request. When the agent later requests a tool token (T3) for `filesystem:read`, this check verifies that `filesystem:read` was in the allowed tools list embedded in T1.

**Why it matters:** Prevents an agent from calling tools that were never granted for a particular user session, even if those tools exist in the MAS.

**Pass:** Tool is in the token's allowed list → exchange proceeds  
**Fail:** Tool not in the allowed list → 403 Forbidden

### DETERMINISTIC_LLM_SELECTED_TOOLS

**What it checks:** Did the LLM actually select this tool for this request?

When the agent calls the LLM and receives tool selections, the sidecar logs those selections to the CASA control plane. When the agent then requests a tool token, this check verifies that the tool was among those logged LLM selections for the current request.

**Why it matters:** Prevents prompt injection attacks where an agent is manipulated into requesting tools that the LLM never selected. A compromised MCP server could try to trick an agent into calling unintended tools; this check blocks that.

**Pass:** Tool was in the LLM's selection for this request → exchange proceeds  
**Fail:** Tool was not selected by the LLM → 403 Forbidden

## Enabling Checks

Checks are configured per MAS in the `MultiAgentSystem` CRD:

```yaml
spec:
  enabledToolChecks:
  - DETERMINISTIC_TOOL_SELECTED
  - DETERMINISTIC_LLM_SELECTED_TOOLS
```

You can enable one or both. If neither is specified, no checks run (all tool exchanges are approved).

## Performance

Deterministic checks add minimal latency to token exchange (< 5ms). They run before any AI inference, so they are suitable for production workloads where low latency is required.

For workflows where you want additional assurance that the tool actually matches the user's intent, add [Semantic Checks](semantic-checks.md) on top.

## Recommended Configuration

For most production MAS deployments:

```yaml
enabledToolChecks:
- DETERMINISTIC_TOOL_SELECTED       # always recommended
- DETERMINISTIC_LLM_SELECTED_TOOLS  # recommended if agents interact with untrusted MCP servers
```

Add `AI_POWERED_TOOL_MATCH` for high-security workflows where semantic intent validation is worth the latency trade-off.
