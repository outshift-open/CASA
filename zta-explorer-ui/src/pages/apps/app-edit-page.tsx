import {useParams, useNavigate} from 'react-router-dom';
import {useAppById, useUpdateApp} from '@/hooks/use-apps';
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
import {applicationEditSchema, type ApplicationEditFormData} from '@/lib/validations/application.schema';
import {Info} from 'lucide-react';

export function AppEditPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: app, isLoading, error, refetch} = useAppById(id || '');
    const updateApp = useUpdateApp();

    const {
        register,
        handleSubmit,
        reset,
        formState: {errors}
    } = useForm<ApplicationEditFormData>({
        resolver: zodResolver(applicationEditSchema),
        defaultValues: {
            name: '',
            base_url: ''
        }
    });

    useEffect(() => {
        if (app) {
            reset({
                name: app.name || '',
                base_url: app.base_url || ''
            });
        }
    }, [app, reset]);

    const onSubmit = async (data: ApplicationEditFormData) => {
        if (!id) return;

        try {
            await updateApp.mutateAsync({
                id,
                app: {
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

                        <Alert>
                            <Info className="h-4 w-4" />
                            <AlertDescription>
                                <strong>Note:</strong> The Multi-Agent System (MAS) and Type cannot be changed after
                                application creation as they are tied to the authorization server configuration.
                            </AlertDescription>
                        </Alert>

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
                                            <Label className="text-sm font-medium">Type</Label>
                                            <div className="rounded-md border border-input bg-muted px-3 py-2">
                                                <p className="text-sm">
                                                    {app.type === 'agent'
                                                        ? 'Agent'
                                                        : app.type === 'client'
                                                          ? 'Client'
                                                          : app.type === 'mcp_server'
                                                            ? 'MCP Server'
                                                            : app.type}
                                                </p>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    Cannot be changed after creation
                                                </p>
                                            </div>
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

                                        <div className="grid gap-2">
                                            <Label className="text-sm font-medium">Multi-Agent System</Label>
                                            <div className="rounded-md border border-input bg-muted px-3 py-2">
                                                <p className="text-sm">{app.mas?.name || 'N/A'}</p>
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
