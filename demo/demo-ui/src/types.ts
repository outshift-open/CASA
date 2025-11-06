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
    llm_app_call: LlmAppCall
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

export interface TraceListResponse {
    items: Trace[]
    total: number
    page: number
    page_size: number
}
