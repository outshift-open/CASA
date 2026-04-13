import {useParams, useNavigate} from 'react-router-dom';
import {useAppById} from '@/hooks/use-apps';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {Input} from '@/components/ui/input';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog';
import {ApiStateHandler} from '@/components/api-state-handler';
import {Network, Copy, Download, Wrench, ExternalLink, Info, Search, Bot, AppWindow, Server} from 'lucide-react';
import {toast} from 'sonner';
import {useState} from 'react';
import type {AppType, Tool} from '@/types/app.types';

function formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)}mo ago`;
    return `${Math.floor(diffInSeconds / 31536000)}y ago`;
}

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agent',
    client: 'Client',
    mcp_server: 'MCP Server'
};

const APP_TYPE_ICONS: Record<AppType, React.ComponentType<{className?: string}>> = {
    agent: Bot,
    client: AppWindow,
    mcp_server: Server
};

const APP_TYPE_COLORS: Record<AppType, string> = {
    agent: 'text-blue-500',
    client: 'text-green-500',
    mcp_server: 'text-purple-500'
};

function safeJsonPretty(raw: string | undefined | null): string {
    if (!raw) return '{}';
    try {
        return JSON.stringify(JSON.parse(raw), null, 2);
    } catch {
        return raw;
    }
}

export function AppDetailPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: app, isLoading, error, refetch} = useAppById(id || '');
    const [activeTab, setActiveTab] = useState('info');
    const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
    const [toolSearch, setToolSearch] = useState('');

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`${label} copied to clipboard`);
    };

    const exportConfig = () => {
        if (!app) return;
        const config = {
            app: {id: app.id, name: app.name, type: app.type, base_url: app.base_url, mas_id: app.mas_id},
            mas: app.mas ? {id: app.mas.id, name: app.mas.name} : null,
            tools: app.tools
        };
        const blob = new Blob([JSON.stringify(config, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${app.name}-config.json`;
        link.click();
        URL.revokeObjectURL(url);
        toast.success('Configuration exported');
    };

    const hasTools = app?.type === 'mcp_server' && (app?.tools?.length ?? 0) > 0;

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Application Details</h1>
                        <p className="text-muted-foreground">View and manage application information</p>
                    </div>
                </div>

                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error || !app}
                    error={error as Error}
                    loadingMessage="Loading application..."
                    errorMessage="Failed to load application. Please try again."
                    onRetry={() => refetch()}
                >
                    {app && (
                        <div className="grid gap-6">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                                    <div className="space-y-2">
                                        <CardTitle>{app.name}</CardTitle>
                                        <CardDescription>Application configuration and tools</CardDescription>
                                    </div>
                                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-auto">
                                        <TabsList>
                                            <TabsTrigger value="info">
                                                <Info className="mr-2 h-4 w-4" />
                                                Info
                                            </TabsTrigger>
                                            {app.type === 'mcp_server' && (
                                                <TabsTrigger value="tools">
                                                    <Wrench className="mr-2 h-4 w-4" />
                                                    Tools
                                                </TabsTrigger>
                                            )}
                                        </TabsList>
                                    </Tabs>
                                </CardHeader>

                                <CardContent>
                                    {activeTab === 'info' && (
                                        <div className="space-y-6">
                                            {/* Metadata row */}
                                            <div className="flex items-start justify-between gap-4">
                                                <div className="grid gap-4 sm:grid-cols-2 flex-1">
                                                    {/* Type */}
                                                    <div className="space-y-1">
                                                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                            Type
                                                        </p>
                                                        <div className="flex items-center gap-2">
                                                            {(() => {
                                                                const Icon = APP_TYPE_ICONS[app.type];
                                                                return (
                                                                    <Icon
                                                                        className={`h-4 w-4 ${APP_TYPE_COLORS[app.type]}`}
                                                                    />
                                                                );
                                                            })()}
                                                            <Badge variant="outline" className="text-xs">
                                                                {APP_TYPE_LABELS[app.type]}
                                                            </Badge>
                                                        </div>
                                                    </div>

                                                    {/* Base URL */}
                                                    <div className="space-y-1">
                                                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                            Base URL
                                                        </p>
                                                        <div className="flex items-center gap-2">
                                                            <code className="text-xs font-mono bg-muted px-2 py-1 rounded truncate max-w-[220px]">
                                                                {app.base_url}
                                                            </code>
                                                            <Button
                                                                variant="ghost"
                                                                size="icon"
                                                                className="h-6 w-6 cursor-pointer flex-shrink-0"
                                                                onClick={() =>
                                                                    copyToClipboard(app.base_url, 'Base URL')
                                                                }
                                                            >
                                                                <Copy className="h-3 w-3" />
                                                            </Button>
                                                        </div>
                                                    </div>

                                                    {/* App ID */}
                                                    <div className="space-y-1">
                                                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                            App ID
                                                        </p>
                                                        <div className="flex items-center gap-2">
                                                            <code className="text-xs font-mono bg-muted px-2 py-1 rounded truncate max-w-[220px]">
                                                                {app.id}
                                                            </code>
                                                            <Button
                                                                variant="ghost"
                                                                size="icon"
                                                                className="h-6 w-6 cursor-pointer flex-shrink-0"
                                                                onClick={() => copyToClipboard(app.id || '', 'App ID')}
                                                            >
                                                                <Copy className="h-3 w-3" />
                                                            </Button>
                                                        </div>
                                                    </div>

                                                    {/* Created */}
                                                    {app.created_at && (
                                                        <div className="space-y-1">
                                                            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                                Created
                                                            </p>
                                                            <div>
                                                                <p className="text-sm font-medium">
                                                                    {formatRelativeTime(app.created_at)}
                                                                </p>
                                                                <p className="text-xs text-muted-foreground">
                                                                    {new Date(app.created_at).toLocaleString()}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* MAS */}
                                                    <div className="space-y-1">
                                                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                            Multi-Agent System
                                                        </p>
                                                        {app.mas ? (
                                                            <div
                                                                className="flex items-center gap-2 cursor-pointer group w-fit"
                                                                onClick={() => navigate(`/mas/${app.mas_id}`)}
                                                            >
                                                                <Network className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                                                <div className="flex flex-col">
                                                                    <span className="text-sm font-medium underline decoration-dotted group-hover:decoration-solid">
                                                                        {app.mas.name}
                                                                    </span>
                                                                    <span className="font-mono text-xs text-muted-foreground">
                                                                        {app.mas.id}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        ) : (
                                                            <p className="text-sm text-muted-foreground">—</p>
                                                        )}
                                                    </div>
                                                </div>

                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={exportConfig}
                                                    className="cursor-pointer flex-shrink-0"
                                                >
                                                    <Download className="mr-2 h-3 w-3" />
                                                    Export
                                                </Button>
                                            </div>
                                        </div>
                                    )}

                                    {activeTab === 'tools' && app.type === 'mcp_server' && (
                                        <div className="space-y-3">
                                            {!hasTools ? (
                                                <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                                                    <Wrench className="h-10 w-10 opacity-40" />
                                                    <div className="text-center">
                                                        <p className="text-sm font-medium">No tools defined</p>
                                                        <p className="text-xs mt-1">
                                                            This MCP server has no tools configured
                                                        </p>
                                                    </div>
                                                </div>
                                            ) : (
                                                <>
                                                    <div className="relative w-1/2">
                                                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                                        <Input
                                                            placeholder="Search tools..."
                                                            value={toolSearch}
                                                            onChange={(e) => setToolSearch(e.target.value)}
                                                            className="pl-9"
                                                        />
                                                    </div>
                                                    <div className="space-y-3">
                                                        {app
                                                            .tools!.filter(
                                                                (t) =>
                                                                    !toolSearch ||
                                                                    t.name
                                                                        .toLowerCase()
                                                                        .includes(toolSearch.toLowerCase()) ||
                                                                    (t.description ?? '')
                                                                        .toLowerCase()
                                                                        .includes(toolSearch.toLowerCase())
                                                            )
                                                            .map((tool) => (
                                                                <div
                                                                    key={tool.id}
                                                                    className="group p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer"
                                                                    onClick={() => setSelectedTool(tool)}
                                                                >
                                                                    <div className="flex items-start gap-4">
                                                                        <div className="flex items-start gap-3 flex-1 min-w-0">
                                                                            <div className="mt-0.5 p-2 rounded-md bg-primary/10 flex-shrink-0">
                                                                                <Wrench className="h-4 w-4 text-primary" />
                                                                            </div>
                                                                            <div className="flex-1 min-w-0">
                                                                                <p className="font-semibold text-foreground">
                                                                                    {tool.name}
                                                                                </p>
                                                                                {tool.description && (
                                                                                    <p className="text-sm text-muted-foreground mt-1">
                                                                                        {tool.description}
                                                                                    </p>
                                                                                )}
                                                                            </div>
                                                                        </div>
                                                                        {tool.scopes && tool.scopes.length > 0 && (
                                                                            <div className="flex-shrink-0 space-y-2">
                                                                                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider text-right">
                                                                                    Required Scopes
                                                                                </p>
                                                                                <div className="flex flex-wrap gap-2 justify-end">
                                                                                    {tool.scopes.map((scope) => (
                                                                                        <button
                                                                                            key={scope.id}
                                                                                            onClick={(e) => {
                                                                                                e.stopPropagation();
                                                                                                navigate(
                                                                                                    `/scopes/${scope.id}`
                                                                                                );
                                                                                            }}
                                                                                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 text-xs font-medium cursor-pointer transition-colors"
                                                                                        >
                                                                                            <span>{scope.name}</span>
                                                                                            <ExternalLink className="h-3 w-3 opacity-70" />
                                                                                        </button>
                                                                                    ))}
                                                                                </div>
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            ))}
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </ApiStateHandler>
            </div>

            <Dialog open={!!selectedTool} onOpenChange={(open) => !open && setSelectedTool(null)}>
                <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <Wrench className="h-5 w-5" />
                            {selectedTool?.name}
                        </DialogTitle>
                        <DialogDescription>{selectedTool?.description}</DialogDescription>
                    </DialogHeader>

                    <div className="space-y-6 mt-4">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold">Input Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        if (selectedTool?.input_schema) {
                                            navigator.clipboard.writeText(selectedTool.input_schema);
                                            toast.success('Input schema copied');
                                        }
                                    }}
                                    className="cursor-pointer h-8 px-2"
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>{safeJsonPretty(selectedTool?.input_schema)}</code>
                            </pre>
                        </div>

                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold">Output Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        if (selectedTool?.output_schema) {
                                            navigator.clipboard.writeText(selectedTool.output_schema);
                                            toast.success('Output schema copied');
                                        }
                                    }}
                                    className="cursor-pointer h-8 px-2"
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>{safeJsonPretty(selectedTool?.output_schema)}</code>
                            </pre>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
}
