import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Shield, Lock, Activity, Loader2, AppWindow, Network} from 'lucide-react';
import {useApps} from '@/hooks/use-apps';
import {useMAS} from '@/hooks/use-mas';
import {useState} from 'react';
import {useNavigate} from 'react-router-dom';

export function DashboardPage() {
    const navigate = useNavigate();
    const {data: appsData, isLoading, error} = useApps();
    const {data: masData, isLoading: masLoading, error: masError} = useMAS();
    const totalApps = appsData?.total ?? 0;
    const totalMAS = masData?.length ?? 0;

    // Generate random stats (these would come from real endpoints in production)
    const [activeSessions] = useState(() => Math.floor(Math.random() * 50) + 10);
    const [authRequests] = useState(() => Math.floor(Math.random() * 500) + 100);

    return (
        <>
            <div>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                    <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => navigate('/mas')}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Multi-Agent Systems</CardTitle>
                            <Network className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            {masLoading ? (
                                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
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
                                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                            ) : error ? (
                                <div className="text-sm text-destructive">Error</div>
                            ) : (
                                <div className="text-2xl font-bold">{totalApps}</div>
                            )}
                            <p className="text-xs text-muted-foreground">Agents, Clients & MCP Servers</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                            <Activity className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{activeSessions}</div>
                            <p className="text-xs text-muted-foreground">Currently authenticated</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Authorization Requests</CardTitle>
                            <Lock className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{authRequests}</div>
                            <p className="text-xs text-muted-foreground">Last 24 hours</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Security Status</CardTitle>
                            <Shield className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-green-600">Secure</div>
                            <p className="text-xs text-muted-foreground">All systems operational</p>
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
                            <li className="flex items-start gap-2 p-2 -m-2">
                                <Shield className="h-4 w-4 mt-0.5 text-primary" />
                                <div>
                                    <strong>Settings:</strong> Configure your authentication policies and preferences
                                </div>
                            </li>
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </>
    );
}
