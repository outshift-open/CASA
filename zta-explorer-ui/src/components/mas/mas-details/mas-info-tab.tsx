import {useMASApps} from '@/hooks/use-mas';
import {MASAppsTable, MASGraphView} from '@/components/mas';
import {Tabs, TabsList, TabsTrigger, TabsContent} from '@/components/ui/tabs';
import {Card, CardContent, CardHeader, CardTitle, CardDescription} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {Table, Network, Plus, Copy, Download, Bot, AppWindow, Server, CheckCircle2} from 'lucide-react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {useMemo} from 'react';
import type {MAS} from '@/types/mas.types';
import type {AppType} from '@/types/app.types';

interface MASInfoTabProps {
    mas: MAS;
}

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agents',
    client: 'Clients',
    mcp_server: 'MCP Servers'
};

const APP_TYPE_ICONS: Record<AppType, React.ComponentType<{className?: string}>> = {
    agent: Bot,
    client: AppWindow,
    mcp_server: Server
};

const APP_TYPE_COLORS: Record<AppType, string> = {
    agent: 'text-green-600 dark:text-green-400',
    client: 'text-blue-600 dark:text-blue-400',
    mcp_server: 'text-purple-600 dark:text-purple-400'
};

function formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)} months ago`;
    return `${Math.floor(diffInSeconds / 31536000)} years ago`;
}

export function MASInfoTab({mas}: MASInfoTabProps) {
    const navigate = useNavigate();
    const {data: apps, isLoading: appsLoading, error: appsError} = useMASApps(mas.id);

    const stats = useMemo(() => {
        if (!apps) return {byType: {agent: 0, client: 0, mcp_server: 0}, totalTools: 0};

        const byType = apps.reduce(
            (acc, app) => {
                acc[app.type] = (acc[app.type] || 0) + 1;
                return acc;
            },
            {agent: 0, client: 0, mcp_server: 0} as Record<AppType, number>
        );

        const totalTools = apps.reduce((sum, app) => sum + (app.tools?.length || 0), 0);

        return {byType, totalTools};
    }, [apps]);

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`${label} copied to clipboard`);
    };

    const exportConfig = () => {
        const config = {
            mas: {
                id: mas.id,
                name: mas.name,
                created_at: mas.created_at
            },
            apps: apps?.map((app) => ({
                id: app.id,
                name: app.name,
                type: app.type,
                base_url: app.base_url,
                tools: app.tools
            }))
        };

        const blob = new Blob([JSON.stringify(config, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${mas.name}-config.json`;
        link.click();
        URL.revokeObjectURL(url);
        toast.success('Configuration exported successfully');
    };

    return (
        <div className="space-y-6">
            {/* Basic Info Card */}
            <Card>
                <CardHeader>
                    <div className="flex items-start justify-between">
                        <div className="space-y-1">
                            <CardTitle>Basic Information</CardTitle>
                            <CardDescription>Core details about this Multi-Agent System</CardDescription>
                        </div>
                        <Button variant="outline" size="sm" onClick={exportConfig} className="cursor-pointer">
                            <Download className="mr-2 h-3 w-3" />
                            Export Config
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-6 md:grid-cols-2">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <p className="text-sm font-medium text-muted-foreground">Name</p>
                                <p className="text-base font-semibold">{mas.name}</p>
                            </div>
                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium text-muted-foreground">MAS ID</p>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => copyToClipboard(mas.id, 'MAS ID')}
                                        className="cursor-pointer h-6 px-2"
                                    >
                                        <Copy className="h-3 w-3" />
                                    </Button>
                                </div>
                                <p className="text-xs font-mono bg-muted px-2 py-1 rounded">{mas.id}</p>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <p className="text-sm font-medium text-muted-foreground">Created</p>
                                <div>
                                    <p className="text-base">{formatRelativeTime(mas.created_at)}</p>
                                    <p className="text-xs text-muted-foreground">
                                        {new Date(mas.created_at).toLocaleString()}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Quick Stats Dashboard */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="py-3">
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Total Applications</p>
                                <p className="text-2xl font-bold">{apps?.length || 0}</p>
                            </div>
                            <Network className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>

                {Object.entries(stats.byType).map(([type, count]) => {
                    const Icon = APP_TYPE_ICONS[type as AppType];
                    const colorClass = APP_TYPE_COLORS[type as AppType];
                    return (
                        <Card key={type} className="py-3">
                            <CardContent className="p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-muted-foreground">
                                            {APP_TYPE_LABELS[type as AppType]}
                                        </p>
                                        <p className="text-2xl font-bold">{count}</p>
                                    </div>
                                    <Icon className={`h-8 w-8 ${colorClass}`} />
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            {/* Additional Stats */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card className="py-3">
                    <CardContent className="p-4">
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                                <p className="text-sm font-medium text-muted-foreground">Total Tools</p>
                            </div>
                            <p className="text-2xl font-bold">{stats.totalTools}</p>
                            <p className="text-xs text-muted-foreground">
                                Across {apps?.length || 0} application{apps?.length !== 1 ? 's' : ''}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="py-3">
                    <CardContent className="p-4">
                        <div className="space-y-2">
                            <p className="text-sm font-medium text-muted-foreground">Average Tools per App</p>
                            <p className="text-2xl font-bold">
                                {apps && apps.length > 0 ? (stats.totalTools / apps.length).toFixed(1) : '0'}
                            </p>
                            <p className="text-xs text-muted-foreground">Mean distribution</p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="py-3">
                    <CardContent className="p-4">
                        <div className="space-y-2">
                            <p className="text-sm font-medium text-muted-foreground">Status</p>
                            <div className="flex items-center gap-2">
                                <Badge variant="default" className="text-sm">
                                    <CheckCircle2 className="mr-1 h-3 w-3" />
                                    Active
                                </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground">All systems operational</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Applications Section */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-lg font-semibold">Applications</p>
                        <p className="text-sm text-muted-foreground">
                            {apps?.length || 0} application{apps?.length !== 1 ? 's' : ''} configured
                        </p>
                    </div>
                    <Button
                        onClick={() => navigate(`/apps/create?mas_id=${mas.id}`)}
                        size="sm"
                        className="cursor-pointer"
                    >
                        <Plus className="mr-2 h-4 w-4" />
                        Add Application
                    </Button>
                </div>

                {appsLoading ? (
                    <Card>
                        <CardContent className="pt-6">
                            <p className="text-sm text-muted-foreground text-center py-8">Loading applications...</p>
                        </CardContent>
                    </Card>
                ) : appsError ? (
                    <Card>
                        <CardContent className="pt-6">
                            <p className="text-sm text-destructive text-center py-8">Error loading applications</p>
                        </CardContent>
                    </Card>
                ) : apps && apps.length > 0 ? (
                    <Tabs defaultValue="table" className="w-full">
                        <TabsList>
                            <TabsTrigger value="table">
                                <Table className="mr-2 h-4 w-4" />
                                Table
                            </TabsTrigger>
                            <TabsTrigger value="graph">
                                <Network className="mr-2 h-4 w-4" />
                                Graph
                            </TabsTrigger>
                        </TabsList>
                        <TabsContent value="table" className="mt-4">
                            <MASAppsTable apps={apps} />
                        </TabsContent>
                        <TabsContent value="graph" className="mt-4">
                            <MASGraphView mas={mas} apps={apps} />
                        </TabsContent>
                    </Tabs>
                ) : (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex flex-col items-center justify-center py-8 text-center">
                                <div className="rounded-full bg-muted p-3 mb-4">
                                    <Plus className="h-6 w-6 text-muted-foreground" />
                                </div>
                                <h3 className="text-lg font-semibold mb-2">No Applications Yet</h3>
                                <p className="text-sm text-muted-foreground mb-6 max-w-sm">
                                    This Multi-Agent System doesn't have any applications associated with it yet. Create
                                    your first application to get started.
                                </p>
                                <Button onClick={() => navigate('/apps/create')}>
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create Application
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
