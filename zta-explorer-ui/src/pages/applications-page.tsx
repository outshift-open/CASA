import {useApps, useCreateApp, useUpdateApp, useDeleteApp} from '@/hooks/use-apps';
import {useState, useCallback} from 'react';
import {toast} from 'sonner';
import {Button} from '@/components/ui/button';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ApplicationsTable, ApplicationFormDialog, ApplicationDeleteDialog} from '@/components/apps';
import {Plus} from 'lucide-react';
import type {App, AppType} from '@/types/app.types';

export function ApplicationsPage() {
    const {data, isLoading, error, refetch} = useApps();
    const createApp = useCreateApp();
    const updateApp = useUpdateApp();
    const deleteApp = useDeleteApp();

    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [deletingAppId, setDeletingAppId] = useState<string | null>(null);
    const [editingApp, setEditingApp] = useState<App | null>(null);

    const handleOpenDialog = useCallback((app?: App) => {
        setEditingApp(app || null);
        setIsDialogOpen(true);
    }, []);

    const handleCloseDialog = useCallback(() => {
        setIsDialogOpen(false);
        setEditingApp(null);
    }, []);

    const handleDelete = useCallback((id: string) => {
        setDeletingAppId(id);
        setIsDeleteDialogOpen(true);
    }, []);

    const handleSubmit = async (appData: {type: AppType; name: string; base_url: string; tools: string[]}) => {
        try {
            if (editingApp?.id) {
                await updateApp.mutateAsync({id: editingApp.id, app: appData});
                toast.success('Application updated successfully');
            } else {
                await createApp.mutateAsync(appData);
                toast.success('Application created successfully');
            }
            handleCloseDialog();
        } catch (error) {
            console.error('Failed to save app:', error);
            toast.error(editingApp?.id ? 'Failed to update application' : 'Failed to create application');
        }
    };

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
                <Button onClick={() => handleOpenDialog()}>
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
                        onEdit={handleOpenDialog}
                        onDelete={handleDelete}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>

            <ApplicationFormDialog
                open={isDialogOpen}
                app={editingApp}
                isPending={createApp.isPending || updateApp.isPending}
                onClose={handleCloseDialog}
                onSubmit={handleSubmit}
            />

            <ApplicationDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteApp.isPending}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={confirmDelete}
            />
        </>
    );
}
