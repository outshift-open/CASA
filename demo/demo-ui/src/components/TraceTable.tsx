import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { Trace, TraceLlmAppCall } from '../types'

interface TraceTableProps {
    traces: Trace[]
}

const formatMaybeJson = (value?: string | null) => {
    if (!value) {
        return ''
    }

    const trimmed = value.trim()
    if (!trimmed) {
        return ''
    }

    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        try {
            const parsed = JSON.parse(trimmed)
            return JSON.stringify(parsed, null, 2)
        } catch (error) {
            return value
        }
    }

    return value
}

const CopyButton = ({ text }: { text: string }) => {
    const [copied, setCopied] = useState(false)

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(text)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch (error) {
            console.error('Failed to copy:', error)
        }
    }

    return (
        <button
            type="button"
            className="copy-button"
            onClick={handleCopy}
            aria-label="Copy to clipboard"
            title="Copy to clipboard"
        >
            {copied ? 'Copied!' : 'Copy'}
        </button>
    )
}

const InfoPanel = ({ title, items, onClose }: { title: string; items: Array<{ label: string; value: ReactNode; copyText?: string }>; onClose: () => void }) => (
    <div className="info-panel-overlay" role="dialog" aria-label={title}>
        <div className="info-panel-header">
            {title}
            <button type="button" className="info-close-button" onClick={onClose} aria-label="Close">
                ✕
            </button>
        </div>
        <div className="info-panel-content">
            {items.map((item) => (
                <div key={item.label} className="info-row">
                    <div className="info-row-header">
                        <span className="info-label">{item.label}</span>
                        {item.copyText && <CopyButton text={item.copyText} />}
                    </div>
                    <span className="info-value">{item.value}</span>
                </div>
            ))}
        </div>
    </div>
)

const Accordion = ({ label, children }: { label: string; children: ReactNode }) => (
    <details className="accordion">
        <summary>{label}</summary>
        <pre className="code-block tight">{children}</pre>
    </details>
)

const hasResponse = (
    item: TraceLlmAppCall,
): item is TraceLlmAppCall & { llm_app_response: NonNullable<TraceLlmAppCall['llm_app_response']> } => Boolean(
    item.llm_app_response,
)

export const TraceTable = ({ traces }: TraceTableProps) => {
    const [openPanels, setOpenPanels] = useState<Set<string>>(new Set())

    const togglePanel = (key: string) => {
        setOpenPanels((current) => {
            const next = new Set(current)
            if (next.has(key)) {
                next.delete(key)
            } else {
                next.add(key)
            }
            return next
        })
    }

    const isOpen = (key: string) => openPanels.has(key)

    const emptyState = useMemo(
        () => <p className="empty-state">No traces yet. Trigger an interaction to populate this view.</p>,
        [],
    )

    if (traces.length === 0) {
        return emptyState
    }

    return (
        <div className="trace-table-wrapper compact">
            <table className="trace-table" role="grid">
                <thead>
                    <tr>
                        <th scope="col">Client</th>
                        <th scope="col">Agent to LLM calls</th>
                        <th scope="col">LLM to Agent responses</th>
                        <th scope="col">Agent to MCP Server calls</th>
                    </tr>
                </thead>
                <tbody>
                    {traces.map((trace) => {
                        const sourceKey = `source-${trace.source_app_call.id}`

                        return (
                            <tr key={trace.source_app_call.id}>
                                <td>
                                    <div className="cell-container">
                                        <div className="cell-header">
                                            <span className="cell-title">Input</span>
                                            <button
                                                type="button"
                                                className="info-button-icon"
                                                onClick={() => togglePanel(sourceKey)}
                                                aria-label="Show source details"
                                            >
                                                ℹ
                                            </button>
                                        </div>
                                        <div className="cell tight">
                                            <p>{trace.source_app_call.input}</p>
                                            {trace.source_app_response ? (
                                                <p className="muted tiny">Response: {trace.source_app_response.output}</p>
                                            ) : (
                                                <p className="muted tiny">Response: —</p>
                                            )}
                                        </div>
                                        {isOpen(sourceKey) && (
                                            <InfoPanel
                                                title="Source details"
                                                onClose={() => togglePanel(sourceKey)}
                                                items={[
                                                    { label: 'Call ID', value: <span className="mono">{trace.source_app_call.id}</span> },
                                                    {
                                                        label: 'Created',
                                                        value: new Date(trace.source_app_call.created_at).toLocaleString(),
                                                    },
                                                    {
                                                        label: 'Token',
                                                        value: trace.source_app_call.token ? (
                                                            <span className="mono">{trace.source_app_call.token}</span>
                                                        ) : (
                                                            <span className="muted">—</span>
                                                        ),
                                                        copyText: trace.source_app_call.token || undefined,
                                                    },
                                                    {
                                                        label: 'Input',
                                                        value: trace.source_app_call.input ? (
                                                            <span className="mono">{trace.source_app_call.input}</span>
                                                        ) : (
                                                            <span className="muted">—</span>
                                                        ),
                                                    },
                                                    {
                                                        label: 'Response',
                                                        value: trace.source_app_response ? (
                                                            <span className="mono">{trace.source_app_response.output}</span>
                                                        ) : (
                                                            <span className="muted">—</span>
                                                        ),
                                                    },
                                                ]}
                                            />
                                        )}
                                    </div>
                                </td>
                                <td>
                                    {trace.llm_app_calls.length === 0 ? null : (
                                        <ul className="inline-list">
                                            {trace.llm_app_calls.filter(c => c.llm_app_call).map((entry, index) => {
                                                const call = entry.llm_app_call!
                                                const key = `llm-call-${call.id}`

                                                return (
                                                    <li key={call.id}>
                                                        <div className="cell-container">
                                                            <div className="cell-header">
                                                                <span className="cell-title">Call #{index + 1}</span>
                                                                <button
                                                                    type="button"
                                                                    className="info-button-icon"
                                                                    onClick={() => togglePanel(key)}
                                                                    aria-label="Show LLM call details"
                                                                >
                                                                    ℹ
                                                                </button>
                                                            </div>
                                                            <div className="cell tight">
                                                                {call.messages && (
                                                                    <Accordion label="Messages">
                                                                        {formatMaybeJson(call.messages)}
                                                                    </Accordion>
                                                                )}
                                                                {call.tools && (
                                                                    <Accordion label="Tools">
                                                                        {formatMaybeJson(call.tools)}
                                                                    </Accordion>
                                                                )}
                                                            </div>
                                                            {isOpen(key) && (
                                                                <InfoPanel
                                                                    title="LLM call details"
                                                                    onClose={() => togglePanel(key)}
                                                                    items={[
                                                                        { label: 'Call ID', value: <span className="mono">{call.proxy_call_id}</span> },
                                                                        {
                                                                            label: 'Created',
                                                                            value: new Date(call.created_at).toLocaleString(),
                                                                        },
                                                                        {
                                                                            label: 'Token',
                                                                            value: call.token ? (
                                                                                <span className="mono">{call.token}</span>
                                                                            ) : (
                                                                                <span className="muted">—</span>
                                                                            ),
                                                                            copyText: call.token || undefined,
                                                                        },
                                                                        {
                                                                            label: 'Proxy ID',
                                                                            value: call.proxy_call_id ? (
                                                                                <span className="mono">{call.proxy_call_id}</span>
                                                                            ) : (
                                                                                <span className="muted">—</span>
                                                                            ),
                                                                        },
                                                                    ]}
                                                                />
                                                            )}
                                                        </div>
                                                    </li>
                                                )
                                            })}
                                        </ul>
                                    )}
                                </td>
                                <td>
                                    {(() => {
                                        const responses = trace.llm_app_calls.filter(hasResponse)

                                        if (responses.length === 0) {
                                            return null
                                        }

                                        return (
                                            <ul className="inline-list">
                                                {responses.map(({ llm_app_response: response }) => {
                                                    const key = `llm-response-${response.id}`

                                                    return (
                                                        <li key={response.id}>
                                                            <div className="cell-container">
                                                                <div className="cell-header">
                                                                    <span className="cell-title">Response</span>
                                                                    <button
                                                                        type="button"
                                                                        className="info-button-icon"
                                                                        onClick={() => togglePanel(key)}
                                                                        aria-label="Show LLM response details"
                                                                    >
                                                                        ℹ
                                                                    </button>
                                                                </div>
                                                                <div className="cell tight">
                                                                    {response.message && (
                                                                        <Accordion label="Message">
                                                                            {formatMaybeJson(response.message)}
                                                                        </Accordion>
                                                                    )}
                                                                    {response.tool_calls && (
                                                                        <Accordion label="Tool calls">
                                                                            {formatMaybeJson(response.tool_calls)}
                                                                        </Accordion>
                                                                    )}
                                                                </div>
                                                                {isOpen(key) && (
                                                                    <InfoPanel
                                                                        title="LLM response details"
                                                                        onClose={() => togglePanel(key)}
                                                                        items={[
                                                                            { label: 'Response ID', value: <span className="mono">{response.id}</span> },
                                                                            { label: 'Call ID', value: <span className="mono">{response.proxy_call_id}</span> },
                                                                            {
                                                                                label: 'Created',
                                                                                value: new Date(response.created_at).toLocaleString(),
                                                                            },
                                                                            {
                                                                                label: 'Token',
                                                                                value: response.token ? (
                                                                                    <span className="mono">{response.token}</span>
                                                                                ) : (
                                                                                    <span className="muted">—</span>
                                                                                ),
                                                                                copyText: response.token || undefined,
                                                                            },
                                                                        ]}
                                                                    />
                                                                )}
                                                            </div>
                                                        </li>
                                                    )
                                                })}
                                            </ul>
                                        )
                                    })()}
                                </td>
                                <td>
                                    {trace.mcp_app_tool_calls.length === 0 ? null : (
                                        <ul className="inline-list">
                                            {trace.mcp_app_tool_calls.map((entry) => {
                                                const call = entry.tool_call
                                                const blockedDescription = entry.blocked_by_description?.trim()
                                                const blockedType = entry.blocked_by_type?.trim()
                                                const key = `mcp-${call.id}`
                                                const isAiBlocked = call.blocked && blockedType === 'AI-POWERED'
                                                const cellClass = `cell-container ${call.blocked ? (isAiBlocked ? 'blocked' : 'blocked') : 'allowed'}`

                                                return (
                                                    <li key={call.id}>
                                                        <div className={cellClass}>
                                                            <div className="cell-header">
                                                                <div className="cell-header-actions">
                                                                    {call.blocked ? (
                                                                        <span className="status-badge blocked">
                                                                            Blocked{blockedType ? ` - ${blockedType}` : ''}
                                                                        </span>
                                                                    ) : (
                                                                        <span className="status-badge allowed">
                                                                            Passed
                                                                        </span>
                                                                    )}
                                                                </div>
                                                                <button
                                                                    type="button"
                                                                    className="info-button-icon"
                                                                    onClick={() => togglePanel(key)}
                                                                    aria-label="Show MCP tool details"
                                                                >
                                                                    ℹ
                                                                </button>
                                                            </div>
                                                            <div className="cell tight">
                                                                <div className="cell-row compact">
                                                                    <span><strong>Tool:</strong> {call.tool}</span>
                                                                </div>
                                                                {call.blocked && (blockedDescription || call.blocked_by_type_id) &&
                                                                    <div className="cell-row compact">
                                                                        <span style={{ color: '#d14b4bff', fontWeight: "bold", fontSize: '0.85em', lineHeight: '1.3' }}>{blockedDescription ?? call.blocked_by_type_id}</span>
                                                                    </div>
                                                                }
                                                            </div>
                                                            {isOpen(key) && (
                                                                <InfoPanel
                                                                    title="MCP tool details"
                                                                    onClose={() => togglePanel(key)}
                                                                    items={[
                                                                        { label: 'Tool call ID', value: <span className="mono">{call.id}</span> },
                                                                        {
                                                                            label: 'Created',
                                                                            value: new Date(call.created_at).toLocaleString(),
                                                                        },
                                                                        {
                                                                            label: 'Blocked',
                                                                            value: call.blocked ? 'Yes' : 'No',
                                                                        },
                                                                        {
                                                                            label: 'Blocked by',
                                                                            value: blockedDescription ? (
                                                                                <span>{blockedDescription}</span>
                                                                            ) : call.blocked_by_type_id ? (
                                                                                <span className="mono">{call.blocked_by_type_id}</span>
                                                                            ) : (
                                                                                <span className="muted">—</span>
                                                                            ),
                                                                        },
                                                                        {
                                                                            label: 'Token',
                                                                            value: call.token ? (
                                                                                <span className="mono">{call.token}</span>
                                                                            ) : (
                                                                                <span className="muted">—</span>
                                                                            ),
                                                                            copyText: call.token || undefined,
                                                                        },
                                                                    ]}
                                                                />
                                                            )}
                                                        </div>
                                                    </li>
                                                )
                                            })}
                                        </ul>
                                    )}
                                </td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        </div>
    )
}
