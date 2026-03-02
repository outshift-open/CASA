import {useParams, useNavigate} from 'react-router-dom';
import {useScopeById, useUpdateScope} from '@/hooks/use-scopes';
import {useMASById} from '@/hooks/use-mas';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {ApiStateHandler} from '@/components/api-state-handler';
import {Alert, AlertDescription} from '@/components/ui/alert';
import {toast} from 'sonner';
import {useEffect} from 'react';
import {scopeUpdateSchema, type ScopeUpdateFormData} from '@/lib/validations/scope.schema';
import {Info} from 'lucide-react';

export function ScopeEditPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: scope, isLoading, error, refetch} = useScopeById(id || '');
    const {data: mas} = useMASById(scope?.mas_id || '');
    const updateScope = useUpdateScope();

    const {
        register,
        handleSubmit,
        reset,
        formState: {errors}
    } = useForm<ScopeUpdateFormData>({
        resolver: zodResolver(scopeUpdateSchema),
        defaultValues: {
            name: ''
        }
    });

    useEffect(() => {
        if (scope) {
            reset({
                name: scope.name || ''
            });
        }
    }, [scope, reset]);

    const onSubmit = async (data: ScopeUpdateFormData) => {
        if (!id) return;

        try {
            await updateScope.mutateAsync({
                id,
                request: {
                    name: data.name
                }
            });
            toast.success('Scope updated successfully');
            navigate(`/scopes/${id}`);
        } catch (error) {
            console.error('Failed to update scope:', error);
            toast.error('Failed to update scope');
        }
    };

    return (
        <div className="space-y-6">
            <ApiStateHandler
                isLoading={isLoading}
                isError={!!error || !scope}
                error={error as Error}
                loadingMessage="Loading scope..."
                errorMessage="Failed to load scope. Please try again."
                onRetry={() => refetch()}
            >
                {scope && (
                    <>
                        <div>
                            <h1 className="text-2xl font-bold">Edit Scope</h1>
                            <p className="text-muted-foreground">Update scope details</p>
                        </div>

                        <Alert>
                            <Info className="h-4 w-4" />
                            <AlertDescription>
                                <strong>Note:</strong> The Multi-Agent System (MAS) cannot be changed after scope
                                creation. Changes will be automatically synchronized with Keycloak.
                            </AlertDescription>
                        </Alert>

                        <Card>
                            <CardHeader>
                                <CardTitle>Scope Details</CardTitle>
                                <CardDescription>Update the scope configuration below</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                                    <div className="grid gap-4">
                                        <div className="grid gap-2">
                                            <Label htmlFor="name" className="text-sm font-medium">
                                                Scope Name <span className="text-destructive">*</span>
                                            </Label>
                                            <Input
                                                id="name"
                                                placeholder="e.g., call-tools, read-data"
                                                {...register('name')}
                                                disabled={updateScope.isPending}
                                            />
                                            {errors.name && (
                                                <p className="text-sm text-destructive">{errors.name.message}</p>
                                            )}
                                            <p className="text-xs text-muted-foreground">
                                                Use letters, numbers, hyphens, and underscores only
                                            </p>
                                        </div>

                                        <div className="grid gap-2">
                                            <Label className="text-sm font-medium">Multi-Agent System</Label>
                                            <div className="rounded-md border border-input bg-muted px-3 py-2">
                                                <p className="text-sm">
                                                    {scope.mas?.name || mas?.name || 'Unknown MAS'}
                                                </p>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    Cannot be changed after creation
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex justify-end gap-2">
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() => navigate(`/scopes/${id}`)}
                                            disabled={updateScope.isPending}
                                        >
                                            Cancel
                                        </Button>
                                        <Button type="submit" disabled={updateScope.isPending}>
                                            {updateScope.isPending ? 'Updating...' : 'Update Scope'}
                                        </Button>
                                    </div>
                                </form>
                            </CardContent>
                        </Card>
                    </>
                )}
            </ApiStateHandler>
        </div>
    );
}
