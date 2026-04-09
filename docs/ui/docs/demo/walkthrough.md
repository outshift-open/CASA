---
id: walkthrough
sidebar_position: 1
title: Demo Walkthrough
---

# Demo Walkthrough

This walkthrough shows the complete ZTA enforcement flow using the demo MAS, from user prompt to tool execution.

## What the Demo Does

The demo has three components: a **Client UI** (chat interface), a **Demo Agent** (LLM-powered), and a **Demo MCP Server** (tool provider). The user interacts entirely through the Client UI — no curl or API calls needed.

The demo scenario:

1. A user types a message in the Client UI: *"Get the account summary and scheduled payments"*
2. The client forwards the conversation to the agent via its A2A endpoint
3. The agent calls an LLM to determine which tools to use
4. The LLM selects `get_account_summary` and `get_scheduled_payments` tools
5. The agent requests a tool token from ZTA for each tool
6. ZTA validates that each tool matches the user's intent (deterministic checks)
7. The agent calls the MCP server with the validated tokens
8. The MCP server executes the tools and returns results
9. The agent response appears in the Client UI
10. ZTA enforces and logs all token operations

## Prerequisites

- ZTA control plane running (see [Install Control Plane](/installation/control-plane))
- Demo MAS deployed and sidecar injection enabled (see [Install Demo MAS](/installation/demo-mas))
- `MultiAgentSystem` CRD applied

## Run the Demo

### 1. Open the Client UI

Port-forward the client service and open it in your browser:

```bash
kubectl -n zta-sidecar port-forward svc/zta-demo-client 3001:3001
# Open http://localhost:3001
```

Type a message such as *"Get the account summary and scheduled payments"* and send it. The client forwards the conversation to the agent, which calls the LLM, requests tool tokens from ZTA, and invokes the MCP server. The agent response appears directly in the chat.

### 2. Observe ZTA events in the Explorer UI

```bash
kubectl -n zta-control-plane port-forward svc/zta-ui-explorer 8080:80
# Open http://localhost:8080
```

In the ZTA Explorer UI, you should see:
- A user input event correlated with your prompt
- Token exchange events for T1 → T2 (LLM) and T1 → T3 (each tool)
- ALLOW decisions for `get_account_summary` and `get_scheduled_payments`

### 3. Test a semantic mismatch (when AI checks are enabled)

If `AI_POWERED_TOOL_MATCH` is enabled in the MAS configuration, send a narrower prompt from the Client UI:

> *"Get the account summary"*

If the agent attempts to also call a write tool, ZTA blocks it.

**Expected behavior:** The write tool call is rejected with 403. The agent returns a partial result using only the approved tools. In the ZTA Explorer UI, you should see:
- A DENY event for the write tool
- The check that failed: `AI_POWERED_TOOL_MATCH` — "filesystem:write does not match user intent: get account summary"

## What ZTA Does Internally

During the above request, ZTA:

1. **Receives token request** from the client UI sidecar (T1 issuance)
   - Stores the user's prompt correlated with the token
2. **Validates LLM token exchange** (T1 → T2)
   - Checks the agent's identity and scope
   - Issues T2 scoped to `llm-access`
3. **Logs LLM trace** — when the agent calls the LLM, the sidecar reports which tools the LLM selected
4. **Validates tool token exchange** (T1 → T3 for each tool)
   - `DETERMINISTIC_TOOL_SELECTED`: is this tool in T1's allowed list? ✅
   - `DETERMINISTIC_LLM_SELECTED_TOOLS`: did the LLM select this tool? ✅
   - `AI_POWERED_TOOL_MATCH` (if enabled): does this tool match the user's prompt? ✅
   - Issues T3 scoped to `call-tools` with `tools=[get_account_summary]`
5. **MCP sidecar introspects T3** — validates the token, checks that the tool being called matches the `tools` claim

## Checking Logs

View auth service logs during the request:

```bash
kubectl -n zta-control-plane logs -f deploy/zta-auth-service | grep -E "token|tool|check"
```

View sidecar logs (pick the relevant pod):

```bash
# Client sidecar
kubectl -n zta-sidecar logs -f deploy/zta-demo-client -c istio-proxy 2>/dev/null || \
kubectl -n zta-sidecar logs -f deploy/zta-demo-client -c zta-sidecar

# Agent sidecar
kubectl -n zta-sidecar logs -f deploy/zta-demo-agent -c istio-proxy 2>/dev/null || \
kubectl -n zta-sidecar logs -f deploy/zta-demo-agent -c zta-sidecar

# MCP sidecar
kubectl -n zta-sidecar logs -f deploy/zta-demo-mcp -c istio-proxy 2>/dev/null || \
kubectl -n zta-sidecar logs -f deploy/zta-demo-mcp -c zta-sidecar
```

## Cleanup

```bash
make mas-helm-uninstall
```
