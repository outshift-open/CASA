import {useParams, useNavigate} from 'react-router-dom';
import {useAppById} from '@/hooks/use-apps';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog';
import {ApiStateHandler} from '@/components/api-state-handler';
import {Network, Copy, Download, Wrench, ExternalLink, Info, Search} from 'lucide-react';
import {toast} from 'sonner';
import {useState} from 'react';
import type {AppType, Tool} from '@/types/app.types';

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

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agent',
    client: 'Client',
    mcp_server: 'MCP Server'
};

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
            app: {
                id: app.id,
                name: app.name,
                type: app.type,
                base_url: app.base_url,
                mas_id: app.mas_id,
                created_at: app.created_at
            },
            mas: app.mas
                ? {
                      id: app.mas.id,
                      name: app.mas.name
                  }
                : null,
            tools: app.tools
        };

        const blob = new Blob([JSON.stringify(config, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${app.name}-config.json`;
        link.click();
        URL.revokeObjectURL(url);
        toast.success('Configuration exported successfully');
    };

    // Check if this app has tools (only MCP servers have tools)
    const hasTools = app?.type === 'mcp_server' && (app?.tools?.length ?? 0) > 0;

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between pb-4">
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
                                    <div>
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
                                        <Card>
                                            <CardHeader>
                                                <div className="flex items-start justify-between">
                                                    <div className="space-y-1">
                                                        <CardTitle>Basic Information</CardTitle>
                                                        <CardDescription>
                                                            Core details about this application
                                                        </CardDescription>
                                                    </div>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={exportConfig}
                                                        className="cursor-pointer"
                                                    >
                                                        <Download className="mr-2 h-3 w-3" />
                                                        Export Config
                                                    </Button>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="grid gap-6 md:grid-cols-2">
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Name
                                                            </p>
                                                            <p className="text-base font-semibold">{app.name}</p>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Type
                                                            </p>
                                                            <p className="text-base">{APP_TYPE_LABELS[app.type]}</p>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Base URL
                                                            </p>
                                                            <p className="text-base font-mono text-sm">
                                                                {app.base_url}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Multi-Agent System
                                                            </p>
                                                            {app.mas ? (
                                                                <div
                                                                    className="flex items-center gap-2 cursor-pointer text-base group"
                                                                    onClick={() => navigate(`/mas/${app.mas_id}`)}
                                                                >
                                                                    <Network className="h-4 w-4 text-muted-foreground" />
                                                                    <div className="flex flex-col">
                                                                        <span className="font-semibold underline decoration-dotted group-hover:decoration-solid">
                                                                            {app.mas.name}
                                                                        </span>
                                                                        <span className="font-mono text-xs text-muted-foreground">
                                                                            {app.mas.id}
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <p className="text-base text-muted-foreground">-</p>
                                                            )}
                                                        </div>
                                                        <div className="space-y-2">
                                                            <div className="flex items-center justify-between">
                                                                <p className="text-sm font-medium text-muted-foreground">
                                                                    Application ID
                                                                </p>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="sm"
                                                                    onClick={() =>
                                                                        copyToClipboard(app.id || '', 'Application ID')
                                                                    }
                                                                    className="cursor-pointer h-6 px-2"
                                                                >
                                                                    <Copy className="h-3 w-3" />
                                                                </Button>
                                                            </div>
                                                            <p className="text-xs font-mono bg-muted px-2 py-1 rounded">
                                                                {app.id}
                                                            </p>
                                                        </div>
                                                        {app.created_at && (
                                                            <div className="space-y-2">
                                                                <p className="text-sm font-medium text-muted-foreground">
                                                                    Created
                                                                </p>
                                                                <div>
                                                                    <p className="text-base">
                                                                        {formatRelativeTime(app.created_at)}
                                                                    </p>
                                                                    <p className="text-xs text-muted-foreground">
                                                                        {new Date(app.created_at).toLocaleString()}
                                                                    </p>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    )}

                                    {activeTab === 'tools' && app.type === 'mcp_server' && (
                                        <div className="space-y-3">
                                            {!hasTools ? (
                                                <div className="flex flex-col items-center justify-center py-8 gap-3">
                                                    <Wrench className="h-10 w-10 text-muted-foreground opacity-40" />
                                                    <p className="text-sm font-medium text-muted-foreground">
                                                        No tools defined for this MCP server
                                                    </p>
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
                                                                                <p className="text-sm text-muted-foreground mt-1">
                                                                                    {tool.description}
                                                                                </p>
                                                                                <p className="text-xs text-muted-foreground mt-2">
                                                                                    Click to view schemas
                                                                                </p>
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
                                                                                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 text-xs font-medium cursor-pointer transition-all hover:scale-105"
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
                        {/* Input Schema */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold text-foreground">Input Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        if (selectedTool?.input_schema) {
                                            navigator.clipboard.writeText(selectedTool.input_schema);
                                            toast.success('Input schema copied to clipboard');
                                        }
                                    }}
                                    className="cursor-pointer h-8 px-2"
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>
                                    {selectedTool?.input_schema
                                        ? JSON.stringify(JSON.parse(selectedTool.input_schema), null, 2)
                                        : '{}'}
                                </code>
                            </pre>
                        </div>

                        {/* Output Schema */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold text-foreground">Output Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        if (selectedTool?.output_schema) {
                                            navigator.clipboard.writeText(selectedTool.output_schema);
                                            toast.success('Output schema copied to clipboard');
                                        }
                                    }}
                                    className="cursor-pointer h-8 px-2"
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>
                                    {selectedTool?.output_schema
                                        ? JSON.stringify(JSON.parse(selectedTool.output_schema), null, 2)
                                        : '{}'}
                                </code>
                            </pre>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
}
