import {useMAS, useDeleteMAS} from '@/hooks/use-mas';
import {useState, useCallback} from 'react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {Button} from '@/components/ui/button';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MASTable, MASDeleteDialog} from '@/components/mas';
import {Plus} from 'lucide-react';

export function MASPage() {
    const navigate = useNavigate();
    const {data, isLoading, error, refetch} = useMAS();
    const deleteMAS = useDeleteMAS();

    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [deletingMASId, setDeletingMASId] = useState<string | null>(null);
    const [deletingMASName, setDeletingMASName] = useState<string>('');

    const handleDelete = useCallback((id: string, name: string) => {
        setDeletingMASId(id);
        setDeletingMASName(name);
        setIsDeleteDialogOpen(true);
    }, []);

    const confirmDelete = async () => {
        if (!deletingMASId) {
            return;
        }

        try {
            await deleteMAS.mutateAsync(deletingMASId);
            toast.success('MAS deleted successfully');
            setIsDeleteDialogOpen(false);
            setDeletingMASId(null);
            await refetch(); // Force refetch to update table
        } catch (error) {
            console.error('Failed to delete MAS:', error);
            toast.error('Failed to delete MAS');
        }
    };

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('MAS refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh MAS:', error);
            toast.error('Failed to refresh MAS');
        }
    };

    return (
        <>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-muted-foreground">Manage Multi-Agent Systems</p>
                </div>
                <Button onClick={() => navigate('/mas/create')}>
                    <Plus className="mr-0.5 h-4 w-4" />
                    Create MAS
                </Button>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading MAS..."
                    errorMessage="Failed to load MAS. Please try again."
                    onRetry={() => refetch()}
                >
                    <MASTable
                        data={data || []}
                        total={data?.length || 0}
                        isLoading={isLoading}
                        onEdit={() => {}}
                        onDelete={(id: string) => {
                            const mas = data?.find((m) => m.id === id);
                            handleDelete(id, mas?.name || '');
                        }}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>

            <MASDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteMAS.isPending}
                masName={deletingMASName}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={confirmDelete}
            />
        </>
    );
}
