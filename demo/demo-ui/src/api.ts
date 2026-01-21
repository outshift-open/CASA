import {
    MCP_TOOL_BLOCKING_DESCRIPTION,
    NewEmptyTrace,
    type LLMCallEndedEvent,
    type LLMCallStartedEvent,
    type MCPCallStartedEvent,
    type NewTraceListResponse,
    type TokenIssuedEvent,
    type Trace,
    type TraceListResponse,
    type App,
    type AppListResponse
} from './types'

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'

const normaliseBaseUrl = (url: string) => url.replace(/\/$/, '')

export const API_BASE_URL = normaliseBaseUrl(
    (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() || DEFAULT_API_BASE_URL,
)

export interface FetchTracesOptions {
    page: number
    pageSize: number
    signal?: AbortSignal
}

export const fetchTraces = async ({ page, pageSize, signal }: FetchTracesOptions): Promise<TraceListResponse> => {
    const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
    })

    const response = await fetch(`${API_BASE_URL}/trace?${params.toString()}`, {
        signal,
        headers: {
            Accept: 'application/json',
        },
    })

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`
        try {
            const payload = await response.json()
            if (payload?.detail) {
                detail = payload.detail
            }
        } catch (error) {
            // Swallow JSON parsing errors and fall back to default detail message.
        }
        throw new Error(detail)
    }

    const traceListResponse = (await response.json()) as NewTraceListResponse
    const traces: Trace[] = []

    for (const uiid in traceListResponse.items) {
        const finalTrace = NewEmptyTrace()
        finalTrace.llm_app_calls = []
        finalTrace.mcp_app_tool_calls = []
        for (const trace of traceListResponse.items[uiid]) {
            if (trace.event_type === "TokenIssuedEvent") {
                const evt = trace.event as TokenIssuedEvent
                finalTrace.source_app_call = {
                    id: evt.id,
                    created_at: evt.created_at,
                    input: evt.prompt,
                    token: evt.token,
                }
            } else if (trace.event_type === "LLMCallStartedEvent") {
                const evt = trace.event as LLMCallStartedEvent
                finalTrace.llm_app_calls.push({
                    llm_app_call: {
                        id: evt.id,
                        created_at: evt.created_at,
                        messages: evt.prompt,
                        proxy_call_id: evt.call_id,
                        token: evt.token,
                        tools: evt.tools ?? "",
                        source_app_call_id: "",
                    }
                })
            } else if (trace.event_type === "LLMCallEndedEvent") {
                const evt = trace.event as LLMCallEndedEvent
                finalTrace.llm_app_calls.push({
                    llm_app_response: {
                        id: evt.id,
                        created_at: evt.created_at,
                        proxy_call_id: evt.call_id,
                        llm_app_call_id: "",
                        message: evt.response,
                        token: evt.token,
                        tool_calls: evt.tools ?? "",
                    }
                })
            } else if (trace.event_type === "MCPCallStartedEvent") {
                const evt = trace.event as MCPCallStartedEvent
                finalTrace.mcp_app_tool_calls.push({
                    tool_call: {
                        id: evt.id,
                        token: evt.token,
                        tool: evt.tool,
                        created_at: evt.created_at,
                        blocked: evt.blocked,
                        blocked_by_type_id: "",
                        llm_app_call_id: "",
                        llm_app_response_id: "",
                        source_app_call_id: "",
                    },
                    blocked_by_type: evt.blocking_type,
                    blocked_by_description: evt.blocking_reason ? MCP_TOOL_BLOCKING_DESCRIPTION[evt.blocking_reason] : null,
                })
            }
        }

        if (finalTrace.llm_app_calls.length > 0) {
            const lastCall = finalTrace.llm_app_calls[finalTrace.llm_app_calls.length - 1];
            if (lastCall.llm_app_response) {
                finalTrace.source_app_response = {
                    id: lastCall.llm_app_response.id,
                    created_at: lastCall.llm_app_response.created_at,
                    token: "",
                    output: lastCall.llm_app_response.message,
                    source_app_call_id: "",
                }
            }

        }

        traces.push(finalTrace)
    }

    const result = {
        items: traces,
        page: traceListResponse.page,
        page_size: traceListResponse.page_size,
        total: traceListResponse.total
    } as TraceListResponse

    return result
}

// App API functions
export const fetchApps = async (signal?: AbortSignal): Promise<AppListResponse> => {
    const response = await fetch(`${API_BASE_URL}/apps`, {
        signal,
        headers: {
            Accept: 'application/json',
        },
    })

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`
        try {
            const payload = await response.json()
            if (payload?.detail) {
                detail = payload.detail
            }
        } catch (error) {
            // Swallow JSON parsing errors
        }
        throw new Error(detail)
    }

    const apps = await response.json()
    return {
        items: Array.isArray(apps) ? apps : [],
        total: Array.isArray(apps) ? apps.length : 0
    }
}

export const createApp = async (app: Omit<App, 'id'>): Promise<App> => {
    const response = await fetch(`${API_BASE_URL}/apps`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
        },
        body: JSON.stringify(app),
    })

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`
        try {
            const payload = await response.json()
            if (payload?.detail) {
                detail = payload.detail
            }
        } catch (error) {
            // Swallow JSON parsing errors
        }
        throw new Error(detail)
    }

    return response.json()
}

export const updateApp = async (id: string, app: Omit<App, 'id'>): Promise<App> => {
    const response = await fetch(`${API_BASE_URL}/apps/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
        },
        body: JSON.stringify(app),
    })

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`
        try {
            const payload = await response.json()
            if (payload?.detail) {
                detail = payload.detail
            }
        } catch (error) {
            // Swallow JSON parsing errors
        }
        throw new Error(detail)
    }

    return response.json()
}

export const deleteApp = async (id: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/apps/${id}`, {
        method: 'DELETE',
        headers: {
            Accept: 'application/json',
        },
    })

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`
        try {
            const payload = await response.json()
            if (payload?.detail) {
                detail = payload.detail
            }
        } catch (error) {
            // Swallow JSON parsing errors
        }
        throw new Error(detail)
    }
}

