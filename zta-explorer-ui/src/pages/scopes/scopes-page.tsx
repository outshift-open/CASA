import {useScopes, useDeleteScope} from '@/hooks/use-scopes';
import {useState, useCallback} from 'react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {Button} from '@/components/ui/button';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ScopesTable, ScopeDeleteDialog} from '@/components/scopes';
import {Plus} from 'lucide-react';

export function ScopesPage() {
    const navigate = useNavigate();
    const {data, isLoading, error, refetch} = useScopes();
    const deleteScope = useDeleteScope();

    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [deletingScopeId, setDeletingScopeId] = useState<string | null>(null);
    const [deletingScopeName, setDeletingScopeName] = useState<string>('');

    const handleDelete = useCallback((id: string, name: string) => {
        setDeletingScopeId(id);
        setDeletingScopeName(name);
        setIsDeleteDialogOpen(true);
    }, []);

    const confirmDelete = async () => {
        if (!deletingScopeId) {
            return;
        }

        try {
            await deleteScope.mutateAsync(deletingScopeId);
            toast.success('Scope deleted successfully');
            setIsDeleteDialogOpen(false);
            setDeletingScopeId(null);
        } catch (error) {
            console.error('Failed to delete scope:', error);
            toast.error('Failed to delete scope');
        }
    };

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Scopes refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh scopes:', error);
            toast.error('Failed to refresh scopes');
        }
    };

    const scopes = Array.isArray(data) ? data : [];

    return (
        <>
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Scopes</h1>
                    <p className="text-muted-foreground">Manage authorization scopes for Multi-Agent Systems</p>
                </div>
                <Button onClick={() => navigate('/scopes/create')} className="cursor-pointer">
                    <Plus className="mr-2 h-4 w-4" />
                    Create Scope
                </Button>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading scopes..."
                    errorMessage="Failed to load scopes. Please try again."
                    onRetry={() => refetch()}
                >
                    <ScopesTable
                        data={scopes}
                        total={scopes.length}
                        isLoading={isLoading}
                        onDelete={(id) => {
                            const scope = scopes.find((s) => s.id === id);
                            handleDelete(id, scope?.name || '');
                        }}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>

            <ScopeDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteScope.isPending}
                scopeName={deletingScopeName}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={confirmDelete}
            />
        </>
    );
}
