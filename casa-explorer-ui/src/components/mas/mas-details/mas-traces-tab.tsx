/**
 * Copyright 2026 Cisco Systems, Inc. and its affiliates
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
import {
    Activity,
    ChevronDown,
    ChevronRight,
    ChevronLeft,
    CheckCircle2,
    XCircle,
    ArrowUpDown,
    Download
} from 'lucide-react';
import {Skeleton} from '@/components/ui/skeleton';
import {Badge} from '@/components/ui/badge';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {toast} from 'sonner';
import {useTraces} from '@/hooks/use-traces';
import {useMASApps} from '@/hooks/use-mas';
import {EventType} from '@/types/trace.types';
import type {Trace} from '@/types/trace.types';
import {EventRow, downloadJson} from '@/components/traces/event-row';
import type {AppNames} from '@/components/traces/event-row';

interface Session {
    userInputId: string;
    prompt: string | null;
    createdAt: string;
    events: Trace[];
    allowedCount: number;
    deniedCount: number;
    llmCallCount: number;
    mcpCallCount: number;
    tokenCount: number;
}

function buildSessions(items: Record<string, Trace[]>): Session[] {
    return Object.entries(items)
        .map(([userInputId, traces]) => {
            const sorted = [...traces].sort(
                (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
            );
            const tokenIssued = sorted.find((t) => t.event_type === EventType.TokenIssued);
            const mcpCalls = sorted.filter((t) => t.event_type === EventType.MCPCallStarted);
            const llmCallCount = sorted.filter((t) => t.event_type === EventType.LLMCallStarted).length;
            const tokenCount = sorted.filter(
                (t) => t.event_type === EventType.TokenIssued || t.event_type === EventType.TokenExchanged
            ).length;
            return {
                userInputId,
                prompt: tokenIssued?.event.prompt ?? null,
                createdAt: tokenIssued?.created_at ?? sorted[0]?.created_at ?? '',
                events: sorted,
                allowedCount: mcpCalls.filter((t) => !t.event.blocked).length,
                deniedCount: mcpCalls.filter((t) => t.event.blocked).length,
                llmCallCount,
                mcpCallCount: mcpCalls.length,
                tokenCount
            };
        })
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}

function SessionRow({session, appNames}: {session: Session; appNames: AppNames}) {
    const [expanded, setExpanded] = useState(false);
    const datetime = session.createdAt
        ? new Date(session.createdAt).toLocaleString([], {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
          })
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
                    {datetime && <p className="text-xs text-muted-foreground mt-0.5">{datetime}</p>}
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0 text-xs">
                    <span className="text-muted-foreground tabular-nums">
                        {session.tokenCount} token{session.tokenCount !== 1 ? 's' : ''}
                        {session.llmCallCount > 0 && <> · {session.llmCallCount} LLM</>}
                        {session.mcpCallCount > 0 && <> · {session.mcpCallCount} MCP</>}
                    </span>
                    <span className="flex items-center gap-2">
                        {session.allowedCount > 0 && (
                            <span className="flex items-center gap-0.5 text-green-500 font-medium">
                                <CheckCircle2 className="h-3.5 w-3.5" />
                                {session.allowedCount}
                            </span>
                        )}
                        {session.deniedCount > 0 && (
                            <span className="flex items-center gap-0.5 text-destructive font-medium">
                                <XCircle className="h-3.5 w-3.5" />
                                {session.deniedCount}
                            </span>
                        )}
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                downloadJson(session.events, `session-${session.userInputId.slice(0, 8)}.json`);
                                toast.success('Session downloaded');
                            }}
                            className="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors cursor-pointer"
                            aria-label="Download session"
                        >
                            <Download className="h-3.5 w-3.5" />
                        </button>
                    </span>
                </div>
            </button>
            {expanded && (
                <div className="px-4 pb-3 border-t bg-muted/20">
                    {session.events.map((trace) => {
                        const idx = trace.event_type === EventType.LLMCallStarted ? llmCallIndex++ : undefined;
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
    const {data, isLoading} = useTraces({masId, page, pageSize, sortAsc}, true);
    const {data: appsData} = useMASApps(masId, true);

    const appNames: AppNames = useMemo(() => {
        if (!appsData) return {};
        return Object.fromEntries(
            appsData.filter((a) => a.id && a.name).map((a) => [a.id!, {name: a.name, type: a.type}])
        );
    }, [appsData]);

    const sessions = useMemo(() => {
        if (!data?.items) return [];
        return buildSessions(data.items);
    }, [data]);

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

    if (sessions.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                <Activity className="h-10 w-10 opacity-40" />
                <div className="text-center">
                    <p className="text-sm font-medium">{page > 1 ? 'No sessions on this page' : 'No traces yet'}</p>
                    <p className="text-xs mt-1">
                        {page > 1
                            ? 'Try going back to a previous page'
                            : 'Authorization activity will appear here once agents start running'}
                    </p>
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
                    onClick={() => {
                        setSortAsc((v) => !v);
                        setPage(1);
                    }}
                    className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                >
                    <ArrowUpDown className="h-3.5 w-3.5" />
                    {sortAsc ? 'Oldest First' : 'Newest First'}
                </button>
            </div>

            {sessions.map((session) => (
                <SessionRow key={session.userInputId} session={session} appNames={appNames} />
            ))}

            {(data?.total ?? 0) > 0 && (
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
