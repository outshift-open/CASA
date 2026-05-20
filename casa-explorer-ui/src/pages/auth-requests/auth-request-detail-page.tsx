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

import {useMemo} from 'react';
import {useParams, useNavigate, Link} from 'react-router-dom';
import {PATHS} from '@/router/paths';
import {useSession} from '@/hooks/use-traces';
import {EventType} from '@/types/trace.types';
import {useMASApps, useMASById} from '@/hooks/use-mas';
import {Skeleton} from '@/components/ui/skeleton';
import {Button} from '@/components/ui/button';
import {ArrowLeft, Network, CheckCircle2, XCircle, Activity, Download, ShieldAlert, Info} from 'lucide-react';
import {toast} from 'sonner';
import {EventRow, downloadJson} from '@/components/traces/event-row';
import type {AppNames} from '@/components/traces/event-row';

// ─── Page ────────────────────────────────────────────────────────────────────

export function AuthRequestDetailPage() {
    const {userInputId} = useParams<{userInputId: string}>();
    const navigate = useNavigate();

    const {data: tracesData, isLoading} = useSession(userInputId);

    const masId = useMemo(() => {
        return tracesData?.find((t) => t.event.mas_id)?.event.mas_id ?? null;
    }, [tracesData]);

    const {data: masData} = useMASById(masId ?? '');
    const {data: appsData} = useMASApps(masId ?? '');

    const appNames: AppNames = useMemo(() => {
        if (!appsData) return {};
        return Object.fromEntries(
            appsData.filter((a) => a.id && a.name).map((a) => [a.id!, {name: a.name, type: a.type}])
        );
    }, [appsData]);

    const session = useMemo(() => {
        if (!tracesData || tracesData.length === 0) return null;
        const tokenIssued = tracesData.find((t) => t.event_type === EventType.TokenIssued);
        const mcpCalls = tracesData.filter((t) => t.event_type === EventType.MCPCallStarted);
        const llmCallCount = tracesData.filter((t) => t.event_type === EventType.LLMCallStarted).length;
        const agentCallCount = tracesData.filter((t) => t.event_type === EventType.AgentCallStarted).length;
        const tokenCount = tracesData.filter(
            (t) => t.event_type === EventType.TokenIssued || t.event_type === EventType.TokenExchanged
        ).length;
        const firstTs = tracesData[0]?.created_at ? new Date(tracesData[0].created_at).getTime() : null;
        const lastTs = tracesData[tracesData.length - 1]?.created_at
            ? new Date(tracesData[tracesData.length - 1].created_at).getTime()
            : null;
        const durationMs = firstTs && lastTs ? lastTs - firstTs : null;
        return {
            prompt: tokenIssued?.event.prompt ?? null,
            createdAt: tokenIssued?.created_at ?? tracesData[0]?.created_at ?? '',
            events: tracesData,
            allowedCount: mcpCalls.filter((t) => !t.event.blocked).length,
            deniedCount: mcpCalls.filter((t) => t.event.blocked).length,
            llmCallCount,
            agentCallCount,
            mcpCallCount: mcpCalls.length,
            tokenCount,
            durationMs
        };
    }, [tracesData]);

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
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(PATHS.authRequests.list)}
                    className="cursor-pointer"
                >
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
                        to={PATHS.authRequests.list}
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
                                onClick={() => navigate(PATHS.mas.detailTab(masId, 'traces'))}
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
                            onClick={() => navigate(PATHS.mas.detailTab(masId, 'deny_conditions'))}
                            className="cursor-pointer"
                        >
                            <ShieldAlert className="mr-2 h-3.5 w-3.5" />
                            Configure Deny Conditions
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
                            onClick={() => navigate(PATHS.mas.detail(masId))}
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
                        {session.llmCallCount} LLM · {session.agentCallCount} agent call
                        {session.agentCallCount !== 1 ? 's' : ''}
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
                        to={PATHS.authRequests.list}
                        className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <ArrowLeft className="h-3.5 w-3.5" />
                        Auth Requests
                    </Link>
                </div>
                <div className="rounded-lg border bg-card p-4">
                    {(() => {
                        let llmCallIndex = 0;
                        return session.events.map((trace) => {
                            const idx = trace.event_type === EventType.LLMCallStarted ? llmCallIndex++ : undefined;
                            return <EventRow key={trace.id} trace={trace} index={idx} appNames={appNames} />;
                        });
                    })()}
                </div>
            </div>
        </div>
    );
}
