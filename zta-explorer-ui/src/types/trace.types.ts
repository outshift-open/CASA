export type EventType =
    | 'TokenIssuedEvent'
    | 'TokenExchangedEvent'
    | 'LLMCallStartedEvent'
    | 'LLMCallEndedEvent'
    | 'MCPCallStartedEvent';

export type BlockingReason =
    | 'no_llm_calls_made_by_app'
    | 'tool_not_selected_by_llm'
    | 'tool_intent_mismatch'
    | 'tool_parameters_mismatch'
    | 'modified_mcp_tool_defs'
    | 'insufficient_scope';

export interface TraceEvent {
    id: string;
    user_input_id: string;
    created_at: string;
    mas_id?: string;
    app_id?: string;
    // TokenIssuedEvent
    token?: string;
    prompt?: string;
    // TokenExchangedEvent
    subject_token?: string;
    act_token?: string;
    subject_app_id?: string;
    act_app_id?: string;
    tools?: string[] | string | null;
    // LLMCallStartedEvent / LLMCallEndedEvent
    call_id?: string;
    response?: string;
    // MCPCallStartedEvent
    caller_app_id?: string;
    callee_app_id?: string;
    tool?: string;
    blocked?: boolean;
    blocking_type?: string;
    blocking_reason?: BlockingReason;
}

export interface Trace {
    id: string;
    user_input_id: string;
    created_at: string;
    event_type: EventType;
    event: TraceEvent;
}

export interface TraceList {
    items: Record<string, Trace[]>;
    total: number;
    page: number;
    page_size: number;
}
