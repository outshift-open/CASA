import {useNavigate} from 'react-router-dom';
import {useCreateApp} from '@/hooks/use-apps';
import {useForm, Controller} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {toast} from 'sonner';
import {applicationSchema, type ApplicationFormData} from '@/lib/validations/application.schema';

export function AppCreatePage() {
    const navigate = useNavigate();
    const createApp = useCreateApp();

    const {
        register,
        handleSubmit,
        control,
        formState: {errors}
    } = useForm<ApplicationFormData>({
        resolver: zodResolver(applicationSchema),
        defaultValues: {
            type: 'agent',
            name: '',
            base_url: ''
        }
    });

    const onSubmit = async (data: ApplicationFormData) => {
        try {
            await createApp.mutateAsync({
                type: data.type,
                name: data.name,
                base_url: data.base_url,
                tools: []
            });
            toast.success('Application created successfully');
            navigate('/applications');
        } catch (error) {
            console.error('Failed to create app:', error);
            toast.error('Failed to create application');
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold">Create Application</h1>
                <p className="text-muted-foreground">Add a new agent, client, or MCP server</p>
            </div>
            <Card>
                <CardHeader>
                    <CardTitle>Application Details</CardTitle>
                    <CardDescription>Fill in the details to create a new application</CardDescription>
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
                                    disabled={createApp.isPending}
                                    autoFocus
                                />
                                {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
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
                                            disabled={createApp.isPending}
                                        >
                                            <SelectTrigger id="type" className="w-full">
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
                                {errors.type && <p className="text-sm text-destructive">{errors.type.message}</p>}
                            </div>

                            <div className="grid gap-2">
                                <Label htmlFor="base_url" className="text-sm font-medium">
                                    Base URL <span className="text-destructive">*</span>
                                </Label>
                                <Input
                                    id="base_url"
                                    placeholder="http://localhost:3000"
                                    {...register('base_url')}
                                    disabled={createApp.isPending}
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
                                onClick={() => navigate('/applications')}
                                disabled={createApp.isPending}
                            >
                                Cancel
                            </Button>
                            <Button type="submit" disabled={createApp.isPending}>
                                {createApp.isPending ? 'Creating...' : 'Create Application'}
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
