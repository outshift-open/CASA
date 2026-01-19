export interface SourceAppCall {
    id: string
    token: string | null
    input: string
    created_at: string
}

export interface SourceAppResponse {
    id: string
    source_app_call_id: string
    token: string
    output: string
    created_at: string
}

export interface LlmAppCall {
    id: string
    source_app_call_id: string
    token: string | null
    proxy_call_id: string
    messages: string
    tools: string
    created_at: string
}

export interface LlmAppResponse {
    id: string
    llm_app_call_id: string
    token: string | null
    proxy_call_id: string
    message: string
    tool_calls: string
    created_at: string
}

export interface TraceLlmAppCall {
    llm_app_call?: LlmAppCall | null
    llm_app_response?: LlmAppResponse | null
}

export interface McpAppToolCall {
    id: string
    source_app_call_id: string
    llm_app_call_id: string | null
    llm_app_response_id: string | null
    token: string | null
    tool: string
    blocked: boolean
    blocked_by_type_id: string | null
    created_at: string
}

export interface TraceMcpAppToolCall {
    tool_call: McpAppToolCall
    blocked_by_description?: string | null
    blocked_by_type?: string | null
}

export interface Trace {
    source_app_call: SourceAppCall
    source_app_response: SourceAppResponse | null
    llm_app_calls: TraceLlmAppCall[]
    mcp_app_tool_calls: TraceMcpAppToolCall[]
}

export function NewEmptyTrace() {
    return {} as Trace
}

// Type definitions related to the new API

export enum MCPToolBlockingReason {
    NO_LLM_CALLS_MADE_BY_APP = "no_llm_calls_made_by_app",
    TOOL_NOT_SELECTED_BY_LLM = "tool_not_selected_by_llm",
    TOOL_INTENT_MISMATCH = "tool_intent_mismatch",
    TOOL_PARAMETERS_MISMATCH = "tool_parameters_mismatch",
    MODIFIED_MCP_TOOL_DEFS = "modified_mcp_tool_defs"
}

export const MCP_TOOL_BLOCKING_DESCRIPTION: Record<string, string> = {
    [MCPToolBlockingReason.MODIFIED_MCP_TOOL_DEFS]: "The LLM received modified MCP Server Tool Definitions",
    [MCPToolBlockingReason.TOOL_NOT_SELECTED_BY_LLM]: "Requested MCP Server Tool was not selected by the LLM",
    [MCPToolBlockingReason.TOOL_PARAMETERS_MISMATCH]: "Requested MCP Server Tool Parameters are different from those selected by the LLM",
    [MCPToolBlockingReason.TOOL_INTENT_MISMATCH]: "MCP Server Tool choice doesn't match the intention of original input",
}

export enum MCPToolBlockingType {
    DETERMINISTIC = "DETERMINISTIC",
    AI_POWERED = "AI_POWERED"
}

export interface BaseEvent {
    id: string;
    user_input_id: string;
    created_at: string;
}

export interface TokenIssuedEvent extends BaseEvent {
    token: string;
    app_id: string;
    prompt: string;
}

export interface TokenExchangedEvent extends BaseEvent {
    subject_token: string;
    act_token: string;
    subject_app_id: string;
    act_app_id: string;
    tools?: string[];
}

export interface LLMCallStartedEvent extends BaseEvent {
    call_id: string;
    token: string;
    app_id: string;
    prompt: string;
    tools?: string;
}

export interface LLMCallEndedEvent extends BaseEvent {
    call_id: string;
    token: string;
    app_id: string;
    response: string;
    tools?: string;
}

export interface MCPCallStartedEvent extends BaseEvent {
    token: string;
    caller_app_id: string;
    callee_app_id: string;
    tool: string;
    blocked: boolean;
    blocking_type?: MCPToolBlockingType | null;
    blocking_reason?: MCPToolBlockingReason | null;
}

export interface NewTrace {
    id: string
    user_input_id: string
    created_at: string
    event_type: string
    event: any
}

export interface TraceListResponse {
    items: Trace[]
    total: number
    page: number
    page_size: number
}

export interface NewTraceListResponse {
    items: Record<string, NewTrace[]>
    total: number
    page: number
    page_size: number
}
