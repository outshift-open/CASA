---
id: token-flow
sidebar_position: 3
title: Token Flow
---

# Token Flow

CASA uses OAuth2 token exchange (RFC 8693) to create a chain of trust from user intent to tool execution. Every token is scoped to a specific purpose, and each exchange requires the previous token to be valid.

## Token Types

| Token | Scope | Issued when | Used for |
|---|---|---|---|
| **T1 (user input token)** | `user-input` | User submits a prompt | Proves origin and user intent |
| **T2 (LLM token)** | `llm-access` | Agent exchanges T1 | Authorizes LLM calls |
| **T3 (tool token)** | `call-tools` + specific tools | Agent exchanges T1 after LLM selects tools | Authorizes MCP tool calls |

Tokens are short-lived (5-minute TTL) and are single-purpose — a T2 LLM token cannot be used to call MCP tools.

## Full Token Exchange Sequence

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#f0fdf4', 'actorBkg': '#1e293b', 'actorBorder': '#475569', 'actorTextColor': '#f1f5f9', 'noteBkgColor': '#134e4a', 'noteTextColor': '#f1f5f9', 'activationBkgColor': '#1a2e05', 'activationBorderColor': '#84cc16', 'signalColor': '#475569', 'signalTextColor': '#1e293b'}}}%%
sequenceDiagram
    participant User
    participant Client
    participant ClientSidecar as Client Sidecar
    participant CASA as CASA Control Plane
    participant Agent
    participant AgentSidecar as Agent Sidecar
    participant LLM as External LLM
    participant MCPSidecar as MCP Sidecar
    participant MCP as MCP Server

    User->>Client: Submit prompt
    Client->>ClientSidecar: (outbound intercepted)
    ClientSidecar->>CASA: POST /oauth/token (client_credentials)
    CASA-->>ClientSidecar: T1 (user input token, stores prompt)
    ClientSidecar->>Agent: Forward request with T1

    Agent->>AgentSidecar: (outbound intercepted)
    AgentSidecar->>CASA: POST /oauth/token/exchange (T1 → T2, scope=llm-access)
    CASA-->>AgentSidecar: T2 (LLM-scoped token)
    AgentSidecar->>LLM: LLM call with T2
    LLM-->>AgentSidecar: Response (tool selections)
    AgentSidecar->>CASA: Log LLM trace (tools selected by LLM)

    Agent->>AgentSidecar: (outbound to MCP intercepted)
    AgentSidecar->>CASA: POST /oauth/token/exchange (T1 → T3, tool=filesystem:read)
    Note over CASA: Run tool checks:<br/>1. Tool in LLM selection?<br/>2. Intent matches user prompt?
    CASA-->>AgentSidecar: T3 (call-tools token, tools=[filesystem:read])

    AgentSidecar->>MCPSidecar: MCP call with T3
    MCPSidecar->>CASA: POST /oauth/introspect (T3)
    CASA-->>MCPSidecar: Active=true, tools=[filesystem:read]
    MCPSidecar->>MCP: Forward MCP request
    MCP-->>MCPSidecar: Tool result
    MCPSidecar-->>Agent: Return result
```

## What Happens When a Check Fails

If a tool check fails during token exchange (step where Agent requests T3):

1. CASA returns a 403 Forbidden response
2. The sidecar logs the denial with the tool name and check that failed
3. The agent receives a 403 and cannot call the tool
4. The event is recorded in telemetry for audit purposes

The user's prompt and the agent's tool selection are both recorded, so you can see exactly why a denial occurred.

## Token Exchange vs Token Introspection

**Token exchange** (`/oauth/token/exchange`):
- Called by sidecars on egress (when making outbound calls)
- Runs all configured tool checks
- Returns a new, narrower-scoped token

**Token introspection** (`/oauth/introspect`):
- Called by sidecars on ingress (when receiving inbound calls)
- Validates the presented token and returns its claims
- No tool checks — validation only

## Sidecar Transparency

Applications are not aware of token operations. The sidecar handles everything:

- On egress: intercepts the request, performs the token exchange, injects the token, forwards
- On ingress: intercepts the request, introspects the token, allows or denies

Your application code never sees tokens, never calls the control plane, and never needs to handle auth errors from CASA.
