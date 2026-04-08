import {useMASScopes} from '@/hooks/use-scopes';
import {Card, CardContent} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Tags} from 'lucide-react';
import {useNavigate} from 'react-router-dom';
import type {MAS} from '@/types/mas.types';

interface MASScopesTabProps {
    mas: MAS;
}

export function MASScopesTab({mas}: MASScopesTabProps) {
    const navigate = useNavigate();
    const {data: scopes, isLoading: scopesLoading, error: scopesError} = useMASScopes(mas.id);

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-lg font-semibold">Scopes</p>
                    <p className="text-sm text-muted-foreground">
                        {scopes?.length || 0} scope{scopes?.length !== 1 ? 's' : ''} configured
                    </p>
                </div>
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
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => navigate(`/scopes/${scope.id}`)}
                                        className="cursor-pointer"
                                    >
                                        View
                                    </Button>
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
                            <h3 className="text-lg font-semibold mb-2">No Scopes</h3>
                            <p className="text-sm text-muted-foreground max-w-sm">
                                This Multi-Agent System doesn't have any scopes configured.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
