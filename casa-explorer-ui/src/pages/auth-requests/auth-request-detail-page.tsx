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
import {useParams, useNavigate, Link} from 'react-router-dom';
import {useTraces} from '@/hooks/use-traces';
import {useMASApps, useMASById} from '@/hooks/use-mas';
import {Skeleton} from '@/components/ui/skeleton';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {
    ArrowLeft,
    Network,
    CheckCircle2,
    XCircle,
    Activity,
    Download,
    ChevronDown,
    ChevronRight,
    Zap,
    ArrowRightLeft,
    Brain,
    BrainCircuit,
    Cpu,
    Sparkles,
    ShieldAlert,
    Info
} from 'lucide-react';
import {toast} from 'sonner';
import type {Trace} from '@/types/trace.types';
import type {AppType} from '@/types/app.types';

// ─── Shared rendering primitives ─────────────────────────────────────────────

const BLOCKING_REASON_LABELS: Record<string, string> = {
    no_llm_calls_made_by_app: 'No LLM calls made',
    tool_not_selected_by_llm: 'Not selected by LLM',
    tool_intent_mismatch: 'Intent mismatch',
    tool_parameters_mismatch: 'Params mismatch',
    modified_mcp_tool_defs: 'Modified tool defs',
    insufficient_scope: 'Insufficient scope'
};

const BLOCKING_REASON_DESCRIPTIONS: Record<string, string> = {
    no_llm_calls_made_by_app: 'The app made no LLM calls before requesting tool access',
    tool_not_selected_by_llm: 'Requested MCP Server Tool was not selected by the LLM',
    tool_intent_mismatch: "MCP Server Tool choice doesn't match the intention of original input",
    tool_parameters_mismatch: 'Requested MCP Server Tool Parameters are different from those selected by the LLM',
    modified_mcp_tool_defs: 'The LLM received modified MCP Server Tool Definitions',
    insufficient_scope: 'Token does not have the required scope for this tool'
};

const APP_TYPE_LABELS: Record<AppType, string> = {client: 'Client', agent: 'Agent', mcp_server: 'MCP'};
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
                    {APP_TYPE_LABELS[info.type]}
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
    const time = new Date(createdAt).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});
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

function EventAttributes({event}: {event: Trace['event']}) {
    const entries = Object.entries(event).filter(
        ([key, val]) => !ALWAYS_HIDDEN.has(key) && val !== null && val !== undefined
    );
    if (entries.length === 0) return null;
    return (
        <div className="mt-1.5 ml-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
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
                    <EventAttributes event={event} />
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

// ─── Page ────────────────────────────────────────────────────────────────────

export function AuthRequestDetailPage() {
    const {userInputId} = useParams<{userInputId: string}>();
    const navigate = useNavigate();

    const {data: tracesData, isLoading} = useTraces(undefined, 1, 100, true);

    const masId = useMemo(() => {
        if (!tracesData?.items || !userInputId) return null;
        const traces = tracesData.items[userInputId];
        const t = traces?.find((t) => t.event.mas_id);
        return t?.event.mas_id ?? null;
    }, [tracesData, userInputId]);

    const {data: masData} = useMASById(masId ?? '');
    const {data: appsData} = useMASApps(masId ?? '');

    const appNames: AppNames = useMemo(() => {
        if (!appsData) return {};
        return Object.fromEntries(
            appsData.filter((a) => a.id && a.name).map((a) => [a.id!, {name: a.name, type: a.type}])
        );
    }, [appsData]);

    const session = useMemo(() => {
        if (!userInputId || !tracesData?.items) return null;
        const traces = tracesData.items[userInputId];
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
              second: '2-digit'
          })
        : null;

    const durationLabel =
        session?.durationMs != null
            ? session.durationMs < 1000
                ? `${session.durationMs}ms`
                : `${(session.durationMs / 1000).toFixed(1)}s`
            : '—';

    let llmCallIndex = 0;

    if (isLoading) {
        return (
            <div className="space-y-4">
                <Skeleton className="h-5 w-48" />
                <div className="grid grid-cols-4 gap-3">
                    {Array.from({length: 4}).map((_, i) => (
                        <Skeleton key={i} className="h-20" />
                    ))}
                </div>
                <div className="space-y-2">
                    {Array.from({length: 6}).map((_, i) => (
                        <Skeleton key={i} className="h-10 w-full" />
                    ))}
                </div>
            </div>
        );
    }

    if (!session) {
        return (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-muted-foreground">
                <Activity className="h-10 w-10 opacity-40" />
                <p className="text-sm font-medium">Session not found</p>
                <Button variant="ghost" size="sm" onClick={() => navigate('/auth-requests')} className="cursor-pointer">
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to Auth Requests
                </Button>
            </div>
        );
    }

    const masName = masData?.name ?? masId;

    return (
        <div className="space-y-6">
            {/* Context banner */}
            <div className="flex items-center gap-2 rounded-lg border bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
                <Info className="h-4 w-4 flex-shrink-0 text-muted-foreground/60" />
                <p className="leading-relaxed">
                    You opened this session trace from{' '}
                    <Link
                        to="/auth-requests"
                        className="text-foreground underline decoration-dotted hover:decoration-solid"
                    >
                        Auth Requests
                    </Link>
                    .
                    {masId && (
                        <>
                            {' '}
                            Open{' '}
                            <button
                                type="button"
                                className="text-foreground underline decoration-dotted hover:decoration-solid cursor-pointer"
                                onClick={() => navigate(`/mas/${masId}?tab=traces`)}
                            >
                                {masName}
                            </button>{' '}
                            on the Traces tab.
                        </>
                    )}
                </p>
            </div>

            {/* Page title + actions */}
            <div className="flex items-start justify-between gap-4">
                <div className="space-y-1 min-w-0">
                    <h1 className="text-2xl font-bold truncate">
                        {session.prompt ?? <span className="text-muted-foreground italic font-normal">No prompt</span>}
                    </h1>
                    <p className="text-sm text-muted-foreground">{datetime}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                    {masId && (
                        <Button
                            variant="default"
                            size="sm"
                            onClick={() => navigate(`/mas/${masId}?tab=deny_conditions`)}
                            className="cursor-pointer"
                        >
                            <ShieldAlert className="mr-2 h-3.5 w-3.5" />
                            Configure deny conditions
                        </Button>
                    )}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                            downloadJson(session.events, `session-${userInputId?.slice(0, 8) ?? 'trace'}.json`);
                            toast.success('Session downloaded');
                        }}
                        className="cursor-pointer"
                    >
                        <Download className="mr-2 h-3.5 w-3.5" />
                        Download
                    </Button>
                </div>
            </div>

            {/* Stat cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="rounded-lg border bg-muted/20 p-4 space-y-1">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">
                        Multi-Agent System
                    </p>
                    {masId ? (
                        <button
                            type="button"
                            className="flex items-center gap-1 text-sm font-medium hover:underline cursor-pointer text-left truncate w-full"
                            onClick={() => navigate(`/mas/${masId}`)}
                        >
                            <Network className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                            <span className="truncate">{masName}</span>
                        </button>
                    ) : (
                        <p className="text-sm text-muted-foreground">—</p>
                    )}
                </div>
                <div className="rounded-lg border bg-muted/20 p-4 space-y-1">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">Activity</p>
                    <p className="text-sm font-medium tabular-nums">
                        {session.tokenCount} token{session.tokenCount !== 1 ? 's' : ''} · {session.mcpCallCount} MCP
                    </p>
                    <p className="text-[11px] text-muted-foreground tabular-nums">
                        {session.llmCallCount} LLM call{session.llmCallCount !== 1 ? 's' : ''}
                    </p>
                </div>
                <div className="rounded-lg border bg-muted/20 p-4 space-y-1">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">Events</p>
                    <p className="text-sm font-medium tabular-nums">{session.events.length}</p>
                    <div className="flex items-center gap-2 text-[11px]">
                        {session.allowedCount > 0 && (
                            <span className="flex items-center gap-0.5 text-green-500">
                                <CheckCircle2 className="h-3 w-3" />
                                {session.allowedCount}
                            </span>
                        )}
                        {session.deniedCount > 0 && (
                            <span className="flex items-center gap-0.5 text-destructive">
                                <XCircle className="h-3 w-3" />
                                {session.deniedCount}
                            </span>
                        )}
                        {session.allowedCount === 0 && session.deniedCount === 0 && (
                            <span className="text-muted-foreground">—</span>
                        )}
                    </div>
                </div>
                <div className="rounded-lg border bg-muted/20 p-4 space-y-1">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">Duration</p>
                    <p className="text-sm font-medium tabular-nums">{durationLabel}</p>
                    <p className="text-[11px] text-muted-foreground">{datetime}</p>
                </div>
            </div>

            {/* Timeline */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-sm font-semibold">Timeline</h2>
                        <code className="text-[11px] text-muted-foreground/60 font-mono">{userInputId}</code>
                    </div>
                    <Link
                        to="/auth-requests"
                        className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <ArrowLeft className="h-3.5 w-3.5" />
                        Auth Requests
                    </Link>
                </div>
                <div className="rounded-lg border bg-card p-4 space-y-0.5">
                    {session.events.map((trace) => {
                        const idx = trace.event_type === 'LLMCallStartedEvent' ? llmCallIndex++ : undefined;
                        return <EventRow key={trace.id} trace={trace} index={idx} appNames={appNames} />;
                    })}
                </div>
            </div>
        </div>
    );
}
