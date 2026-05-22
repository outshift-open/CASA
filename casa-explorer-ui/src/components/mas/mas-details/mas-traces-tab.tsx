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
import {Activity, ChevronLeft, ChevronRight, ArrowUpDown} from 'lucide-react';
import {useQueries} from '@tanstack/react-query';
import {Skeleton} from '@/components/ui/skeleton';
import {Badge} from '@/components/ui/badge';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {useTraces} from '@/hooks/use-traces';
import {masService} from '@/services/mas.service';
import {EventType} from '@/types/trace.types';
import type {Trace} from '@/types/trace.types';
import type {AppNames} from '@/components/traces/event-row';
import {SessionRow} from '@/components/traces/session-row';
import type {SessionData} from '@/components/traces/session-row';

function buildSessions(items: Record<string, Trace[]>): SessionData[] {
    return Object.entries(items)
        .map(([userInputId, traces]) => {
            const sorted = [...traces].sort(
                (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
            );
            const tokenIssued = sorted.find((t) => t.event_type === EventType.TokenIssued);
            const mcpCalls = sorted.filter((t) => t.event_type === EventType.MCPCallStarted);
            const llmCallCount = sorted.filter((t) => t.event_type === EventType.LLMCallStarted).length;
            const agentCallCount = sorted.filter((t) => t.event_type === EventType.AgentCallStarted).length;
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
                agentCallCount,
                mcpCallCount: mcpCalls.length,
                tokenCount
            };
        })
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
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

    const masIds = useMemo(() => {
        if (!data?.items) return [masId];
        const ids = Object.values(data.items)
            .flat()
            .map((t) => t.event.mas_id)
            .filter(Boolean) as string[];
        return [...new Set([masId, ...ids])];
    }, [data, masId]);

    const appsQueries = useQueries({
        queries: masIds.map((id) => ({
            queryKey: ['mas', id, 'apps'],
            queryFn: () => masService.getMASApps(id),
            enabled: !!id
        }))
    });

    const appNames: AppNames = useMemo(() => {
        const result: AppNames = {};
        for (const q of appsQueries) {
            if (!q.data) continue;
            for (const a of q.data) {
                if (a.id && a.name) result[a.id] = {name: a.name, type: a.type};
            }
        }
        return result;
    }, [appsQueries]);

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
