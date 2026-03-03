import {useParams, useNavigate} from 'react-router-dom';
import {useScopeById, useDeleteScope} from '@/hooks/use-scopes';
import {useMASById} from '@/hooks/use-mas';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ScopeDeleteDialog} from '@/components/scopes';
import {Pencil, Trash2, Network, Copy, Wrench, ExternalLink, Info} from 'lucide-react';
import {toast} from 'sonner';
import {useState, useMemo} from 'react';
import type {Tool} from '@/types/app.types';

export function ScopeDetailPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: scope, isLoading, error, refetch} = useScopeById(id || '');
    const {data: mas} = useMASById(scope?.mas_id || '');
    const deleteScope = useDeleteScope();
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('info');
    const [selectedTool, setSelectedTool] = useState<Tool | null>(null);

    const handleDelete = async () => {
        if (!id) return;

        try {
            await deleteScope.mutateAsync(id);
            toast.success('Scope deleted successfully');
            navigate('/scopes');
        } catch (error) {
            console.error('Failed to delete scope:', error);
            toast.error('Failed to delete scope');
        }
    };

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`${label} copied to clipboard`);
    };

    // Get all tools from MAS apps that use this scope
    // Only MCP server apps have tools
    const toolsUsingScope = useMemo(() => {
        if (!mas?.apps || !scope) return [];

        const allTools = mas.apps.filter((app) => app.type === 'mcp_server').flatMap((app) => app.tools || []);

        // Filter tools that have this scope in their scopes list
        return allTools.filter((tool) => tool.scopes?.some((s) => s.id === scope.id));
    }, [mas, scope]);

    const hasTools = toolsUsingScope.length > 0;

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Scope Details</h1>
                        <p className="text-muted-foreground">View and manage scope information</p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            onClick={() => navigate(`/scopes/${id}/edit`)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !scope}
                        >
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={() => setIsDeleteDialogOpen(true)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !scope}
                        >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                        </Button>
                    </div>
                </div>

                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error || !scope}
                    error={error as Error}
                    loadingMessage="Loading scope..."
                    errorMessage="Failed to load scope. Please try again."
                    onRetry={() => refetch()}
                >
                    {scope && (
                        <div className="grid gap-6">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                                    <div>
                                        <CardTitle>{scope.name}</CardTitle>
                                        <CardDescription>Scope information and tools</CardDescription>
                                    </div>
                                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-auto">
                                        <TabsList>
                                            <TabsTrigger value="info">
                                                <Info className="mr-2 h-4 w-4" />
                                                Info
                                            </TabsTrigger>
                                            <TabsTrigger value="tools">
                                                <Wrench className="mr-2 h-4 w-4" />
                                                Tools
                                            </TabsTrigger>
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
                                                        <CardDescription>Core details about this scope</CardDescription>
                                                    </div>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="grid gap-6 md:grid-cols-2">
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Name
                                                            </p>
                                                            <p className="text-base font-semibold">{scope.name}</p>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <div className="flex items-center justify-between">
                                                                <p className="text-sm font-medium text-muted-foreground">
                                                                    Scope ID
                                                                </p>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="sm"
                                                                    onClick={() =>
                                                                        copyToClipboard(scope.id, 'Scope ID')
                                                                    }
                                                                    className="cursor-pointer h-6 px-2"
                                                                >
                                                                    <Copy className="h-3 w-3" />
                                                                </Button>
                                                            </div>
                                                            <p className="text-xs font-mono bg-muted px-2 py-1 rounded">
                                                                {scope.id}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Multi-Agent System
                                                            </p>
                                                            {scope.mas || mas ? (
                                                                <div
                                                                    className="flex items-center gap-2 cursor-pointer text-base group"
                                                                    onClick={() => navigate(`/mas/${scope.mas_id}`)}
                                                                >
                                                                    <Network className="h-4 w-4 text-muted-foreground" />
                                                                    <div className="flex flex-col">
                                                                        <span className="font-semibold underline decoration-dotted group-hover:decoration-solid">
                                                                            {scope.mas?.name ||
                                                                                mas?.name ||
                                                                                'Unknown MAS'}
                                                                        </span>
                                                                        <span className="font-mono text-xs text-muted-foreground">
                                                                            {scope.mas?.id || mas?.id || scope.mas_id}
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <p className="text-base text-muted-foreground">
                                                                    Loading...
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    )}

                                    {activeTab === 'tools' && (
                                        <div>
                                            {!hasTools ? (
                                                <div className="text-center py-8">
                                                    <p className="text-sm text-muted-foreground">
                                                        No tools are currently using this scope
                                                    </p>
                                                </div>
                                            ) : (
                                                <div className="space-y-3">
                                                    {toolsUsingScope.map((tool) => (
                                                        <div
                                                            key={tool.id}
                                                            className="group p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer"
                                                            onClick={() => setSelectedTool(tool)}
                                                        >
                                                            <div className="flex items-start justify-between gap-4">
                                                                <div className="flex items-start gap-3 flex-1 min-w-0">
                                                                    <div className="mt-0.5 p-2 rounded-md bg-primary/10">
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
                                                                {tool.app_id && (
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="sm"
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            navigate(`/apps/${tool.app_id}`);
                                                                        }}
                                                                        className="cursor-pointer h-8 w-8 p-0 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                                                                        title="View app"
                                                                    >
                                                                        <ExternalLink className="h-4 w-4" />
                                                                    </Button>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </ApiStateHandler>
            </div>

            <ScopeDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteScope.isPending}
                scopeName={scope?.name || ''}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDelete}
            />

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
