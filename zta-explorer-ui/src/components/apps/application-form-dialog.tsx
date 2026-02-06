import {useCreateApp} from '@/hooks/use-apps';
import {useForm, Controller} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from '@/components/ui/dialog';
import {toast} from 'sonner';
import {applicationSchema, type ApplicationFormData} from '@/lib/validations/application.schema';

interface ApplicationFormDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess?: (appId: string) => void;
}

export function ApplicationFormDialog({open, onOpenChange, onSuccess}: ApplicationFormDialogProps) {
    const createApp = useCreateApp();

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

    const onSubmit = async (data: ApplicationFormData) => {
        try {
            const newApp = await createApp.mutateAsync({
                type: data.type,
                name: data.name,
                base_url: data.base_url,
                tools: []
            });
            toast.success('Application created successfully');
            reset();
            onOpenChange(false);
            if (onSuccess && newApp.id) {
                onSuccess(newApp.id);
            }
        } catch (error) {
            console.error('Failed to create app:', error);
            toast.error('Failed to create application');
        }
    };

    const handleClose = () => {
        reset();
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Create Application</DialogTitle>
                    <DialogDescription>Add a new agent, client, or MCP server</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div className="grid gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="dialog-name" className="text-sm font-medium">
                                Name <span className="text-destructive">*</span>
                            </Label>
                            <Input
                                id="dialog-name"
                                placeholder="My Application"
                                {...register('name')}
                                disabled={createApp.isPending}
                                autoFocus
                            />
                            {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
                        </div>

                        <div className="grid gap-2">
                            <Label htmlFor="dialog-type" className="text-sm font-medium">
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
                                        <SelectTrigger id="dialog-type" className="w-full">
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
                            <Label htmlFor="dialog-base_url" className="text-sm font-medium">
                                Base URL <span className="text-destructive">*</span>
                            </Label>
                            <Input
                                id="dialog-base_url"
                                placeholder="http://localhost:3000"
                                {...register('base_url')}
                                disabled={createApp.isPending}
                            />
                            {errors.base_url && <p className="text-sm text-destructive">{errors.base_url.message}</p>}
                        </div>
                    </div>

                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={handleClose} disabled={createApp.isPending}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={createApp.isPending}>
                            {createApp.isPending ? 'Creating...' : 'Create Application'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
