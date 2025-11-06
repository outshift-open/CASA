import type { TraceListResponse } from './types'

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

    return (await response.json()) as TraceListResponse
}
