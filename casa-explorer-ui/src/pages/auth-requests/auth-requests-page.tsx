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
import {useNavigate, useSearchParams} from 'react-router-dom';
import {PATHS} from '@/router/paths';
import {useTraces} from '@/hooks/use-traces';
import {useMAS, useMASApps} from '@/hooks/use-mas';
import {useApps} from '@/hooks/use-apps';
import {DataTable} from '@/components/ui/data-table';
import {CheckTypeBadge} from '@/components/ui/check-type-badge';
import {AuthStatusBadge} from '@/components/ui/auth-status-badge';
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
    ExternalLink,
    Activity,
    Download
} from 'lucide-react';
import type {ColumnDef} from '@tanstack/react-table';
import {ArrowUpDown} from 'lucide-react';
import type {BlockingReason, Trace} from '@/types/trace.types';
import {
    EventRow,
    downloadJson,
    BLOCKING_REASON_LABELS,
    BLOCKING_REASON_DESCRIPTIONS
} from '@/components/traces/event-row';
import type {AppNames} from '@/components/traces/event-row';
import {toast} from 'sonner';

// ─── Session trace sheet ─────────────────────────────────────────────────────

interface SessionTraceSheetProps {
    userInputId: string | null;
    focusTraceId: string | null;
    masId: string | null;
    masName: string | null;
    tracesData: Record<string, Trace[]> | null;
    onClose: () => void;
}

function SessionTraceSheet({userInputId, focusTraceId, masId, masName, tracesData, onClose}: SessionTraceSheetProps) {
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
                    {!session ? (
                        <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                            <Activity className="h-8 w-8 opacity-40" />
                            <p className="text-sm">No events found for this session</p>
                        </div>
                    ) : (
                        session.events.map((trace) => {
                            const idx = trace.event_type === 'LLMCallStartedEvent' ? llmCallIndex++ : undefined;
                            return (
                                <EventRow
                                    key={trace.id}
                                    trace={trace}
                                    index={idx}
                                    appNames={appNames}
                                    initialExpanded={trace.id === focusTraceId}
                                />
                            );
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
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
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
        return Object.fromEntries((masData.items ?? []).map((m) => [m.id, m.name]));
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
                                    if (req.masId) navigate(PATHS.mas.detail(req.masId));
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
                            <AuthStatusBadge blocked={blocked} />
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
                            {!type ? <span className="text-muted-foreground">—</span> : <CheckTypeBadge type={type} />}
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
                                setSelectedTraceId(row.id);
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
                focusTraceId={selectedTraceId}
                masId={selectedMasId}
                masName={selectedMasName}
                tracesData={tracesData?.items ?? null}
                onClose={() => {
                    setSelectedUserInputId(null);
                    setSelectedTraceId(null);
                    setSelectedMasId(null);
                    setSelectedMasName(null);
                }}
            />
        </div>
    );
}
