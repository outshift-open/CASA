import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Skeleton} from '@/components/ui/skeleton';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Shield, Lock, AppWindow, Network, Tags, RefreshCw} from 'lucide-react';
import {useApps} from '@/hooks/use-apps';
import {useMAS} from '@/hooks/use-mas';
import {useScopes} from '@/hooks/use-scopes';
import {useTraces} from '@/hooks/use-traces';
import {useMemo} from 'react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {
    PieChart,
    Pie,
    Cell,
    Tooltip as ChartTooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid
} from 'recharts';
import type {BlockingReason, Trace} from '@/types/trace.types';

const BLOCKING_REASON_LABELS: Record<BlockingReason, string> = {
    no_llm_calls_made_by_app: 'No LLM calls',
    tool_not_selected_by_llm: 'Not selected by LLM',
    tool_intent_mismatch: 'Intent mismatch',
    tool_parameters_mismatch: 'Params mismatch',
    modified_mcp_tool_defs: 'Modified tool defs',
    insufficient_scope: 'Insufficient scope'
};

const CHART_TOOLTIP_STYLE = {
    contentStyle: {
        backgroundColor: '#22252b',
        border: '1px solid rgba(204,204,220,0.2)',
        borderRadius: '6px',
        fontSize: '12px'
    },
    itemStyle: {color: '#ccccdc'},
    labelStyle: {color: '#ccccdc'}
};

interface DonutChartProps {
    data: {name: string; value: number; color: string}[];
    loading: boolean;
    emptyIcon: React.ReactNode;
    emptyText: string;
    unit: string;
}

function DonutChart({data, loading, emptyIcon, emptyText, unit}: DonutChartProps) {
    if (loading) {
        return (
            <div className="flex items-center justify-center h-[200px]">
                <Skeleton className="h-[160px] w-[160px] rounded-full" />
            </div>
        );
    }
    if (data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-[200px] gap-3 text-muted-foreground">
                {emptyIcon}
                <p className="text-sm">{emptyText}</p>
            </div>
        );
    }
    const total = data.reduce((s, d) => s + d.value, 0);
    return (
        <div className="flex items-center justify-center gap-8">
            <div className="w-[160px] h-[160px] flex-shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={48}
                            outerRadius={72}
                            paddingAngle={data.length > 1 ? 3 : 0}
                            dataKey="value"
                        >
                            {data.map((entry) => (
                                <Cell key={entry.name} fill={entry.color} />
                            ))}
                        </Pie>
                        <ChartTooltip
                            {...CHART_TOOLTIP_STYLE}
                            formatter={(value: number, name: string) => [value, name]}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
            <div className="flex flex-col gap-3">
                {data.map((entry) => {
                    const pct = Math.round((entry.value / total) * 100);
                    return (
                        <div key={entry.name} className="flex items-center gap-2.5">
                            <span
                                className="h-2.5 w-2.5 rounded-full flex-shrink-0"
                                style={{backgroundColor: entry.color}}
                            />
                            <div className="flex flex-col">
                                <span className="text-sm font-medium leading-none">{entry.name}</span>
                                <span className="text-xs text-muted-foreground mt-1">
                                    {entry.value} {entry.value === 1 ? unit : `${unit}s`} · {pct}%
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export function DashboardPage() {
    const navigate = useNavigate();
    const {data: appsData, isLoading, error, dataUpdatedAt: appsUpdatedAt, refetch: refetchApps} = useApps();
    const {
        data: masData,
        isLoading: masLoading,
        error: masError,
        dataUpdatedAt: masUpdatedAt,
        refetch: refetchMAS
    } = useMAS();
    const {
        data: scopesData,
        isLoading: scopesLoading,
        error: scopesError,
        dataUpdatedAt: scopesUpdatedAt,
        refetch: refetchScopes
    } = useScopes();
    const {
        data: tracesData,
        isLoading: tracesLoading,
        dataUpdatedAt: tracesUpdatedAt,
        refetch: refetchTraces
    } = useTraces();

    const isRefreshing = isLoading || masLoading || scopesLoading || tracesLoading;

    const handleRefresh = async () => {
        try {
            await Promise.all([refetchApps(), refetchMAS(), refetchScopes(), refetchTraces()]);
            toast.success('Dashboard refreshed successfully');
        } catch {
            toast.error('Failed to refresh dashboard');
        }
    };

    const totalApps = appsData?.total ?? 0;
    const totalMAS = masData?.length ?? 0;
    const totalScopes = Array.isArray(scopesData) ? scopesData.length : 0;

    const lastUpdated = Math.max(appsUpdatedAt, masUpdatedAt, scopesUpdatedAt, tracesUpdatedAt);
    const lastUpdatedLabel = lastUpdated
        ? new Date(lastUpdated).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'})
        : null;

    const allTraces: Trace[] = useMemo(() => {
        if (!tracesData?.items) return [];
        return Object.values(tracesData.items).flat();
    }, [tracesData]);

    const traceStats = useMemo(() => {
        const tokenRequests = allTraces.filter((t) => t.event_type === 'TokenIssuedEvent').length;
        const mcpCalls = allTraces.filter((t) => t.event_type === 'MCPCallStartedEvent');
        const approved = mcpCalls.filter((t) => !t.event.blocked).length;
        const blocked = mcpCalls.filter((t) => t.event.blocked).length;

        const reasonCounts: Partial<Record<BlockingReason, number>> = {};
        mcpCalls
            .filter((t) => t.event.blocked && t.event.blocking_reason)
            .forEach((t) => {
                const r = t.event.blocking_reason!;
                reasonCounts[r] = (reasonCounts[r] ?? 0) + 1;
            });

        const blockReasons = Object.entries(reasonCounts)
            .map(([reason, count]) => ({
                name: BLOCKING_REASON_LABELS[reason as BlockingReason] ?? reason,
                count
            }))
            .sort((a, b) => b.count - a.count);

        const deterministicBlocks = mcpCalls.filter(
            (t) => t.event.blocked && t.event.blocking_type === 'DETERMINISTIC'
        ).length;
        const aiBlocks = mcpCalls.filter((t) => t.event.blocked && t.event.blocking_type === 'AI_POWERED').length;

        return {
            tokenRequests,
            approved,
            blocked,
            totalMcpCalls: mcpCalls.length,
            blockReasons,
            deterministicBlocks,
            aiBlocks
        };
    }, [allTraces]);

    const appTypeData = useMemo(() => {
        const items = appsData?.items ?? [];
        const counts = {agent: 0, client: 0, mcp_server: 0};
        items.forEach((app) => {
            counts[app.type] = (counts[app.type] ?? 0) + 1;
        });
        return [
            {name: 'Client', value: counts.client, color: '#22c55e'},
            {name: 'Agent', value: counts.agent, color: '#3b82f6'},
            {name: 'MCP Server', value: counts.mcp_server, color: '#a855f7'}
        ].filter((d) => d.value > 0);
    }, [appsData]);

    const mcpDonutData = useMemo(
        () =>
            [
                {name: 'Approved', value: traceStats.approved, color: '#22c55e'},
                {name: 'Blocked', value: traceStats.blocked, color: '#ef4444'}
            ].filter((d) => d.value > 0),
        [traceStats]
    );

    const blockTypeData = useMemo(
        () =>
            [
                {name: 'Deterministic', value: traceStats.deterministicBlocks, color: '#f97316'},
                {name: 'AI-Powered', value: traceStats.aiBlocks, color: '#a855f7'}
            ].filter((d) => d.value > 0),
        [traceStats]
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                    <p className="text-muted-foreground">Overview of your Zero Trust Architecture</p>
                </div>
                <div className="flex items-center gap-3">
                    {lastUpdatedLabel && (
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            <RefreshCw className="h-3 w-3" />
                            <span>Updated {lastUpdatedLabel}</span>
                        </div>
                    )}
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="outline"
                                size="icon"
                                onClick={handleRefresh}
                                disabled={isRefreshing}
                                className="cursor-pointer"
                                aria-label="Refresh dashboard"
                            >
                                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Refresh</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            </div>

            {/* Stat cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => navigate('/mas')}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Multi-Agent Systems</CardTitle>
                        <Network className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        {masLoading ? (
                            <Skeleton className="h-8 w-16" />
                        ) : masError ? (
                            <div className="text-sm text-destructive">Error</div>
                        ) : (
                            <div className="text-2xl font-bold">{totalMAS}</div>
                        )}
                        <p className="text-xs text-muted-foreground">Configured MAS</p>
                    </CardContent>
                </Card>

                <Card
                    className="cursor-pointer hover:bg-accent transition-colors"
                    onClick={() => navigate('/applications')}
                >
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
                        <AppWindow className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <Skeleton className="h-8 w-16" />
                        ) : error ? (
                            <div className="text-sm text-destructive">Error</div>
                        ) : (
                            <div className="text-2xl font-bold">{totalApps}</div>
                        )}
                        <p className="text-xs text-muted-foreground">Agents, Clients & MCP Servers</p>
                    </CardContent>
                </Card>

                <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => navigate('/scopes')}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Scopes</CardTitle>
                        <Tags className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        {scopesLoading ? (
                            <Skeleton className="h-8 w-16" />
                        ) : scopesError ? (
                            <div className="text-sm text-destructive">Error</div>
                        ) : (
                            <div className="text-2xl font-bold">{totalScopes}</div>
                        )}
                        <p className="text-xs text-muted-foreground">Authorization scopes</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Authorization Requests</CardTitle>
                        <Lock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        {tracesLoading ? (
                            <Skeleton className="h-8 w-16" />
                        ) : (
                            <div className="text-2xl font-bold">{traceStats.tokenRequests}</div>
                        )}
                        <p className="text-xs text-muted-foreground">
                            {traceStats.totalMcpCalls > 0
                                ? `${traceStats.approved} approved · ${traceStats.blocked} blocked`
                                : 'Token requests issued'}
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Charts row */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Card>
                    <CardHeader>
                        <CardTitle>Applications by Type</CardTitle>
                        <CardDescription>Breakdown of registered application types</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <DonutChart
                            data={appTypeData}
                            loading={isLoading}
                            emptyIcon={<AppWindow className="h-8 w-8 opacity-40" />}
                            emptyText="No applications registered"
                            unit="app"
                        />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>MCP Tool Calls</CardTitle>
                        <CardDescription>Approved vs blocked tool call decisions</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <DonutChart
                            data={mcpDonutData}
                            loading={tracesLoading}
                            emptyIcon={<Shield className="h-8 w-8 opacity-40" />}
                            emptyText="No tool calls recorded yet"
                            unit="call"
                        />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Block Type</CardTitle>
                        <CardDescription>Deterministic vs AI-powered blocks</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <DonutChart
                            data={blockTypeData}
                            loading={tracesLoading}
                            emptyIcon={<Shield className="h-8 w-8 opacity-40" />}
                            emptyText="No blocked calls recorded yet"
                            unit="block"
                        />
                    </CardContent>
                </Card>
            </div>

            {/* Block reasons bar chart — only shown when there's data */}
            {(tracesLoading || traceStats.blockReasons.length > 0) && (
                <Card>
                    <CardHeader>
                        <CardTitle>Block Reasons</CardTitle>
                        <CardDescription>Why tool calls were blocked by the authorization server</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {tracesLoading ? (
                            <div className="space-y-3">
                                {Array.from({length: 3}).map((_, i) => (
                                    <Skeleton key={i} className="w-full h-8" />
                                ))}
                            </div>
                        ) : (
                            <div style={{height: `${traceStats.blockReasons.length * 48 + 16}px`}}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart
                                        data={traceStats.blockReasons}
                                        layout="vertical"
                                        margin={{left: 8, right: 24, top: 4, bottom: 4}}
                                    >
                                        <CartesianGrid
                                            strokeDasharray="3 3"
                                            stroke="rgba(204,204,220,0.1)"
                                            horizontal={false}
                                        />
                                        <XAxis
                                            type="number"
                                            allowDecimals={false}
                                            tick={{fill: '#8b8fa8', fontSize: 11}}
                                            axisLine={false}
                                            tickLine={false}
                                        />
                                        <YAxis
                                            type="category"
                                            dataKey="name"
                                            width={140}
                                            tick={{fill: '#ccccdc', fontSize: 11}}
                                            axisLine={false}
                                            tickLine={false}
                                        />
                                        <ChartTooltip
                                            {...CHART_TOOLTIP_STYLE}
                                            formatter={(value: number) => [value, 'blocked calls']}
                                        />
                                        <Bar
                                            dataKey="count"
                                            name="Blocked calls"
                                            fill="#ef4444"
                                            radius={[0, 4, 4, 0]}
                                            barSize={14}
                                        />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
