import {useMASScopes, useDeleteScope} from '@/hooks/use-scopes';
import {Card, CardContent} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Tags, Plus, Pencil, Trash2} from 'lucide-react';
import {useNavigate} from 'react-router-dom';
import {toast} from 'sonner';
import {useState} from 'react';
import type {MAS} from '@/types/mas.types';
import {ScopeDeleteDialog} from '@/components/scopes';

interface MASScopesTabProps {
    mas: MAS;
}

export function MASScopesTab({mas}: MASScopesTabProps) {
    const navigate = useNavigate();
    const {data: scopes, isLoading: scopesLoading, error: scopesError} = useMASScopes(mas.id);
    const deleteScope = useDeleteScope();
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [deletingScopeId, setDeletingScopeId] = useState<string | null>(null);
    const [deletingScopeName, setDeletingScopeName] = useState<string>('');

    const handleDelete = async () => {
        if (!deletingScopeId) return;
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

    return (
        <>
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-lg font-semibold">Scopes</p>
                        <p className="text-sm text-muted-foreground">
                            {scopes?.length || 0} scope{scopes?.length !== 1 ? 's' : ''} configured
                        </p>
                    </div>
                    <Button
                        onClick={() => navigate(`/scopes/create?mas_id=${mas.id}`)}
                        size="sm"
                        className="cursor-pointer"
                    >
                        <Plus className="mr-2 h-4 w-4" />
                        Add Scope
                    </Button>
                </div>

                {scopesLoading ? (
                    <Card>
                        <CardContent className="pt-6">
                            <p className="text-sm text-muted-foreground text-center py-8">Loading scopes...</p>
                        </CardContent>
                    </Card>
                ) : scopesError ? (
                    <Card>
                        <CardContent className="pt-6">
                            <p className="text-sm text-destructive text-center py-8">Error loading scopes</p>
                        </CardContent>
                    </Card>
                ) : scopes && scopes.length > 0 ? (
                    <Card className="py-0">
                        <CardContent className="p-0">
                            <div className="divide-y">
                                {scopes.map((scope) => (
                                    <div
                                        key={scope.id}
                                        className="flex items-center justify-between px-4 py-4 hover:bg-muted/50 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                                <Tags className="h-5 w-5 text-primary" />
                                            </div>
                                            <div>
                                                <p className="font-semibold">{scope.name}</p>
                                                <p className="text-xs text-muted-foreground font-mono">{scope.id}</p>
                                            </div>
                                        </div>
                                        <div className="flex gap-2">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => navigate(`/scopes/${scope.id}`)}
                                                className="cursor-pointer"
                                            >
                                                View
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => navigate(`/scopes/${scope.id}/edit`)}
                                                className="cursor-pointer"
                                            >
                                                <Pencil className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => {
                                                    setDeletingScopeId(scope.id);
                                                    setDeletingScopeName(scope.name);
                                                    setIsDeleteDialogOpen(true);
                                                }}
                                                className="cursor-pointer text-destructive hover:text-destructive"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                ) : (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex flex-col items-center justify-center py-8 text-center">
                                <div className="rounded-full bg-muted p-3 mb-4">
                                    <Tags className="h-6 w-6 text-muted-foreground" />
                                </div>
                                <h3 className="text-lg font-semibold mb-2">No Scopes Yet</h3>
                                <p className="text-sm text-muted-foreground mb-6 max-w-sm">
                                    This Multi-Agent System doesn't have any scopes yet. Create your first scope to get
                                    started.
                                </p>
                                <Button onClick={() => navigate(`/scopes/create?mas_id=${mas.id}`)}>
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create Scope
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>

            <ScopeDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteScope.isPending}
                scopeName={deletingScopeName}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDelete}
            />
        </>
    );
}
