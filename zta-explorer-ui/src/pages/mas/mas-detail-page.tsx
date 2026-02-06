import {useParams, useNavigate} from 'react-router-dom';
import {useMASById, useDeleteMAS} from '@/hooks/use-mas';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MASDeleteDialog} from '@/components/mas';
import {Pencil, Trash2} from 'lucide-react';
import {toast} from 'sonner';
import {useState} from 'react';

export function MASDetailPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: mas, isLoading, error, refetch} = useMASById(id || '');
    const deleteMAS = useDeleteMAS();
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

    const handleDelete = async () => {
        if (!id) return;

        try {
            await deleteMAS.mutateAsync(id);
            toast.success('MAS deleted successfully');
            navigate('/mas');
        } catch (error) {
            console.error('Failed to delete MAS:', error);
            toast.error('Failed to delete MAS');
        }
    };

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">MAS Details</h1>
                        <p className="text-muted-foreground">View and manage Multi-Agent System</p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            onClick={() => navigate(`/mas/${id}/edit`)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !mas}
                        >
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={() => setIsDeleteDialogOpen(true)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !mas}
                        >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                        </Button>
                    </div>
                </div>

                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error || !mas}
                    error={error as Error}
                    loadingMessage="Loading MAS..."
                    errorMessage="Failed to load MAS. Please try again."
                    onRetry={() => refetch()}
                >
                    {mas && (
                        <div className="grid gap-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>{mas.name}</CardTitle>
                                    <CardDescription>Multi-Agent System configuration and applications</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6">
                                    <div className="grid gap-4">
                                        <div className="space-y-2">
                                            <p className="text-sm font-medium text-muted-foreground">Name</p>
                                            <p className="text-base">{mas.name}</p>
                                        </div>
                                        <div className="space-y-2">
                                            <p className="text-sm font-medium text-muted-foreground">Created</p>
                                            <p className="text-base">{new Date(mas.created_at).toLocaleString()}</p>
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <p className="text-sm font-medium text-muted-foreground">
                                            Applications ({mas.apps?.length || 0})
                                        </p>
                                        {mas.apps && mas.apps.length > 0 ? (
                                            <div className="grid gap-3">
                                                {mas.apps.map((app) => (
                                                    <Card
                                                        key={app.id}
                                                        className="cursor-pointer hover:bg-accent transition-colors"
                                                        onClick={() => navigate(`/apps/${app.id}`)}
                                                    >
                                                        <CardContent className="p-4">
                                                            <div className="flex items-start justify-between gap-4">
                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-center gap-2 mb-1.5">
                                                                        <p className="font-semibold truncate">
                                                                            {app.name}
                                                                        </p>
                                                                        <Badge
                                                                            variant="secondary"
                                                                            className="text-xs shrink-0"
                                                                        >
                                                                            {app.type}
                                                                        </Badge>
                                                                    </div>
                                                                    <p className="text-sm text-muted-foreground truncate">
                                                                        {app.base_url}
                                                                    </p>
                                                                </div>
                                                            </div>
                                                        </CardContent>
                                                    </Card>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-sm text-muted-foreground">
                                                No applications associated with this MAS
                                            </p>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </ApiStateHandler>
            </div>

            <MASDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteMAS.isPending}
                masName={mas?.name || ''}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDelete}
            />
        </>
    );
}
