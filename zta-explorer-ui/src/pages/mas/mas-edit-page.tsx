import {useParams, useNavigate} from 'react-router-dom';
import {useMASById, useUpdateMAS} from '@/hooks/use-mas';
import {useEffect} from 'react';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {ApiStateHandler} from '@/components/api-state-handler';
import {toast} from 'sonner';
import {masSchema, type MASFormData} from '@/lib/validations/mas.schema';

export function MASEditPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: mas, isLoading, error, refetch} = useMASById(id || '');
    const updateMAS = useUpdateMAS();

    const {
        register,
        handleSubmit,
        reset,
        formState: {errors}
    } = useForm<MASFormData>({
        resolver: zodResolver(masSchema),
        defaultValues: {
            name: ''
        }
    });

    useEffect(() => {
        if (mas) {
            reset({
                name: mas.name || ''
            });
        }
    }, [mas, reset]);

    const onSubmit = async (data: MASFormData) => {
        if (!id) return;

        try {
            await updateMAS.mutateAsync({
                id,
                name: data.name
            });
            toast.success('MAS updated successfully');
            navigate(`/mas/${id}`);
        } catch (error) {
            console.error('Failed to update MAS:', error);
            toast.error('Failed to update MAS');
        }
    };

    return (
        <div className="space-y-6">
            <ApiStateHandler
                isLoading={isLoading}
                isError={!!error || !mas}
                error={error as Error}
                loadingMessage="Loading MAS..."
                errorMessage="Failed to load MAS. Please try again."
                onRetry={() => refetch()}
            >
                {mas && (
                    <>
                        <div>
                            <h1 className="text-2xl font-bold">Edit Multi-Agent System</h1>
                            <p className="text-muted-foreground">
                                Update MAS name. Manage applications via the app edit pages.
                            </p>
                        </div>
                        <Card>
                            <CardHeader>
                                <CardTitle>MAS Details</CardTitle>
                                <CardDescription>Update the Multi-Agent System name</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                                    <div className="grid gap-4">
                                        <div className="grid gap-2">
                                            <Label htmlFor="name" className="text-sm font-medium">
                                                Name <span className="text-destructive">*</span>
                                            </Label>
                                            <Input
                                                id="name"
                                                placeholder="Enter MAS name"
                                                {...register('name')}
                                                disabled={updateMAS.isPending}
                                                autoFocus
                                            />
                                            {errors.name && (
                                                <p className="text-sm text-destructive">{errors.name.message}</p>
                                            )}
                                        </div>
                                    </div>

                                    <div className="flex justify-end gap-2">
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() => navigate(`/mas/${id}`)}
                                            disabled={updateMAS.isPending}
                                        >
                                            Cancel
                                        </Button>
                                        <Button type="submit" disabled={updateMAS.isPending}>
                                            {updateMAS.isPending ? 'Saving...' : 'Save Changes'}
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
