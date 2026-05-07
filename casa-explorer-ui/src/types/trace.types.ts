/**
 * Copyright 2026 Copyright 2026 Cisco Systems, Inc. and its affiliates
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export const EventType = {
    TokenIssued: 'TokenIssuedEvent',
    TokenExchanged: 'TokenExchangedEvent',
    LLMCallStarted: 'LLMCallStartedEvent',
    LLMCallEnded: 'LLMCallEndedEvent',
    MCPCallStarted: 'MCPCallStartedEvent'
} as const;

export type EventType = (typeof EventType)[keyof typeof EventType];

export const BlockingType = {
    Deterministic: 'DETERMINISTIC',
    AIPowered: 'AI_POWERED'
} as const;

export type BlockingType = (typeof BlockingType)[keyof typeof BlockingType];

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
    blocking_type?: BlockingType;
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
