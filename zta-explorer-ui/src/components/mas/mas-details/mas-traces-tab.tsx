import {useMemo, useState} from 'react';
import {
    Activity,
    ChevronDown,
    ChevronRight,
    CheckCircle2,
    XCircle,
    Zap,
    ArrowRightLeft,
    Brain,
    BrainCircuit,
    ArrowUpDown
} from 'lucide-react';
import {Skeleton} from '@/components/ui/skeleton';
import {Badge} from '@/components/ui/badge';
import {useTraces} from '@/hooks/use-traces';
import {useMASApps} from '@/hooks/use-mas';
import type {Trace, EventType, BlockingReason} from '@/types/trace.types';

const BLOCKING_REASON_LABELS: Record<BlockingReason, string> = {
    no_llm_calls_made_by_app: 'No LLM calls made',
    tool_not_selected_by_llm: 'Not selected by LLM',
    tool_intent_mismatch: 'Intent mismatch',
    tool_parameters_mismatch: 'Params mismatch',
    modified_mcp_tool_defs: 'Modified tool defs',
    insufficient_scope: 'Insufficient scope'
};

const EVENT_ORDER: EventType[] = [
    'TokenIssuedEvent',
    'TokenExchangedEvent',
    'LLMCallStartedEvent',
    'LLMCallEndedEvent',
    'MCPCallStartedEvent'
];

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

type AppNames = Record<string, string>;

interface Session {
    userInputId: string;
    prompt: string | null;
    createdAt: string;
    events: Trace[];
    approvedCount: number;
    blockedCount: number;
    llmCallCount: number;
}

function buildSessions(items: Record<string, Trace[]>): Session[] {
    return Object.entries(items)
        .map(([userInputId, traces]) => {
            const sorted = [...traces].sort(
                (a, b) =>
                    EVENT_ORDER.indexOf(a.event_type) - EVENT_ORDER.indexOf(b.event_type) ||
                    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
            );
            const tokenIssued = sorted.find((t) => t.event_type === 'TokenIssuedEvent');
            const mcpCalls = sorted.filter((t) => t.event_type === 'MCPCallStartedEvent');
            const llmCallCount = sorted.filter((t) => t.event_type === 'LLMCallStartedEvent').length;
            return {
                userInputId,
                prompt: tokenIssued?.event.prompt ?? null,
                createdAt: tokenIssued?.created_at ?? sorted[0]?.created_at ?? '',
                events: sorted,
                approvedCount: mcpCalls.filter((t) => !t.event.blocked).length,
                blockedCount: mcpCalls.filter((t) => t.event.blocked).length,
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
    const name = appNames[id];
    return (
        <code className="px-1 py-0.5 rounded bg-muted text-[10px] font-mono" title={id}>
            {name ?? shortId(id)}
        </code>
    );
}

function EventRow({trace, index, appNames}: {trace: Trace; index?: number; appNames: AppNames}) {
    const {event_type, event} = trace;

    if (event_type === 'TokenIssuedEvent') {
        return (
            <div className="flex items-start gap-2 py-1.5 pl-4 border-l-2 border-muted ml-2">
                <Zap className="h-3.5 w-3.5 text-muted-foreground mt-0.5 flex-shrink-0" />
                <div className="text-xs text-muted-foreground flex flex-wrap items-center gap-x-1">
                    <span className="font-medium text-foreground">Token issued</span>
                    {event.app_id && (
                        <>
                            <span>by</span>
                            <AppIdChip id={event.app_id} appNames={appNames} />
                        </>
                    )}
                    {event.prompt && <span className="ml-1 text-foreground/70">"{event.prompt}"</span>}
                </div>
            </div>
        );
    }

    if (event_type === 'TokenExchangedEvent') {
        const tools = parseToolsList(event.tools);
        return (
            <div className="flex items-start gap-2 py-1.5 pl-4 border-l-2 border-muted ml-2">
                <ArrowRightLeft className="h-3.5 w-3.5 text-muted-foreground mt-0.5 flex-shrink-0" />
                <div className="text-xs text-muted-foreground flex flex-wrap items-center gap-x-1">
                    <span className="font-medium text-foreground">Token exchanged</span>
                    {event.subject_app_id && (
                        <>
                            <span>by</span>
                            <AppIdChip id={event.subject_app_id} appNames={appNames} />
                        </>
                    )}
                    {tools.length > 0 && (
                        <>
                            <span className="ml-1">— requested:</span>
                            <ToolChips tools={tools} />
                        </>
                    )}
                </div>
            </div>
        );
    }

    if (event_type === 'LLMCallStartedEvent') {
        const tools = parseToolsList(event.tools);
        return (
            <div className="flex items-start gap-2 py-1.5 pl-4 border-l-2 border-blue-500/30 ml-2">
                <Brain className="h-3.5 w-3.5 text-blue-400 mt-0.5 flex-shrink-0" />
                <div className="text-xs text-muted-foreground flex flex-wrap items-center gap-x-1">
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
            </div>
        );
    }

    if (event_type === 'LLMCallEndedEvent') {
        const selectedTools = parseToolsList(event.tools);
        return (
            <div className="flex items-start gap-2 py-1.5 pl-4 border-l-2 border-blue-500/30 ml-2">
                <BrainCircuit className="h-3.5 w-3.5 text-blue-400 mt-0.5 flex-shrink-0" />
                <div className="text-xs text-muted-foreground flex flex-wrap items-center gap-x-1">
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
            </div>
        );
    }

    if (event_type === 'MCPCallStartedEvent') {
        const blocked = event.blocked;
        const reason = event.blocking_reason ? BLOCKING_REASON_LABELS[event.blocking_reason] : null;
        return (
            <div
                className={`flex items-start gap-2 py-1.5 pl-4 border-l-2 ml-2 ${blocked ? 'border-destructive/40' : 'border-green-500/40'}`}
            >
                {blocked ? (
                    <XCircle className="h-3.5 w-3.5 text-destructive mt-0.5 flex-shrink-0" />
                ) : (
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
                )}
                <div className="text-xs flex flex-wrap items-center gap-x-2 gap-y-1">
                    <code className="px-1.5 py-0.5 rounded bg-muted font-mono text-[11px]">{event.tool ?? '—'}</code>
                    {(event.caller_app_id || event.callee_app_id) && (
                        <span className="text-muted-foreground flex items-center gap-1">
                            <AppIdChip id={event.caller_app_id} appNames={appNames} />
                            <span>→</span>
                            <AppIdChip id={event.callee_app_id} appNames={appNames} />
                        </span>
                    )}
                    {blocked ? (
                        <Badge variant="destructive" className="text-[10px] h-4 px-1.5">
                            Blocked{reason ? ` · ${reason}` : ''}
                        </Badge>
                    ) : (
                        <Badge variant="outline" className="text-[10px] h-4 px-1.5 border-green-500/50 text-green-500">
                            Approved
                        </Badge>
                    )}
                </div>
            </div>
        );
    }

    return null;
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

    // Track LLM call index for numbering
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
                    {session.approvedCount > 0 && (
                        <span className="text-xs text-green-500 font-medium">{session.approvedCount} approved</span>
                    )}
                    {session.blockedCount > 0 && (
                        <span className="text-xs text-destructive font-medium">{session.blockedCount} blocked</span>
                    )}
                    {session.approvedCount === 0 && session.blockedCount === 0 && session.llmCallCount === 0 && (
                        <span className="text-xs text-muted-foreground">No activity</span>
                    )}
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

const PAGE_SIZE = 10;

export function MASTracesTab({masId}: MASTracesTabProps) {
    const [page, setPage] = useState(1);
    const [sortAsc, setSortAsc] = useState(false);
    const {data, isLoading} = useTraces(masId, page, PAGE_SIZE);
    const {data: appsData} = useMASApps(masId);

    const appNames: AppNames = useMemo(() => {
        if (!appsData) return {};
        return Object.fromEntries(appsData.filter((a) => a.id && a.name).map((a) => [a.id!, a.name]));
    }, [appsData]);

    const sessions = useMemo(() => {
        if (!data?.items) return [];
        const built = buildSessions(data.items);
        return sortAsc ? [...built].reverse() : built;
    }, [data, sortAsc]);

    const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

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
                <p className="text-xs text-muted-foreground">
                    {data && data.total > 0
                        ? `${(page - 1) * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE, data.total)} of ${data.total} sessions`
                        : ''}
                </p>
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

            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 pt-2">
                    <button
                        type="button"
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="text-xs px-3 py-1.5 rounded border hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                    >
                        Previous
                    </button>
                    <span className="text-xs text-muted-foreground">
                        Page {page} of {totalPages}
                    </span>
                    <button
                        type="button"
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="text-xs px-3 py-1.5 rounded border hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
}
