import {useApps, useDeleteApp} from '@/hooks/use-apps';
import {useState, useCallback} from 'react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {Button} from '@/components/ui/button';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ApplicationsTable, ApplicationDeleteDialog} from '@/components/apps';
import {Plus} from 'lucide-react';

export function ApplicationsPage() {
    const navigate = useNavigate();
    const {data, isLoading, error, refetch} = useApps();
    const deleteApp = useDeleteApp();

    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [deletingAppId, setDeletingAppId] = useState<string | null>(null);
    const [deletingAppName, setDeletingAppName] = useState<string>('');

    const handleDelete = useCallback((id: string, name: string) => {
        setDeletingAppId(id);
        setDeletingAppName(name);
        setIsDeleteDialogOpen(true);
    }, []);

    const confirmDelete = async () => {
        if (!deletingAppId) {
            return;
        }

        try {
            await deleteApp.mutateAsync(deletingAppId);
            toast.success('Application deleted successfully');
            setIsDeleteDialogOpen(false);
            setDeletingAppId(null);
        } catch (error) {
            console.error('Failed to delete app:', error);
            toast.error('Failed to delete application');
        }
    };

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Applications refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh apps:', error);
            toast.error('Failed to refresh applications');
        }
    };

    return (
        <>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-muted-foreground">Manage agents, clients, and MCP servers</p>
                </div>
                <Button onClick={() => navigate('/apps/create')}>
                    <Plus className="mr-0.5 h-4 w-4" />
                    Add Application
                </Button>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading applications..."
                    errorMessage="Failed to load applications. Please try again."
                    onRetry={() => refetch()}
                >
                    <ApplicationsTable
                        data={data?.items || []}
                        total={data?.total || 0}
                        isLoading={isLoading}
                        onDelete={(id) => {
                            const app = data?.items?.find((a) => a.id === id);
                            handleDelete(id, app?.name || '');
                        }}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>

            <ApplicationDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteApp.isPending}
                appName={deletingAppName}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={confirmDelete}
            />
        </>
    );
}
