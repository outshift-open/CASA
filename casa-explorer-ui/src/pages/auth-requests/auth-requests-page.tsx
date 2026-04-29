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

import {useMemo, useState} from 'react';
import {useNavigate, useSearchParams} from 'react-router-dom';
import {useTraces} from '@/hooks/use-traces';
import {useMAS, useMASApps} from '@/hooks/use-mas';
import {useApps} from '@/hooks/use-apps';
import {DataTable} from '@/components/ui/data-table';
import {Badge} from '@/components/ui/badge';
import {DateHover} from '@/components/ui/date-hover';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {Skeleton} from '@/components/ui/skeleton';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Alert, AlertTitle} from '@/components/ui/alert';
import {Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle} from '@/components/ui/sheet';
import {
    CheckCircle2,
    XCircle,
    RefreshCw,
    Network,
    Shield,
    Search,
    X,
    Cpu,
    Sparkles,
    ExternalLink,
    Activity,
    ChevronDown,
    ChevronRight,
    Zap,
    ArrowRightLeft,
    Brain,
    BrainCircuit,
    Download
} from 'lucide-react';
import type {ColumnDef} from '@tanstack/react-table';
import {ArrowUpDown} from 'lucide-react';
import type {BlockingReason, Trace} from '@/types/trace.types';
import type {AppType} from '@/types/app.types';
import {toast} from 'sonner';

// ─── Shared trace rendering (mirrors mas-traces-tab.tsx) ────────────────────

const BLOCKING_REASON_LABELS: Record<BlockingReason, string> = {
    no_llm_calls_made_by_app: 'No LLM calls made',
    tool_not_selected_by_llm: 'Not selected by LLM',
    tool_intent_mismatch: 'Intent mismatch',
    tool_parameters_mismatch: 'Params mismatch',
    modified_mcp_tool_defs: 'Modified tool defs',
    insufficient_scope: 'Insufficient scope'
};

const BLOCKING_REASON_DESCRIPTIONS: Partial<Record<BlockingReason, string>> = {
    no_llm_calls_made_by_app: 'The app made no LLM calls before requesting tool access',
    tool_not_selected_by_llm: 'Requested MCP Server Tool was not selected by the LLM',
    tool_intent_mismatch: "MCP Server Tool choice doesn't match the intention of original input",
    tool_parameters_mismatch: 'Requested MCP Server Tool Parameters are different from those selected by the LLM',
    modified_mcp_tool_defs: 'The LLM received modified MCP Server Tool Definitions',
    insufficient_scope: 'Token does not have the required scope for this tool'
};

const APP_TYPE_LABELS_TRACE: Record<AppType, string> = {
    client: 'Client',
    agent: 'Agent',
    mcp_server: 'MCP'
};

const APP_TYPE_CLASSES: Record<AppType, string> = {
    client: 'bg-blue-500/10 text-blue-400',
    agent: 'bg-purple-500/10 text-purple-400',
    mcp_server: 'bg-orange-500/10 text-orange-400'
};

type AppInfo = {name: string; type: AppType};
type AppNames = Record<string, AppInfo>;

function downloadJson(data: unknown, filename: string) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function parseToolsList(raw: string[] | string | null | undefined): string[] {
    if (!raw) return [];
    if (Array.isArray(raw)) return raw;
    try {
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [raw];
    } catch {
        return [raw];
    }
}

function shortId(id: string | undefined): string {
    if (!id) return '—';
    return id.length > 8 ? `${id.slice(0, 8)}…` : id;
}

function ToolChips({tools}: {tools: string[]}) {
    if (tools.length === 0) return null;
    return (
        <>
            {tools.map((t) => (
                <code key={t} className="mx-0.5 px-1 py-0.5 rounded bg-muted text-[10px] font-mono">
                    {t}
                </code>
            ))}
        </>
    );
}

function AppIdChip({id, appNames}: {id: string | undefined; appNames: AppNames}) {
    if (!id) return <span className="text-muted-foreground">—</span>;
    const info = appNames[id];
    return (
        <span className="inline-flex items-center gap-1">
            {info?.type && (
                <span
                    className={`px-1 py-0.5 rounded text-[9px] font-medium uppercase tracking-wide ${APP_TYPE_CLASSES[info.type]}`}
                >
                    {APP_TYPE_LABELS_TRACE[info.type]}
                </span>
            )}
            <code className="px-1 py-0.5 rounded bg-muted text-[10px] font-mono" title={id}>
                {info?.name ?? shortId(id)}
            </code>
        </span>
    );
}

function EventTimestamp({createdAt}: {createdAt: string}) {
    if (!createdAt) return null;
    const time = new Date(createdAt).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    return <span className="ml-auto pl-3 text-[11px] text-muted-foreground/60 flex-shrink-0 tabular-nums">{time}</span>;
}

const ALWAYS_HIDDEN = new Set(['id', 'user_input_id', 'mas_id', 'created_at']);
const JWT_FIELDS = new Set(['token', 'subject_token', 'act_token']);
const FIELD_LABELS: Record<string, string> = {prompt: 'task'};

function decodeJwtPayload(jwt: string): Record<string, unknown> | null {
    try {
        const parts = jwt.split('.');
        if (parts.length !== 3) return null;
        const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(payload));
    } catch {
        return null;
    }
}

function formatValue(key: string, val: unknown): string {
    if (JWT_FIELDS.has(key) && typeof val === 'string') {
        const decoded = decodeJwtPayload(val);
        return decoded ? JSON.stringify(decoded, null, 2) : val;
    }
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'object') return JSON.stringify(val, null, 2);
    return String(val);
}

function EventAttributes({event, eventType: _eventType}: {event: Trace['event']; eventType: string}) {
    const entries = Object.entries(event).filter(
        ([key, val]) => !ALWAYS_HIDDEN.has(key) && val !== null && val !== undefined
    );
    if (entries.length === 0) return null;
    return (
        <div className="ml-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
            {entries.map(([key, val]) => {
                const isJwt = JWT_FIELDS.has(key) && typeof val === 'string';
                const display = formatValue(key, val);
                return (
                    <>
                        <span
                            key={`k-${key}`}
                            className="text-[10px] text-muted-foreground/70 font-mono pt-0.5 whitespace-nowrap"
                        >
                            {FIELD_LABELS[key] ?? key}
                        </span>
                        {isJwt ? (
                            <pre
                                key={`v-${key}`}
                                className="text-[10px] font-mono text-foreground/80 whitespace-pre-wrap break-all leading-relaxed"
                            >
                                {display}
                            </pre>
                        ) : (
                            <span key={`v-${key}`} className="text-[10px] font-mono text-foreground/80 break-all">
                                {display}
                            </span>
                        )}
                    </>
                );
            })}
        </div>
    );
}

function EventRow({trace, index, appNames}: {trace: Trace; index?: number; appNames: AppNames}) {
    const {event_type, event, created_at} = trace;
    const [expanded, setExpanded] = useState(false);

    let borderClass = 'border-muted';
    let expandedBgClass = 'bg-muted/10';
    let rowBgClass = '';
    let icon: React.ReactNode = null;
    let summary: React.ReactNode = null;

    if (event_type === 'TokenIssuedEvent') {
        icon = <Zap className="h-3.5 w-3.5 text-muted-foreground mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[13px] text-muted-foreground flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-foreground">Token issued</span>
                {event.app_id && (
                    <>
                        <span>by</span>
                        <AppIdChip id={event.app_id} appNames={appNames} />
                    </>
                )}
                {event.prompt && (
                    <>
                        <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide ml-1">
                            Task:
                        </span>
                        <span className="text-foreground/70">"{event.prompt}"</span>
                    </>
                )}
            </div>
        );
    } else if (event_type === 'TokenExchangedEvent') {
        const tools = parseToolsList(event.tools);
        icon = <ArrowRightLeft className="h-3.5 w-3.5 text-muted-foreground mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[13px] text-muted-foreground flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-foreground">Token exchanged</span>
                {event.subject_app_id && (
                    <>
                        <span>by</span>
                        <AppIdChip id={event.subject_app_id} appNames={appNames} />
                    </>
                )}
                {event.act_app_id && (
                    <>
                        <span>→ for</span>
                        <AppIdChip id={event.act_app_id} appNames={appNames} />
                    </>
                )}
                {tools.length > 0 && (
                    <>
                        <span className="ml-1">— requested:</span>
                        <ToolChips tools={tools} />
                    </>
                )}
            </div>
        );
    } else if (event_type === 'LLMCallStartedEvent') {
        const tools = parseToolsList(event.tools);
        borderClass = 'border-blue-500/30';
        expandedBgClass = 'bg-blue-500/5';
        rowBgClass = 'bg-blue-500/5';
        icon = <Brain className="h-3.5 w-3.5 text-blue-400 mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[13px] text-muted-foreground flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-foreground">
                    LLM call {index !== undefined ? `#${index + 1}` : ''}
                </span>
                {event.app_id && (
                    <>
                        <span>from</span>
                        <AppIdChip id={event.app_id} appNames={appNames} />
                    </>
                )}
                {tools.length > 0 && (
                    <>
                        <span className="ml-1">— offered:</span>
                        <ToolChips tools={tools} />
                    </>
                )}
            </div>
        );
    } else if (event_type === 'LLMCallEndedEvent') {
        const selectedTools = parseToolsList(event.tools);
        borderClass = 'border-blue-500/30';
        expandedBgClass = 'bg-blue-500/5';
        rowBgClass = 'bg-blue-500/5';
        icon = <BrainCircuit className="h-3.5 w-3.5 text-blue-400 mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[13px] text-muted-foreground flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-foreground">LLM responded</span>
                {selectedTools.length > 0 ? (
                    <>
                        <span className="ml-1">— selected:</span>
                        <ToolChips tools={selectedTools} />
                    </>
                ) : (
                    <span className="ml-1 italic">— no tools selected</span>
                )}
            </div>
        );
    } else if (event_type === 'MCPCallStartedEvent') {
        const blocked = event.blocked;
        const reason = event.blocking_reason ? BLOCKING_REASON_LABELS[event.blocking_reason] : null;
        const reasonDescription = event.blocking_reason ? BLOCKING_REASON_DESCRIPTIONS[event.blocking_reason] : null;
        borderClass = blocked ? 'border-destructive/40' : 'border-green-500/40';
        expandedBgClass = blocked ? 'bg-destructive/5' : 'bg-green-500/5';
        rowBgClass = blocked ? 'bg-destructive/5' : 'bg-green-500/5';
        icon = blocked ? (
            <XCircle className="h-3.5 w-3.5 text-destructive mt-0.5 flex-shrink-0" />
        ) : (
            <CheckCircle2 className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
        );
        summary = (
            <div className="text-[13px] flex flex-wrap items-center gap-x-2 gap-y-1 flex-1 min-w-0">
                <code className="px-1.5 py-0.5 rounded bg-muted font-mono text-[11px]">{event.tool ?? '—'}</code>
                {(event.caller_app_id || event.callee_app_id) && (
                    <span className="text-muted-foreground flex items-center gap-1">
                        <AppIdChip id={event.caller_app_id} appNames={appNames} />
                        <span>→</span>
                        <AppIdChip id={event.callee_app_id} appNames={appNames} />
                    </span>
                )}
                {blocked ? (
                    <>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Badge variant="destructive" className="text-[10px] h-4 px-1.5 cursor-default">
                                    Denied{reason ? ` · ${reason}` : ''}
                                </Badge>
                            </TooltipTrigger>
                            {reasonDescription && (
                                <TooltipContent>
                                    <p className="text-center">{reasonDescription}</p>
                                </TooltipContent>
                            )}
                        </Tooltip>
                        {event.blocking_type && (
                            <Badge
                                variant="outline"
                                className={`text-[9px] h-4 px-1.5 font-medium gap-0.5 ${event.blocking_type === 'AI_POWERED' ? 'border-sky-500/50 text-sky-400' : 'border-orange-500/50 text-orange-400'}`}
                            >
                                {event.blocking_type === 'AI_POWERED' ? (
                                    <Sparkles className="h-2.5 w-2.5" />
                                ) : (
                                    <Cpu className="h-2.5 w-2.5" />
                                )}
                                {event.blocking_type === 'AI_POWERED' ? 'Semantic' : 'Deterministic'}
                            </Badge>
                        )}
                    </>
                ) : (
                    <Badge variant="outline" className="text-[10px] h-4 px-1.5 border-green-500/50 text-green-500">
                        Allowed
                    </Badge>
                )}
            </div>
        );
    }

    if (!icon) return null;

    return (
        <div className={`border-l-2 ml-2 ${borderClass}`}>
            <button
                type="button"
                className={`w-full flex items-start gap-2 py-1.5 pl-4 hover:bg-muted/30 transition-colors text-left cursor-pointer ${rowBgClass}`}
                onClick={() => setExpanded((v) => !v)}
            >
                {expanded ? (
                    <ChevronDown className="h-3 w-3 text-muted-foreground/50 mt-1 flex-shrink-0" />
                ) : (
                    <ChevronRight className="h-3 w-3 text-muted-foreground/50 mt-1 flex-shrink-0" />
                )}
                {icon}
                {summary}
                <EventTimestamp createdAt={created_at} />
            </button>
            {expanded && (
                <div className={`pl-4 pb-2 ${expandedBgClass}`}>
                    <EventAttributes event={event} eventType={event_type} />
                    <button
                        type="button"
                        onClick={(e) => {
                            e.stopPropagation();
                            downloadJson(trace, `event-${trace.id.slice(0, 8)}.json`);
                            toast.success('Event downloaded');
                        }}
                        className="mt-2 ml-6 flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                    >
                        <Download className="h-3 w-3" />
                        Download event
                    </button>
                </div>
            )}
        </div>
    );
}

// ─── Session trace sheet ─────────────────────────────────────────────────────

interface SessionTraceSheetProps {
    userInputId: string | null;
    masId: string | null;
    masName: string | null;
    tracesData: Record<string, Trace[]> | null;
    onClose: () => void;
}

function SessionTraceSheet({userInputId, masId, masName, tracesData, onClose}: SessionTraceSheetProps) {
    const navigate = useNavigate();
    const {data: appsData} = useMASApps(masId ?? '');

    const appNames: AppNames = useMemo(() => {
        if (!appsData) return {};
        return Object.fromEntries(
            appsData.filter((a) => a.id && a.name).map((a) => [a.id!, {name: a.name, type: a.type}])
        );
    }, [appsData]);

    const session = useMemo(() => {
        if (!userInputId || !tracesData) return null;
        const traces = tracesData[userInputId];
        if (!traces || traces.length === 0) return null;
        const sorted = [...traces].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        const tokenIssued = sorted.find((t) => t.event_type === 'TokenIssuedEvent');
        const mcpCalls = sorted.filter((t) => t.event_type === 'MCPCallStartedEvent');
        const llmCallCount = sorted.filter((t) => t.event_type === 'LLMCallStartedEvent').length;
        const tokenCount = sorted.filter(
            (t) => t.event_type === 'TokenIssuedEvent' || t.event_type === 'TokenExchangedEvent'
        ).length;
        const firstTs = sorted[0]?.created_at ? new Date(sorted[0].created_at).getTime() : null;
        const lastTs = sorted[sorted.length - 1]?.created_at
            ? new Date(sorted[sorted.length - 1].created_at).getTime()
            : null;
        const durationMs = firstTs && lastTs ? lastTs - firstTs : null;
        return {
            prompt: tokenIssued?.event.prompt ?? null,
            createdAt: tokenIssued?.created_at ?? sorted[0]?.created_at ?? '',
            events: sorted,
            allowedCount: mcpCalls.filter((t) => !t.event.blocked).length,
            deniedCount: mcpCalls.filter((t) => t.event.blocked).length,
            llmCallCount,
            mcpCallCount: mcpCalls.length,
            tokenCount,
            durationMs
        };
    }, [userInputId, tracesData]);

    const datetime = session?.createdAt
        ? new Date(session.createdAt).toLocaleString([], {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
          })
        : null;

    const durationLabel =
        session?.durationMs != null
            ? session.durationMs < 1000
                ? `${session.durationMs}ms`
                : `${(session.durationMs / 1000).toFixed(1)}s`
            : '—';

    let llmCallIndex = 0;

    return (
        <Sheet open={!!userInputId} onOpenChange={(open) => !open && onClose()}>
            <SheetContent
                side="right"
                className="w-[900px] sm:max-w-[900px] flex flex-col p-0 gap-0"
                showCloseButton={false}
            >
                {/* Top bar */}
                <div className="flex items-center justify-between px-6 py-3 border-b flex-shrink-0">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            Session trace
                        </span>
                        {userInputId && (
                            <code className="text-[10px] text-muted-foreground/60 font-mono">
                                {userInputId.slice(0, 8)}…
                            </code>
                        )}
                    </div>
                    <div className="flex items-center gap-1">
                        {userInputId && (
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7 cursor-pointer"
                                onClick={() => navigate(`/auth-requests/${userInputId}`)}
                                title="Open full page"
                            >
                                <ExternalLink className="h-3.5 w-3.5" />
                            </Button>
                        )}
                        <SheetClose asChild>
                            <Button variant="ghost" size="icon" className="h-7 w-7 cursor-pointer" onClick={onClose}>
                                <X className="h-4 w-4" />
                            </Button>
                        </SheetClose>
                    </div>
                </div>

                {/* Header */}
                <SheetHeader className="px-6 pt-5 pb-4 border-b flex-shrink-0">
                    <SheetTitle className="text-base font-semibold truncate">
                        {session?.prompt ?? <span className="text-muted-foreground italic font-normal">No prompt</span>}
                    </SheetTitle>
                    <SheetDescription>{datetime ?? '—'}</SheetDescription>
                </SheetHeader>

                {/* Stat cards */}
                <div className="grid grid-cols-4 gap-3 px-6 py-4 border-b flex-shrink-0">
                    <div className="rounded-lg border bg-muted/20 p-3 space-y-1">
                        <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">MAS</p>
                        {masId ? (
                            <button
                                type="button"
                                className="flex items-center gap-1 text-sm font-medium hover:underline cursor-pointer text-left truncate w-full"
                                onClick={() => navigate(`/mas/${masId}`)}
                            >
                                <Network className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                                <span className="truncate">{masName ?? masId}</span>
                            </button>
                        ) : (
                            <p className="text-sm text-muted-foreground">—</p>
                        )}
                    </div>
                    <div className="rounded-lg border bg-muted/20 p-3 space-y-1">
                        <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">
                            Activity
                        </p>
                        <p className="text-sm font-medium tabular-nums">
                            {session?.tokenCount ?? 0} token{session?.tokenCount !== 1 ? 's' : ''}
                        </p>
                        <p className="text-[11px] text-muted-foreground tabular-nums">
                            {session?.mcpCallCount ?? 0} MCP · {session?.llmCallCount ?? 0} LLM
                        </p>
                    </div>
                    <div className="rounded-lg border bg-muted/20 p-3 space-y-1">
                        <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">Auth</p>
                        <div className="flex items-center gap-2 text-sm font-medium">
                            {(session?.allowedCount ?? 0) > 0 && (
                                <span className="flex items-center gap-0.5 text-green-500">
                                    <CheckCircle2 className="h-3.5 w-3.5" />
                                    {session?.allowedCount}
                                </span>
                            )}
                            {(session?.deniedCount ?? 0) > 0 && (
                                <span className="flex items-center gap-0.5 text-destructive">
                                    <XCircle className="h-3.5 w-3.5" />
                                    {session?.deniedCount}
                                </span>
                            )}
                            {(session?.allowedCount ?? 0) === 0 && (session?.deniedCount ?? 0) === 0 && (
                                <span className="text-muted-foreground">—</span>
                            )}
                        </div>
                    </div>
                    <div className="rounded-lg border bg-muted/20 p-3 space-y-1">
                        <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">
                            Duration
                        </p>
                        <p className="text-sm font-medium tabular-nums">{durationLabel}</p>
                        <p className="text-[11px] text-muted-foreground">{session?.events.length ?? 0} events</p>
                    </div>
                </div>

                {/* Events list */}
                <div className="flex-1 overflow-y-auto px-6 py-4 space-y-0.5">
                    {!session ? (
                        <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                            <Activity className="h-8 w-8 opacity-40" />
                            <p className="text-sm">No events found for this session</p>
                        </div>
                    ) : (
                        session.events.map((trace) => {
                            const idx = trace.event_type === 'LLMCallStartedEvent' ? llmCallIndex++ : undefined;
                            return <EventRow key={trace.id} trace={trace} index={idx} appNames={appNames} />;
                        })
                    )}
                </div>

                {/* Footer actions */}
                {session && (
                    <div className="px-6 py-3 border-t flex-shrink-0 flex items-center justify-between">
                        <button
                            type="button"
                            onClick={() => {
                                downloadJson(session.events, `session-${userInputId?.slice(0, 8) ?? 'trace'}.json`);
                                toast.success('Session downloaded');
                            }}
                            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                        >
                            <Download className="h-3.5 w-3.5" />
                            Download session
                        </button>
                    </div>
                )}
            </SheetContent>
        </Sheet>
    );
}

// ─── Page ────────────────────────────────────────────────────────────────────

interface AuthRequest {
    id: string;
    userInputId: string;
    tool: string;
    callerAppName: string | null;
    calleeAppName: string | null;
    masId: string | null;
    masName: string | null;
    blocked: boolean;
    blockingType: string | null;
    blockingReason: BlockingReason | null;
    createdAt: string;
}

export function AuthRequestsPage() {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();

    const search = searchParams.get('q') ?? '';
    const authFilter = (searchParams.get('auth') ?? 'all') as 'all' | 'allowed' | 'denied';
    const masFilter = searchParams.get('mas') ?? 'all';
    const denyTypeFilter = (searchParams.get('denyType') ?? 'all') as 'all' | 'DETERMINISTIC' | 'AI_POWERED';
    const fromDashboard = searchParams.get('from') === 'dashboard';

    const setSearch = (v: string) =>
        setSearchParams(
            (p) => {
                const n = new URLSearchParams(p);
                if (v) n.set('q', v);
                else n.delete('q');
                return n;
            },
            {replace: true}
        );
    const setAuthFilter = (v: string) =>
        setSearchParams(
            (p) => {
                const n = new URLSearchParams(p);
                if (v && v !== 'all') n.set('auth', v);
                else n.delete('auth');
                return n;
            },
            {replace: true}
        );
    const setMasFilter = (v: string) =>
        setSearchParams(
            (p) => {
                const n = new URLSearchParams(p);
                if (v && v !== 'all') n.set('mas', v);
                else n.delete('mas');
                return n;
            },
            {replace: true}
        );
    const setDenyTypeFilter = (v: string) =>
        setSearchParams(
            (p) => {
                const n = new URLSearchParams(p);
                if (v && v !== 'all') n.set('denyType', v);
                else n.delete('denyType');
                return n;
            },
            {replace: true}
        );

    const [selectedUserInputId, setSelectedUserInputId] = useState<string | null>(null);
    const [selectedMasId, setSelectedMasId] = useState<string | null>(null);
    const [selectedMasName, setSelectedMasName] = useState<string | null>(null);

    const {data: tracesData, isLoading: tracesLoading, refetch} = useTraces(undefined, 1, 100, true, false);
    const {data: masData} = useMAS();
    const {data: appsData} = useApps();

    const dashboardFilterLabel = useMemo(() => {
        if (!fromDashboard) return null;
        const parts: string[] = [];
        if (authFilter === 'allowed') parts.push('allowed calls');
        if (authFilter === 'denied') parts.push('denied calls');
        if (denyTypeFilter === 'DETERMINISTIC') parts.push('deterministic denials');
        if (denyTypeFilter === 'AI_POWERED') parts.push('semantic denials');
        if (search) parts.push(`"${search}"`);
        return parts.length > 0 ? parts.join(' · ') : 'filtered view';
    }, [fromDashboard, authFilter, denyTypeFilter, search]);

    const clearDashboardFilter = () => setSearchParams(new URLSearchParams(), {replace: true});

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Auth requests refreshed successfully');
        } catch {
            toast.error('Failed to refresh auth requests');
        }
    };

    const masMap = useMemo(() => {
        if (!masData) return {} as Record<string, string>;
        return Object.fromEntries(masData.map((m) => [m.id, m.name]));
    }, [masData]);

    const appNameMap = useMemo(() => {
        if (!appsData?.items) return {} as Record<string, string>;
        return Object.fromEntries(appsData.items.filter((a) => a.id).map((a) => [a.id!, a.name]));
    }, [appsData]);

    const allMcpCalls = useMemo((): AuthRequest[] => {
        if (!tracesData?.items) return [];
        const all: Trace[] = Object.values(tracesData.items).flat();
        return all
            .filter((t) => t.event_type === 'MCPCallStartedEvent')
            .map((t) => ({
                id: t.id,
                userInputId: t.user_input_id,
                tool: t.event.tool ?? '—',
                callerAppName: t.event.caller_app_id
                    ? (appNameMap[t.event.caller_app_id] ?? t.event.caller_app_id)
                    : null,
                calleeAppName: t.event.callee_app_id
                    ? (appNameMap[t.event.callee_app_id] ?? t.event.callee_app_id)
                    : null,
                masId: t.event.mas_id ?? null,
                masName: t.event.mas_id ? (masMap[t.event.mas_id] ?? t.event.mas_id) : null,
                blocked: t.event.blocked ?? false,
                blockingType: t.event.blocking_type ?? null,
                blockingReason: t.event.blocking_reason ?? null,
                createdAt: t.created_at
            }))
            .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    }, [tracesData, masMap, appNameMap]);

    const masList = useMemo(() => {
        const ids = new Set(allMcpCalls.map((r) => r.masId).filter(Boolean) as string[]);
        return Array.from(ids).map((id) => ({id, name: masMap[id] ?? id}));
    }, [allMcpCalls, masMap]);

    const filtered = useMemo(() => {
        let result = allMcpCalls;
        if (authFilter === 'allowed') result = result.filter((r) => !r.blocked);
        if (authFilter === 'denied') result = result.filter((r) => r.blocked);
        if (masFilter !== 'all') result = result.filter((r) => r.masId === masFilter);
        if (denyTypeFilter !== 'all') result = result.filter((r) => r.blockingType === denyTypeFilter);
        if (search) {
            const q = search.toLowerCase();
            result = result.filter(
                (r) =>
                    r.tool.toLowerCase().includes(q) ||
                    (r.masName ?? '').toLowerCase().includes(q) ||
                    (r.blockingReason ?? '').toLowerCase().includes(q) ||
                    r.id.toLowerCase().includes(q)
            );
        }
        return result;
    }, [allMcpCalls, authFilter, masFilter, denyTypeFilter, search]);

    const columns = useMemo<ColumnDef<AuthRequest>[]>(
        () => [
            {
                accessorKey: 'tool',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Tool <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <code className="font-mono text-sm font-medium">{row.getValue('tool')}</code>
                    </div>
                )
            },
            {
                accessorKey: 'callerAppName',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Caller <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <span className="text-sm text-muted-foreground">{row.getValue('callerAppName') ?? '—'}</span>
                    </div>
                )
            },
            {
                accessorKey: 'calleeAppName',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            MCP Server <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <span className="text-sm text-muted-foreground">{row.getValue('calleeAppName') ?? '—'}</span>
                    </div>
                )
            },
            {
                accessorKey: 'masName',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            MAS <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const req = row.original;
                    if (!req.masName)
                        return (
                            <div className="flex justify-center">
                                <span className="text-muted-foreground">—</span>
                            </div>
                        );
                    return (
                        <div className="flex justify-center">
                            <button
                                type="button"
                                className="flex items-center gap-1.5 text-sm hover:underline cursor-pointer"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (req.masId) navigate(`/mas/${req.masId}`);
                                }}
                            >
                                <Network className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                                <span className="truncate max-w-[160px]">{req.masName}</span>
                            </button>
                        </div>
                    );
                }
            },
            {
                accessorKey: 'blocked',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Authorization <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const blocked = row.getValue('blocked') as boolean;
                    return (
                        <div className="flex justify-center">
                            {blocked ? (
                                <Badge variant="destructive" className="gap-1">
                                    <XCircle className="h-3 w-3" /> Denied
                                </Badge>
                            ) : (
                                <Badge variant="outline" className="gap-1 border-green-500/50 text-green-400">
                                    <CheckCircle2 className="h-3 w-3" /> Allowed
                                </Badge>
                            )}
                        </div>
                    );
                }
            },
            {
                accessorKey: 'blockingType',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Deny Type <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const type = row.getValue('blockingType') as string | null;
                    return (
                        <div className="flex justify-center">
                            {!type ? (
                                <span className="text-muted-foreground">—</span>
                            ) : (
                                <Badge
                                    variant="outline"
                                    className={`gap-1 ${type === 'AI_POWERED' ? 'border-sky-500/50 text-sky-500' : 'border-orange-500/50 text-orange-500'}`}
                                >
                                    {type === 'AI_POWERED' ? (
                                        <Sparkles className="h-3 w-3" />
                                    ) : (
                                        <Cpu className="h-3 w-3" />
                                    )}
                                    {type === 'AI_POWERED' ? 'Semantic' : 'Deterministic'}
                                </Badge>
                            )}
                        </div>
                    );
                }
            },
            {
                accessorKey: 'blockingReason',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Deny Reason <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const reason = row.getValue('blockingReason') as BlockingReason | null;
                    if (!reason)
                        return (
                            <div className="flex justify-center">
                                <span className="text-muted-foreground">—</span>
                            </div>
                        );
                    const label = BLOCKING_REASON_LABELS[reason] ?? reason;
                    const desc = BLOCKING_REASON_DESCRIPTIONS[reason];
                    return (
                        <div className="flex justify-center">
                            {desc ? (
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <span className="text-sm cursor-default">{label}</span>
                                    </TooltipTrigger>
                                    <TooltipContent className="max-w-[240px]">
                                        <p>{desc}</p>
                                    </TooltipContent>
                                </Tooltip>
                            ) : (
                                <span className="text-sm">{label}</span>
                            )}
                        </div>
                    );
                }
            },
            {
                accessorKey: 'createdAt',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Created At <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <DateHover date={row.getValue('createdAt')} className="text-sm" />
                    </div>
                )
            }
        ],
        [navigate]
    );

    return (
        <div>
            <div className="flex items-center justify-between pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Auth Requests</h1>
                    <p className="text-muted-foreground">MCP auth requests in traces.</p>
                </div>
            </div>

            {dashboardFilterLabel && (
                <Alert className="mb-4 flex items-center justify-between py-2">
                    <AlertTitle className="mb-0">
                        Showing <span className="font-semibold">{dashboardFilterLabel}</span>{' '}
                        <span className="text-muted-foreground font-normal">(from dashboard)</span>
                    </AlertTitle>
                    <Button
                        variant="secondary"
                        size="sm"
                        className="shrink-0 cursor-pointer"
                        onClick={clearDashboardFilter}
                    >
                        Clear dashboard filter
                    </Button>
                </Alert>
            )}

            <Card>
                <CardHeader className="px-6">
                    <div className="flex items-center justify-between">
                        <div className="space-y-2">
                            <CardTitle>Auth Requests</CardTitle>
                            <CardDescription>
                                {tracesLoading
                                    ? 'Loading...'
                                    : `${allMcpCalls.length} request${allMcpCalls.length !== 1 ? 's' : ''} recorded`}
                            </CardDescription>
                        </div>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="outline"
                                    size="icon"
                                    onClick={handleRefresh}
                                    disabled={tracesLoading}
                                    className="cursor-pointer"
                                    aria-label="Refresh"
                                >
                                    <RefreshCw className={`h-4 w-4 ${tracesLoading ? 'animate-spin' : ''}`} />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Refresh</p>
                            </TooltipContent>
                        </Tooltip>
                    </div>
                    <div className="flex items-center justify-between gap-2 mt-2">
                        <div className="relative w-1/2">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                placeholder="Filter by tool, MAS, trace id, reason..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <Select value={authFilter} onValueChange={(v) => setAuthFilter(v as typeof authFilter)}>
                                <SelectTrigger className="w-[160px]">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All authorizations</SelectItem>
                                    <SelectItem value="allowed">Allowed only</SelectItem>
                                    <SelectItem value="denied">Denied only</SelectItem>
                                </SelectContent>
                            </Select>
                            <Select value={masFilter} onValueChange={setMasFilter}>
                                <SelectTrigger className="w-[160px]">
                                    <SelectValue placeholder="All MAS" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All MAS</SelectItem>
                                    {masList.map((m) => (
                                        <SelectItem key={m.id} value={m.id}>
                                            {m.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <Select
                                value={denyTypeFilter}
                                onValueChange={(v) => setDenyTypeFilter(v as typeof denyTypeFilter)}
                            >
                                <SelectTrigger className="w-[160px]">
                                    <SelectValue placeholder="Any deny type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">Any deny type</SelectItem>
                                    <SelectItem value="DETERMINISTIC">Deterministic</SelectItem>
                                    <SelectItem value="AI_POWERED">Semantic</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {tracesLoading ? (
                        <div className="space-y-2">
                            {Array.from({length: 5}).map((_, i) => (
                                <Skeleton key={i} className="h-12 w-full" />
                            ))}
                        </div>
                    ) : allMcpCalls.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 gap-3">
                            <Shield className="h-10 w-10 text-muted-foreground opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No auth requests yet</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    MCP tool authorization activity will appear here
                                </p>
                            </div>
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={filtered}
                            hideSearch
                            onRowClick={(row) => {
                                setSelectedUserInputId(row.userInputId);
                                setSelectedMasId(row.masId);
                                setSelectedMasName(row.masName);
                            }}
                            getRowClassName={(row) => {
                                if (row.userInputId !== selectedUserInputId) return '';
                                return 'border-l-2 border-b-0 border-[rgba(0,188,235,0.5)]';
                            }}
                        />
                    )}
                </CardContent>
            </Card>

            <SessionTraceSheet
                userInputId={selectedUserInputId}
                masId={selectedMasId}
                masName={selectedMasName}
                tracesData={tracesData?.items ?? null}
                onClose={() => {
                    setSelectedUserInputId(null);
                    setSelectedMasId(null);
                    setSelectedMasName(null);
                }}
            />
        </div>
    );
}
