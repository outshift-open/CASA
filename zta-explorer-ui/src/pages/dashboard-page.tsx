import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Skeleton} from '@/components/ui/skeleton';
import {Shield, Lock, AppWindow, Network, Tags, RefreshCw} from 'lucide-react';
import {useApps} from '@/hooks/use-apps';
import {useMAS} from '@/hooks/use-mas';
import {useScopes} from '@/hooks/use-scopes';
import {useState} from 'react';
import {useNavigate} from 'react-router-dom';

export function DashboardPage() {
    const navigate = useNavigate();
    const {data: appsData, isLoading, error, dataUpdatedAt: appsUpdatedAt} = useApps();
    const {data: masData, isLoading: masLoading, error: masError, dataUpdatedAt: masUpdatedAt} = useMAS();
    const {
        data: scopesData,
        isLoading: scopesLoading,
        error: scopesError,
        dataUpdatedAt: scopesUpdatedAt
    } = useScopes();
    const totalApps = appsData?.total ?? 0;
    const totalMAS = masData?.length ?? 0;
    const totalScopes = Array.isArray(scopesData) ? scopesData.length : 0;

    const lastUpdated = Math.max(appsUpdatedAt, masUpdatedAt, scopesUpdatedAt);
    const lastUpdatedLabel = lastUpdated
        ? new Date(lastUpdated).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'})
        : null;

    // Generate random stats (these would come from real endpoints in production)
    const [authRequests] = useState(() => Math.floor(Math.random() * 500) + 100);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                    <p className="text-muted-foreground">Overview of your Zero Trust Architecture</p>
                </div>
                {lastUpdatedLabel && (
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <RefreshCw className="h-3 w-3" />
                        <span>Updated {lastUpdatedLabel}</span>
                    </div>
                )}
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

            <div>
                <Card>
                    <CardHeader>
                        <CardTitle>Welcome to ZTA Explorer</CardTitle>
                        <CardDescription>Zero Trust Architecture Identity & Authorization Management</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground">
                            This dashboard provides an overview of your authentication and authorization infrastructure.
                            Use the sidebar to navigate between different sections:
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
