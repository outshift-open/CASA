import {useParams, useNavigate} from 'react-router-dom';
import {useScopeById, useDeleteScope} from '@/hooks/use-scopes';
import {useMASById} from '@/hooks/use-mas';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ScopeDeleteDialog} from '@/components/scopes';
import {Pencil, Trash2, Network, Copy, Wrench, ExternalLink} from 'lucide-react';
import {toast} from 'sonner';
import {useState} from 'react';

export function ScopeDetailPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: scope, isLoading, error, refetch} = useScopeById(id || '');
    const {data: mas} = useMASById(scope?.mas_id || '');
    const deleteScope = useDeleteScope();
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

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

    // Check if MAS has any MCP server apps - check both scope.mas and separately fetched mas
    const masData = scope?.mas || mas;
    const hasMcpServers = masData?.apps?.some((app) => app.type === 'mcp_server') ?? false;

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
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <CardTitle>{scope.name}</CardTitle>
                                            <CardDescription>Scope information and configuration</CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid gap-6 md:grid-cols-2">
                                        <div className="space-y-4">
                                            <div className="space-y-2">
                                                <p className="text-sm font-medium text-muted-foreground">Name</p>
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
                                                        onClick={() => copyToClipboard(scope.id, 'Scope ID')}
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
                                        <div className="space-y-4 md:col-span-2">
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
                                                            {scope.mas?.name || mas?.name || 'Unknown MAS'}
                                                        </span>
                                                        <span className="font-mono text-xs text-muted-foreground">
                                                            {scope.mas?.id || mas?.id || scope.mas_id}
                                                        </span>
                                                    </div>
                                                </div>
                                            ) : (
                                                <p className="text-base text-muted-foreground">Loading...</p>
                                            )}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {hasMcpServers && (
                                <Card>
                                    <CardHeader>
                                        <div className="flex items-center gap-2">
                                            <Wrench className="h-5 w-5" />
                                            <div>
                                                <CardTitle>Tools Using This Scope</CardTitle>
                                                <CardDescription>
                                                    {scope.tools?.length || 0} tool
                                                    {scope.tools?.length !== 1 ? 's' : ''} require this scope
                                                </CardDescription>
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        {!scope.tools || scope.tools.length === 0 ? (
                                            <div className="text-center py-8">
                                                <p className="text-sm text-muted-foreground">
                                                    No tools are currently using this scope
                                                </p>
                                            </div>
                                        ) : (
                                            <div className="space-y-3">
                                                {scope.tools.map((tool) => (
                                                    <div
                                                        key={tool.id}
                                                        className="flex items-start justify-between p-3 rounded-lg border hover:bg-accent/50 transition-colors"
                                                    >
                                                        <div className="flex items-start gap-3 flex-1 min-w-0">
                                                            <Wrench className="h-4 w-4 mt-0.5 text-muted-foreground flex-shrink-0" />
                                                            <div className="flex-1 min-w-0">
                                                                <p className="font-medium truncate">{tool.name}</p>
                                                                <p className="text-xs text-muted-foreground truncate">
                                                                    {tool.description}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        {tool.app_id && (
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => navigate(`/apps/${tool.app_id}`)}
                                                                className="cursor-pointer h-7 flex-shrink-0"
                                                            >
                                                                <ExternalLink className="h-3 w-3" />
                                                            </Button>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            )}
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
        </>
    );
}
