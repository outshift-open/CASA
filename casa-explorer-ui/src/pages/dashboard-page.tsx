import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Skeleton} from '@/components/ui/skeleton';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Separator} from '@/components/ui/separator';
import {Shield, Activity, ShieldAlert, Network, Tags, RefreshCw, HelpCircle, Cpu, Sparkles} from 'lucide-react';
import {useMAS} from '@/hooks/use-mas';
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

const BLOCKING_REASON_DESCRIPTIONS: Partial<Record<BlockingReason, string>> = {
    no_llm_calls_made_by_app: 'The app made no LLM calls before requesting tool access',
    tool_not_selected_by_llm: 'Requested MCP Server Tool was not selected by the LLM',
    tool_intent_mismatch: "MCP Server Tool choice doesn't match the intention of original input",
    tool_parameters_mismatch: 'Requested MCP Server Tool Parameters are different from those selected by the LLM',
    modified_mcp_tool_defs: 'The LLM received modified MCP Server Tool Definitions',
    insufficient_scope: 'Token does not have the required scope for this tool'
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
    data: {name: string; value: number; color: string; icon?: React.ElementType}[];
    loading: boolean;
    emptyIcon: React.ReactNode;
    emptyText: string;
    unit: string;
    onSegmentClick?: (entry: {name: string; value: number; color: string}) => void;
}

function DonutChart({data, loading, emptyIcon, emptyText, unit, onSegmentClick}: DonutChartProps) {
    if (loading) {
        return (
            <div className="flex items-center justify-center h-[120px]">
                <Skeleton className="h-[100px] w-[100px] rounded-full" />
            </div>
        );
    }
    if (data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-[120px] gap-3 text-muted-foreground w-full">
                {emptyIcon}
                <p className="text-sm text-center">{emptyText}</p>
            </div>
        );
    }
    const total = data.reduce((s, d) => s + d.value, 0);
    return (
        <div className="flex items-center justify-center gap-6 h-full">
            <div className="w-[120px] h-[120px] flex-shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={36}
                            outerRadius={54}
                            paddingAngle={data.length > 1 ? 3 : 0}
                            dataKey="value"
                            onClick={
                                onSegmentClick
                                    ? (d) => onSegmentClick(d as {name: string; value: number; color: string})
                                    : undefined
                            }
                        >
                            {data.map((entry) => (
                                <Cell
                                    key={entry.name}
                                    fill={entry.color}
                                    style={onSegmentClick ? {cursor: 'pointer'} : undefined}
                                />
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
                        <div
                            key={entry.name}
                            className={`flex items-center gap-2.5 group ${onSegmentClick ? 'cursor-pointer' : ''}`}
                            onClick={() => onSegmentClick?.(entry)}
                        >
                            {entry.icon ? (
                                <entry.icon className="h-3.5 w-3.5 flex-shrink-0" style={{color: entry.color}} />
                            ) : (
                                <span
                                    className="h-2.5 w-2.5 rounded-full flex-shrink-0"
                                    style={{backgroundColor: entry.color}}
                                />
                            )}
                            <div className="flex flex-col">
                                <span
                                    className={`text-sm font-medium leading-none ${onSegmentClick ? 'group-hover:underline' : ''}`}
                                >
                                    {entry.name}
                                </span>
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
    const {
        data: masData,
        isLoading: masLoading,
        error: masError,
        dataUpdatedAt: masUpdatedAt,
        refetch: refetchMAS
    } = useMAS();
    const {
        data: tracesData,
        isLoading: tracesLoading,
        dataUpdatedAt: tracesUpdatedAt,
        refetch: refetchTraces
    } = useTraces(undefined, 1, 100, true);

    const isRefreshing = masLoading || tracesLoading;

    const handleRefresh = async () => {
        try {
            await Promise.all([refetchMAS(), refetchTraces()]);
            toast.success('Dashboard refreshed successfully');
        } catch {
            toast.error('Failed to refresh dashboard');
        }
    };

    const totalMAS = masData?.length ?? 0;

    const lastUpdated = Math.max(masUpdatedAt, tracesUpdatedAt);
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
        const allowed = mcpCalls.filter((t) => !t.event.blocked).length;
        const denied = mcpCalls.filter((t) => t.event.blocked).length;

        const reasonCounts: Partial<Record<BlockingReason, number>> = {};
        mcpCalls
            .filter((t) => t.event.blocked && t.event.blocking_reason)
            .forEach((t) => {
                const r = t.event.blocking_reason!;
                reasonCounts[r] = (reasonCounts[r] ?? 0) + 1;
            });

        const blockReasons = Object.entries(reasonCounts)
            .map(([reason, count]) => ({
                reason,
                name: BLOCKING_REASON_LABELS[reason as BlockingReason] ?? reason,
                description: BLOCKING_REASON_DESCRIPTIONS[reason as BlockingReason] ?? '',
                count
            }))
            .sort((a, b) => b.count - a.count);

        const deterministicBlocks = mcpCalls.filter(
            (t) => t.event.blocked && t.event.blocking_type === 'DETERMINISTIC'
        ).length;
        const aiBlocks = mcpCalls.filter((t) => t.event.blocked && t.event.blocking_type === 'AI_POWERED').length;

        return {
            tokenRequests,
            allowed,
            denied,
            totalMcpCalls: mcpCalls.length,
            blockReasons,
            deterministicBlocks,
            aiBlocks
        };
    }, [allTraces]);

    const mcpDonutData = useMemo(
        () =>
            [
                {name: 'Allowed', value: traceStats.allowed, color: '#22c55e'},
                {name: 'Denied', value: traceStats.denied, color: '#ef4444'}
            ].filter((d) => d.value > 0),
        [traceStats]
    );

    const blockTypeData = useMemo(
        () =>
            [
                {name: 'Deterministic', value: traceStats.deterministicBlocks, color: '#f97316', icon: Cpu},
                {name: 'Semantic', value: traceStats.aiBlocks, color: '#38bdf8', icon: Sparkles}
            ].filter((d) => d.value > 0),
        [traceStats]
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                    <p className="text-muted-foreground">Overview of your CASA (Continuous Agent Semantic Authorization)</p>
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
                        <TooltipContent className="max-w-[180px]">
                            <p>Refresh</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            </div>

            {/* Stat cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {/* Auth requests — donut: Allowed vs Denied */}
                <Card className="gap-0 flex flex-col py-3">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 py-4">
                        <div className="flex items-center gap-2">
                            <Activity className="h-4 w-4 text-muted-foreground" />
                            <CardTitle className="text-sm font-medium">Auth Requests</CardTitle>
                        </div>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-[180px]">
                                <p className="text-center">
                                    OAuth2 token requests issued to agents, showing allowed vs denied MCP tool calls
                                </p>
                            </TooltipContent>
                        </Tooltip>
                    </CardHeader>
                    <div className="px-4">
                        <Separator />
                    </div>
                    <CardContent className="flex-1 flex items-center justify-center px-4 py-4">
                        <DonutChart
                            data={mcpDonutData}
                            loading={tracesLoading}
                            emptyIcon={<Shield className="h-8 w-8 opacity-40" />}
                            emptyText="No tool calls recorded yet"
                            unit="call"
                            onSegmentClick={(entry) => {
                                const auth = entry.name === 'Allowed' ? 'allowed' : 'denied';
                                navigate(`/auth-requests?auth=${auth}&from=dashboard`);
                            }}
                        />
                    </CardContent>
                </Card>

                {/* Deny type — donut: Deterministic vs Semantic */}
                <Card className="gap-0 flex flex-col py-3">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                        <div className="flex items-center gap-2">
                            <ShieldAlert className="h-4 w-4 text-muted-foreground" />
                            <CardTitle className="text-sm font-medium">Deny Type</CardTitle>
                        </div>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-[180px]">
                                <p className="text-center">
                                    How denied calls were caught — deterministic rules (scope, params) vs semantic
                                    AI-powered intent verification
                                </p>
                            </TooltipContent>
                        </Tooltip>
                    </CardHeader>
                    <div className="px-4">
                        <Separator />
                    </div>
                    <CardContent className="flex-1 flex items-center justify-center px-4 py-4">
                        <DonutChart
                            data={blockTypeData}
                            loading={tracesLoading}
                            emptyIcon={<Shield className="h-8 w-8 opacity-40" />}
                            emptyText="No denied calls recorded yet"
                            unit="block"
                            onSegmentClick={(entry) => {
                                const denyType = entry.name === 'Semantic' ? 'AI_POWERED' : 'DETERMINISTIC';
                                navigate(`/auth-requests?auth=denied&denyType=${denyType}&from=dashboard`);
                            }}
                        />
                    </CardContent>
                </Card>

                {/* Multi-Agent Systems — number */}
                <Card
                    className="gap-0 flex flex-col cursor-pointer hover:bg-accent transition-colors py-3"
                    onClick={() => navigate('/mas')}
                >
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                        <div className="flex items-center gap-2">
                            <Network className="h-4 w-4 text-muted-foreground" />
                            <CardTitle className="text-sm font-medium">Multi-Agent Systems</CardTitle>
                        </div>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-[180px]">
                                <p className="text-center">
                                    Multi-Agent Systems grouping agents, clients, and MCP servers under a shared
                                    authorization policy
                                </p>
                            </TooltipContent>
                        </Tooltip>
                    </CardHeader>
                    <div className="px-4">
                        <Separator />
                    </div>
                    <CardContent className="pt-4 px-4 pb-4">
                        {masLoading ? (
                            <Skeleton className="h-8 w-16" />
                        ) : masError ? (
                            <div className="text-sm text-destructive">Error</div>
                        ) : (
                            <div className="text-2xl font-bold">{totalMAS}</div>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">Configured MAS</p>
                    </CardContent>
                </Card>

                {/* Auth scopes — coming soon */}
                <Card className="gap-0 flex flex-col opacity-50 cursor-not-allowed py-3">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                        <div className="flex items-center gap-2">
                            <Tags className="h-4 w-4 text-muted-foreground" />
                            <CardTitle className="text-sm font-medium">Auth Scopes</CardTitle>
                        </div>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-[180px]">
                                <p className="text-center">
                                    Fine-grained OAuth2 scopes controlling which MCP tools each agent is permitted to
                                    call
                                </p>
                            </TooltipContent>
                        </Tooltip>
                    </CardHeader>
                    <div className="px-4">
                        <Separator />
                    </div>
                    <CardContent className="pt-4 px-4 pb-4">
                        <div className="text-2xl font-bold text-muted-foreground">—</div>
                        <p className="text-xs text-muted-foreground mt-1">Coming soon</p>
                    </CardContent>
                </Card>
            </div>

            {/* Deny reasons bar chart */}
            <Card className="gap-0 py-3">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                    <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-muted-foreground" />
                        <CardTitle className="text-sm font-medium">Deny Reasons</CardTitle>
                    </div>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[180px]">
                            <p className="text-center">
                                Breakdown of why MCP tool calls were denied by the authorization server
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </CardHeader>
                <div className="px-4">
                    <Separator />
                </div>
                <CardContent className="pt-4 px-4 pb-4">
                    {tracesLoading ? (
                        <div className="space-y-3">
                            {Array.from({length: 3}).map((_, i) => (
                                <Skeleton key={i} className="w-full h-8" />
                            ))}
                        </div>
                    ) : traceStats.blockReasons.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-[200px] gap-3 text-muted-foreground">
                            <Shield className="h-8 w-8 opacity-40" />
                            <p className="text-sm">No denied calls recorded yet</p>
                        </div>
                    ) : (
                        <>
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
                                            width={180}
                                            tick={{fill: '#ccccdc', fontSize: 11}}
                                            axisLine={false}
                                            tickLine={false}
                                        />
                                        <ChartTooltip
                                            content={({active, payload}) => {
                                                if (!active || !payload?.length) return null;
                                                const d = payload[0].payload as {
                                                    name: string;
                                                    description: string;
                                                    count: number;
                                                };
                                                return (
                                                    <div
                                                        style={CHART_TOOLTIP_STYLE.contentStyle}
                                                        className="px-3 py-2 max-w-[260px]"
                                                    >
                                                        <p className="font-medium text-[#ccccdc] mb-1">{d.name}</p>
                                                        {d.description && (
                                                            <p className="text-[11px] text-[#8b8fa8] mb-1.5 leading-snug">
                                                                {d.description}
                                                            </p>
                                                        )}
                                                        <p className="text-[#ccccdc]">
                                                            {d.count} denied {d.count === 1 ? 'call' : 'calls'}
                                                        </p>
                                                    </div>
                                                );
                                            }}
                                        />
                                        <Bar
                                            dataKey="count"
                                            name="Denied calls"
                                            fill="#ef4444"
                                            radius={[0, 4, 4, 0]}
                                            barSize={14}
                                            style={{cursor: 'pointer'}}
                                            onClick={(d) =>
                                                navigate(
                                                    `/auth-requests?auth=denied&q=${encodeURIComponent((d as {reason: string}).reason)}`
                                                )
                                            }
                                        />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="mt-3">
                                <Separator className="mb-3" />
                                <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                                    <span className="text-xs text-muted-foreground">Auth Requests</span>
                                    {traceStats.blockReasons.map((r) => (
                                        <button
                                            key={r.reason}
                                            type="button"
                                            className="flex items-center gap-1 text-xs text-primary hover:underline cursor-pointer"
                                            onClick={() =>
                                                navigate(
                                                    `/auth-requests?auth=denied&q=${encodeURIComponent(r.reason)}&from=dashboard`
                                                )
                                            }
                                        >
                                            {r.name}
                                            <span className="text-muted-foreground">({r.count})</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
