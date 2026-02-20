import {useParams, useNavigate} from 'react-router-dom';
import {useAppById, useDeleteApp} from '@/hooks/use-apps';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ApplicationDeleteDialog} from '@/components/apps';
import {Pencil, Trash2, Network} from 'lucide-react';
import {toast} from 'sonner';
import {useState} from 'react';
import type {AppType} from '@/types/app.types';

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agent',
    client: 'Client',
    mcp_server: 'MCP Server'
};

const APP_TYPE_VARIANTS: Record<AppType, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    agent: 'default',
    client: 'secondary',
    mcp_server: 'outline'
};

export function AppDetailPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: app, isLoading, error, refetch} = useAppById(id || '');
    const deleteApp = useDeleteApp();
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

    const handleDelete = async () => {
        if (!id) return;

        try {
            await deleteApp.mutateAsync(id);
            toast.success('Application deleted successfully');
            navigate('/applications');
        } catch (error) {
            console.error('Failed to delete app:', error);
            toast.error('Failed to delete application');
        }
    };

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Application Details</h1>
                        <p className="text-muted-foreground">View and manage application information</p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            onClick={() => navigate(`/apps/${id}/edit`)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !app}
                        >
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={() => setIsDeleteDialogOpen(true)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !app}
                        >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                        </Button>
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
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <CardTitle>{app.name}</CardTitle>
                                            <CardDescription>Application information and configuration</CardDescription>
                                        </div>
                                        <Badge variant={APP_TYPE_VARIANTS[app.type]}>{APP_TYPE_LABELS[app.type]}</Badge>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-6">
                                    <div className="grid gap-4 md:grid-cols-2">
                                        <div className="space-y-2">
                                            <p className="text-sm font-medium text-muted-foreground">Name</p>
                                            <p className="text-base">{app.name}</p>
                                        </div>
                                        <div className="space-y-2">
                                            <p className="text-sm font-medium text-muted-foreground">Type</p>
                                            <p className="text-base">{APP_TYPE_LABELS[app.type]}</p>
                                        </div>
                                        <div className="space-y-2 md:col-span-2">
                                            <p className="text-sm font-medium text-muted-foreground">Base URL</p>
                                            <p className="text-base font-mono text-sm">{app.base_url}</p>
                                        </div>
                                        <div className="space-y-2 md:col-span-2">
                                            <p className="text-sm font-medium text-muted-foreground">
                                                Multi-Agent System
                                            </p>
                                            {app.mas ? (
                                                <div
                                                    className="flex items-center gap-2 cursor-pointer hover:decoration-solid text-base"
                                                    onClick={() => navigate(`/mas/${app.mas_id}`)}
                                                >
                                                    <Network className="h-4 w-4 text-muted-foreground" />
                                                    <div className="flex flex-col">
                                                        <span className="font-semibold">{app.mas.name}</span>
                                                        <span className="font-mono text-xs text-muted-foreground">
                                                            {app.mas.id}
                                                        </span>
                                                    </div>
                                                </div>
                                            ) : (
                                                <p className="text-base text-muted-foreground">-</p>
                                            )}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </ApiStateHandler>
            </div>

            <ApplicationDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteApp.isPending}
                appName={app?.name || ''}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDelete}
            />
        </>
    );
}
