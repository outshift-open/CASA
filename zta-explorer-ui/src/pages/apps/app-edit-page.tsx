import {useParams, useNavigate} from 'react-router-dom';
import {useAppById, useUpdateApp} from '@/hooks/use-apps';
import {useForm, Controller} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {ApiStateHandler} from '@/components/api-state-handler';
import {toast} from 'sonner';
import {useEffect} from 'react';
import type {AppType} from '@/types/app.types';
import {applicationSchema, type ApplicationFormData} from '@/lib/validations/application.schema';

export function AppEditPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: app, isLoading, error, refetch} = useAppById(id || '');
    const updateApp = useUpdateApp();

    const {
        register,
        handleSubmit,
        control,
        reset,
        formState: {errors}
    } = useForm<ApplicationFormData>({
        resolver: zodResolver(applicationSchema),
        defaultValues: {
            type: 'agent',
            name: '',
            base_url: ''
        }
    });

    useEffect(() => {
        if (app) {
            reset({
                type: (app.type || 'agent') as AppType,
                name: app.name || '',
                base_url: app.base_url || ''
            });
        }
    }, [app, reset]);

    const onSubmit = async (data: ApplicationFormData) => {
        if (!id) return;

        try {
            await updateApp.mutateAsync({
                id,
                app: {
                    type: data.type,
                    name: data.name,
                    base_url: data.base_url,
                    tools: []
                }
            });
            toast.success('Application updated successfully');
            navigate(`/apps/${id}`);
        } catch (error) {
            console.error('Failed to update app:', error);
            toast.error('Failed to update application');
        }
    };

    return (
        <div className="space-y-6">
            <ApiStateHandler
                isLoading={isLoading}
                isError={!!error || !app}
                error={error as Error}
                loadingMessage="Loading application..."
                errorMessage="Failed to load application. Please try again."
                onRetry={() => refetch()}
            >
                {app && (
                    <>
                        <div>
                            <h1 className="text-2xl font-bold">Edit Application</h1>
                            <p className="text-muted-foreground">Update application details</p>
                        </div>
                        <Card>
                            <CardHeader>
                                <CardTitle>Application Details</CardTitle>
                                <CardDescription>Update the application configuration below</CardDescription>
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
                                                placeholder="My Application"
                                                {...register('name')}
                                                disabled={updateApp.isPending}
                                            />
                                            {errors.name && (
                                                <p className="text-sm text-destructive">{errors.name.message}</p>
                                            )}
                                        </div>

                                        <div className="grid gap-2">
                                            <Label htmlFor="type" className="text-sm font-medium">
                                                Type <span className="text-destructive">*</span>
                                            </Label>
                                            <Controller
                                                name="type"
                                                control={control}
                                                render={({field}) => (
                                                    <Select
                                                        value={field.value}
                                                        onValueChange={field.onChange}
                                                        disabled={updateApp.isPending}
                                                    >
                                                        <SelectTrigger id="type">
                                                            <SelectValue placeholder="Select type" />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="agent">Agent</SelectItem>
                                                            <SelectItem value="client">Client</SelectItem>
                                                            <SelectItem value="mcp_server">MCP Server</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                )}
                                            />
                                            {errors.type && (
                                                <p className="text-sm text-destructive">{errors.type.message}</p>
                                            )}
                                        </div>

                                        <div className="grid gap-2">
                                            <Label htmlFor="base_url" className="text-sm font-medium">
                                                Base URL <span className="text-destructive">*</span>
                                            </Label>
                                            <Input
                                                id="base_url"
                                                placeholder="http://localhost:3000"
                                                {...register('base_url')}
                                                disabled={updateApp.isPending}
                                            />
                                            {errors.base_url && (
                                                <p className="text-sm text-destructive">{errors.base_url.message}</p>
                                            )}
                                        </div>
                                    </div>

                                    <div className="flex justify-end gap-2">
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() => navigate(`/apps/${id}`)}
                                            disabled={updateApp.isPending}
                                        >
                                            Cancel
                                        </Button>
                                        <Button type="submit" disabled={updateApp.isPending}>
                                            {updateApp.isPending ? 'Saving...' : 'Save Changes'}
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
