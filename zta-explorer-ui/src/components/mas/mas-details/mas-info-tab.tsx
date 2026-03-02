import {useMASApps} from '@/hooks/use-mas';
import {useMASScopes} from '@/hooks/use-scopes';
import {Card, CardContent, CardHeader, CardTitle, CardDescription} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {Network, Copy, Download, Bot, AppWindow, Server, CheckCircle2, Tags} from 'lucide-react';
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
    const {data: apps} = useMASApps(mas.id);
    const {data: scopes} = useMASScopes(mas.id);

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
            <div className="grid gap-4 md:grid-cols-4">
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
                            <div className="flex items-center gap-2">
                                <Tags className="h-4 w-4 text-primary" />
                                <p className="text-sm font-medium text-muted-foreground">Total Scopes</p>
                            </div>
                            <p className="text-2xl font-bold">{scopes?.length || 0}</p>
                            <p className="text-xs text-muted-foreground">Authorization scopes</p>
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
        </div>
    );
}
