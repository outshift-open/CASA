import {useMemo, useState} from 'react';
import {
    Activity,
    ChevronDown,
    ChevronRight,
    ChevronLeft,
    CheckCircle2,
    XCircle,
    Zap,
    ArrowRightLeft,
    Brain,
    BrainCircuit,
    ArrowUpDown,
    Download
} from 'lucide-react';
import {Skeleton} from '@/components/ui/skeleton';
import {Badge} from '@/components/ui/badge';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {toast} from 'sonner';
import {useTraces} from '@/hooks/use-traces';
import {useMASApps} from '@/hooks/use-mas';
import type {Trace, BlockingReason} from '@/types/trace.types';
import type {AppType} from '@/types/app.types';

function downloadJson(data: unknown, filename: string) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

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

const APP_TYPE_LABELS: Record<AppType, string> = {
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

interface Session {
    userInputId: string;
    prompt: string | null;
    createdAt: string;
    events: Trace[];
    allowedCount: number;
    deniedCount: number;
    llmCallCount: number;
}

function buildSessions(items: Record<string, Trace[]>): Session[] {
    return Object.entries(items)
        .map(([userInputId, traces]) => {
            const sorted = [...traces].sort(
                (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
            );
            const tokenIssued = sorted.find((t) => t.event_type === 'TokenIssuedEvent');
            const mcpCalls = sorted.filter((t) => t.event_type === 'MCPCallStartedEvent');
            const llmCallCount = sorted.filter((t) => t.event_type === 'LLMCallStartedEvent').length;
            return {
                userInputId,
                prompt: tokenIssued?.event.prompt ?? null,
                createdAt: tokenIssued?.created_at ?? sorted[0]?.created_at ?? '',
                events: sorted,
                allowedCount: mcpCalls.filter((t) => !t.event.blocked).length,
                deniedCount: mcpCalls.filter((t) => t.event.blocked).length,
                llmCallCount
            };
        })
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
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
    const time = new Date(createdAt).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    return <span className="ml-auto pl-3 text-[11px] text-muted-foreground/60 flex-shrink-0 tabular-nums">{time}</span>;
}

// Only hide internal/base fields
const ALWAYS_HIDDEN = new Set(['id', 'user_input_id', 'mas_id', 'created_at']);

const JWT_FIELDS = new Set(['token', 'subject_token', 'act_token']);

const FIELD_LABELS: Record<string, string> = {
    prompt: 'task'
};

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
                                className={`text-[9px] h-4 px-1.5 font-medium ${event.blocking_type === 'AI_POWERED' ? 'border-sky-500/50 text-sky-400' : 'border-orange-500/50 text-orange-400'}`}
                            >
                                {event.blocking_type === 'AI_POWERED' ? 'SEMANTIC' : 'DETERMINISTIC'}
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
                className="w-full flex items-start gap-2 py-1.5 pl-4 hover:bg-muted/30 transition-colors text-left cursor-pointer"
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
                <div className="pl-4 pb-2">
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

function SessionRow({session, appNames}: {session: Session; appNames: AppNames}) {
    const [expanded, setExpanded] = useState(false);
    const time = session.createdAt
        ? new Date(session.createdAt).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
          })
        : null;
    const date = session.createdAt
        ? new Date(session.createdAt).toLocaleDateString([], {month: 'short', day: 'numeric'})
        : null;

    let llmCallIndex = 0;

    return (
        <div className="border rounded-lg overflow-hidden">
            <button
                type="button"
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-accent/50 transition-colors text-left cursor-pointer"
                onClick={() => setExpanded((v) => !v)}
            >
                {expanded ? (
                    <ChevronDown className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                ) : (
                    <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mr-1.5">
                            Task:
                        </span>
                        {session.prompt ?? <span className="text-muted-foreground italic">No prompt</span>}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                        {date} {time}
                    </p>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                    {session.llmCallCount > 0 && (
                        <span className="text-xs text-blue-400 font-medium">
                            {session.llmCallCount} LLM {session.llmCallCount === 1 ? 'call' : 'calls'}
                        </span>
                    )}
                    {session.allowedCount > 0 && (
                        <span className="text-xs text-green-500 font-medium">{session.allowedCount} allowed</span>
                    )}
                    {session.deniedCount > 0 && (
                        <span className="text-xs text-destructive font-medium">{session.deniedCount} denied</span>
                    )}
                    {session.allowedCount === 0 && session.deniedCount === 0 && session.llmCallCount === 0 && (
                        <span className="text-xs text-muted-foreground">No activity</span>
                    )}
                    <button
                        type="button"
                        onClick={(e) => {
                            e.stopPropagation();
                            downloadJson(session.events, `session-${session.userInputId.slice(0, 8)}.json`);
                            toast.success('Session downloaded');
                        }}
                        className="ml-1 p-1 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors cursor-pointer"
                        aria-label="Download session"
                    >
                        <Download className="h-3.5 w-3.5" />
                    </button>
                </div>
            </button>
            {expanded && (
                <div className="px-4 pb-3 pt-1 border-t space-y-0.5 bg-muted/20">
                    {session.events.map((trace) => {
                        const idx = trace.event_type === 'LLMCallStartedEvent' ? llmCallIndex++ : undefined;
                        return <EventRow key={trace.id} trace={trace} index={idx} appNames={appNames} />;
                    })}
                </div>
            )}
        </div>
    );
}

interface MASTracesTabProps {
    masId: string;
}

const PAGE_SIZE_OPTIONS = [5, 10, 20, 50];

export function MASTracesTab({masId}: MASTracesTabProps) {
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(5);
    const [sortAsc, setSortAsc] = useState(false);
    const {data, isLoading} = useTraces(masId, page, pageSize, false, true);
    const {data: appsData} = useMASApps(masId, true);

    const appNames: AppNames = useMemo(() => {
        if (!appsData) return {};
        return Object.fromEntries(
            appsData.filter((a) => a.id && a.name).map((a) => [a.id!, {name: a.name, type: a.type}])
        );
    }, [appsData]);

    const sessions = useMemo(() => {
        if (!data?.items) return [];
        const built = buildSessions(data.items);
        return sortAsc ? [...built].reverse() : built;
    }, [data, sortAsc]);

    const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

    if (isLoading) {
        return (
            <div className="space-y-2">
                {Array.from({length: 4}).map((_, i) => (
                    <Skeleton key={i} className="h-14 w-full" />
                ))}
            </div>
        );
    }

    if (sessions.length === 0 && page === 1) {
        return (
            <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                <Activity className="h-10 w-10 opacity-40" />
                <div className="text-center">
                    <p className="text-sm font-medium">No traces yet</p>
                    <p className="text-xs mt-1">Authorization activity will appear here once agents start running</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Badge variant="outline" className="gap-1.5 border-red-500/30 text-red-400 bg-red-500/10">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75" />
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
                        </span>
                        LIVE
                    </Badge>
                    {data && data.total > 0 && (
                        <Badge variant="outline">
                            {data.total} {data.total === 1 ? 'session' : 'sessions'}
                        </Badge>
                    )}
                </div>
                <button
                    type="button"
                    onClick={() => setSortAsc((v) => !v)}
                    className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                >
                    <ArrowUpDown className="h-3.5 w-3.5" />
                    {sortAsc ? 'Oldest first' : 'Newest first'}
                </button>
            </div>

            {sessions.map((session) => (
                <SessionRow key={session.userInputId} session={session} appNames={appNames} />
            ))}

            {(totalPages > 1 || data?.total) && (
                <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">Sessions per page</span>
                        <Select
                            value={`${pageSize}`}
                            onValueChange={(v) => {
                                setPageSize(Number(v));
                                setPage(1);
                            }}
                        >
                            <SelectTrigger className="h-8 w-[70px]">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent side="top">
                                {PAGE_SIZE_OPTIONS.map((s) => (
                                    <SelectItem key={s} value={`${s}`}>
                                        {s}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        {data && data.total > 0 && (
                            <span className="text-xs text-muted-foreground">
                                {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, data.total)} of {data.total}{' '}
                                session{data.total === 1 ? '' : 's'}
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-1">
                        <button
                            type="button"
                            onClick={() => setPage((p) => Math.max(1, p - 1))}
                            disabled={page === 1}
                            className="p-1.5 rounded border hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                            aria-label="Previous page"
                        >
                            <ChevronLeft className="h-3.5 w-3.5" />
                        </button>
                        <span className="text-xs text-muted-foreground px-1">
                            {page} / {totalPages}
                        </span>
                        <button
                            type="button"
                            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages}
                            className="p-1.5 rounded border hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                            aria-label="Next page"
                        >
                            <ChevronRight className="h-3.5 w-3.5" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
