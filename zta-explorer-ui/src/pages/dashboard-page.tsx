import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Skeleton} from '@/components/ui/skeleton';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Shield, Lock, AppWindow, Network, Tags, RefreshCw} from 'lucide-react';
import {useApps} from '@/hooks/use-apps';
import {useMAS} from '@/hooks/use-mas';
import {useScopes} from '@/hooks/use-scopes';
import {useState, useMemo} from 'react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {PieChart, Pie, Cell, Tooltip as ChartTooltip, ResponsiveContainer} from 'recharts';

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

    const isRefreshing = isLoading || masLoading || scopesLoading;
    const handleRefresh = async () => {
        try {
            await Promise.all([refetchApps(), refetchMAS(), refetchScopes()]);
            toast.success('Dashboard refreshed successfully');
        } catch {
            toast.error('Failed to refresh dashboard');
        }
    };
    const totalApps = appsData?.total ?? 0;
    const totalMAS = masData?.length ?? 0;
    const totalScopes = Array.isArray(scopesData) ? scopesData.length : 0;

    const lastUpdated = Math.max(appsUpdatedAt, masUpdatedAt, scopesUpdatedAt);
    const lastUpdatedLabel = lastUpdated
        ? new Date(lastUpdated).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'})
        : null;

    // Generate random stats (these would come from real endpoints in production)
    const [authRequests] = useState(() => Math.floor(Math.random() * 500) + 100);

    const appTypeData = useMemo(() => {
        const items = appsData?.items ?? [];
        const counts = {agent: 0, client: 0, mcp_server: 0};
        items.forEach((app) => {
            counts[app.type] = (counts[app.type] ?? 0) + 1;
        });
        return [
            {name: 'Agent', value: counts.agent, color: '#6e9fff'},
            {name: 'Client', value: counts.client, color: '#3d71d9'},
            {name: 'MCP Server', value: counts.mcp_server, color: '#5794f2'}
        ].filter((d) => d.value > 0);
    }, [appsData]);

    return (
        <div className="space-y-6">
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

            <div>
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
                    <Card
                        className="cursor-pointer hover:bg-accent transition-colors"
                        onClick={() => navigate('/scopes')}
                    >
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
                    <Card className="border-dashed">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Authorization Requests</CardTitle>
                            <Lock className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{authRequests}</div>
                            <p className="text-xs text-muted-foreground">Coming soon</p>
                        </CardContent>
                    </Card>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
                {/* Apps by type chart */}
                <Card>
                    <CardHeader>
                        <CardTitle>Applications by Type</CardTitle>
                        <CardDescription>Breakdown of registered application types</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="flex items-center justify-center h-[200px]">
                                <Skeleton className="h-[160px] w-[160px] rounded-full" />
                            </div>
                        ) : appTypeData.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-[200px] gap-3 text-muted-foreground">
                                <AppWindow className="h-8 w-8 opacity-40" />
                                <p className="text-sm">No applications registered</p>
                            </div>
                        ) : (
                            <div className="flex items-center justify-center gap-8">
                                <div className="w-[160px] h-[160px] flex-shrink-0">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={appTypeData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={48}
                                                outerRadius={72}
                                                paddingAngle={appTypeData.length > 1 ? 3 : 0}
                                                dataKey="value"
                                            >
                                                {appTypeData.map((entry) => (
                                                    <Cell key={entry.name} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <ChartTooltip
                                                contentStyle={{
                                                    backgroundColor: '#22252b',
                                                    border: '1px solid rgba(204,204,220,0.2)',
                                                    borderRadius: '6px',
                                                    fontSize: '12px'
                                                }}
                                                itemStyle={{color: '#ccccdc'}}
                                                labelStyle={{color: '#ccccdc'}}
                                                formatter={(value: number, name: string) => [value, name]}
                                            />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                                <div className="flex flex-col gap-3">
                                    {appTypeData.map((entry) => {
                                        const total = appTypeData.reduce((s, d) => s + d.value, 0);
                                        const pct = Math.round((entry.value / total) * 100);
                                        return (
                                            <div key={entry.name} className="flex items-center gap-2.5">
                                                <span
                                                    className="h-2.5 w-2.5 rounded-full flex-shrink-0"
                                                    style={{backgroundColor: entry.color}}
                                                />
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium leading-none">
                                                        {entry.name}
                                                    </span>
                                                    <span className="text-xs text-muted-foreground mt-1">
                                                        {entry.value} {entry.value === 1 ? 'app' : 'apps'} · {pct}%
                                                    </span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Welcome / quick nav */}
                <Card>
                    <CardHeader>
                        <CardTitle>Welcome to ZTA Explorer</CardTitle>
                        <CardDescription>Zero Trust Architecture Identity & Authorization Management</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground">
                            Overview of your authentication and authorization infrastructure. Navigate using the sidebar
                            or shortcuts below:
                        </p>
                        <ul className="space-y-2 text-sm">
                            <li
                                className="flex items-start gap-2 cursor-pointer hover:bg-accent p-2 -m-2 rounded transition-colors"
                                onClick={() => navigate('/mas')}
                            >
                                <Network className="h-4 w-4 mt-0.5 text-primary" />
                                <div>
                                    <strong>Multi-Agent Systems:</strong> Configure and orchestrate multi-agent
                                    workflows
                                </div>
                            </li>
                            <li
                                className="flex items-start gap-2 cursor-pointer hover:bg-accent p-2 -m-2 rounded transition-colors"
                                onClick={() => navigate('/applications')}
                            >
                                <AppWindow className="h-4 w-4 mt-0.5 text-primary" />
                                <div>
                                    <strong>Applications:</strong> Manage your agents, clients, and MCP servers
                                </div>
                            </li>
                            <li
                                className="flex items-start gap-2 cursor-pointer hover:bg-accent p-2 -m-2 rounded transition-colors"
                                onClick={() => navigate('/scopes')}
                            >
                                <Tags className="h-4 w-4 mt-0.5 text-primary" />
                                <div>
                                    <strong>Scopes:</strong> Manage authorization scopes for Multi-Agent Systems
                                </div>
                            </li>
                            <li
                                className="flex items-start gap-2 cursor-pointer hover:bg-accent p-2 -m-2 rounded transition-colors"
                                onClick={() => navigate('/settings')}
                            >
                                <Shield className="h-4 w-4 mt-0.5 text-primary" />
                                <div>
                                    <strong>Settings:</strong> Configure your authentication policies and preferences
                                </div>
                            </li>
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
