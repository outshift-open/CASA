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

import {useMemo} from 'react';
import {useNavigate} from 'react-router-dom';
import {PATHS} from '@/router/paths';
import {useSession} from '@/hooks/use-traces';
import {EventType} from '@/types/trace.types';
import {useMASById, useMASApps} from '@/hooks/use-mas';
import {Button} from '@/components/ui/button';
import {Skeleton} from '@/components/ui/skeleton';
import {Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle} from '@/components/ui/sheet';
import {CheckCircle2, XCircle, Network, X, ExternalLink, Activity, Download} from 'lucide-react';
import {EventRow, downloadJson} from '@/components/traces/event-row';
import type {AppNames} from '@/components/traces/event-row';
import {toast} from 'sonner';

interface SessionTraceSheetProps {
    userInputId: string | null;
    focusTraceId: string | null;
    onClose: () => void;
}

export function SessionTraceSheet({userInputId, focusTraceId, onClose}: SessionTraceSheetProps) {
    const navigate = useNavigate();
    const {data: sessionData, isLoading} = useSession(userInputId ?? undefined);

    const session = useMemo(() => {
        if (!sessionData || sessionData.length === 0) return null;
        const tokenIssued = sessionData.find((t) => t.event_type === EventType.TokenIssued);
        const mcpCalls = sessionData.filter((t) => t.event_type === EventType.MCPCallStarted);
        const llmCallCount = sessionData.filter((t) => t.event_type === EventType.LLMCallStarted).length;
        const tokenCount = sessionData.filter(
            (t) => t.event_type === EventType.TokenIssued || t.event_type === EventType.TokenExchanged
        ).length;
        const masId = sessionData.find((t) => t.event.mas_id)?.event.mas_id ?? null;
        const firstTs = sessionData[0]?.created_at ? new Date(sessionData[0].created_at).getTime() : null;
        const lastTs = sessionData[sessionData.length - 1]?.created_at
            ? new Date(sessionData[sessionData.length - 1].created_at).getTime()
            : null;
        const durationMs = firstTs && lastTs ? lastTs - firstTs : null;
        return {
            masId,
            prompt: tokenIssued?.event.prompt ?? null,
            createdAt: tokenIssued?.created_at ?? sessionData[0]?.created_at ?? '',
            events: sessionData,
            allowedCount: mcpCalls.filter((t) => !t.event.blocked).length,
            deniedCount: mcpCalls.filter((t) => t.event.blocked).length,
            llmCallCount,
            mcpCallCount: mcpCalls.length,
            tokenCount,
            durationMs
        };
    }, [sessionData]);

    const masId = session?.masId ?? null;
    const {data: appsData} = useMASApps(masId ?? '');
    const {data: masData} = useMASById(masId ?? '');

    const masName = masData?.name ?? masId;

    const appNames: AppNames = useMemo(() => {
        if (!appsData) return {};
        return Object.fromEntries(
            appsData.filter((a) => a.id && a.name).map((a) => [a.id!, {name: a.name, type: a.type}])
        );
    }, [appsData]);

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
                                onClick={() => navigate(PATHS.authRequests.detail(userInputId))}
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
                                onClick={() => navigate(PATHS.mas.detail(masId))}
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
                    {isLoading ? (
                        <div className="space-y-2">
                            {Array.from({length: 4}).map((_, i) => (
                                <Skeleton key={i} className="h-10 w-full" />
                            ))}
                        </div>
                    ) : !session ? (
                        <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                            <Activity className="h-8 w-8 opacity-40" />
                            <p className="text-sm">No events found for this session</p>
                        </div>
                    ) : (
                        (() => {
                            let llmCallIndex = 0;
                            return session.events.map((trace) => {
                                const idx = trace.event_type === EventType.LLMCallStarted ? llmCallIndex++ : undefined;
                                return (
                                    <EventRow
                                        key={trace.id}
                                        trace={trace}
                                        index={idx}
                                        appNames={appNames}
                                        initialExpanded={trace.id === focusTraceId}
                                    />
                                );
                            });
                        })()
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
