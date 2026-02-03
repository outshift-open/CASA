import {useEffect} from 'react';
import {useForm, Controller} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from '@/components/ui/dialog';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {Textarea} from '@/components/ui/textarea';
import type {App, AppType} from '@/types/app.types';
import {applicationSchema, type ApplicationFormData} from '@/lib/validations/application.schema';

interface ApplicationFormDialogProps {
    open: boolean;
    app: App | null;
    isPending: boolean;
    onClose: () => void;
    onSubmit: (data: {type: AppType; name: string; base_url: string; tools: string[]}) => void;
}

export function ApplicationFormDialog({open, app, isPending, onClose, onSubmit}: ApplicationFormDialogProps) {
    const {
        register,
        handleSubmit,
        control,
        reset,
        formState: {errors, isDirty}
    } = useForm<ApplicationFormData>({
        resolver: zodResolver(applicationSchema),
        defaultValues: {
            type: 'agent',
            name: '',
            base_url: '',
            tools: ''
        }
    });

    const handleClose = () => {
        if (isDirty && !isPending) {
            if (window.confirm('You have unsaved changes. Are you sure you want to close?')) {
                onClose();
            }
        } else {
            onClose();
        }
    };

    // Reset form when dialog opens with new data
    useEffect(() => {
        if (open) {
            reset({
                type: (app?.type || 'agent') as AppType,
                name: app?.name || '',
                base_url: app?.base_url || '',
                tools: app?.tools?.join(', ') || ''
            });
        }
    }, [open, app, reset]);

    const onFormSubmit = (data: ApplicationFormData) => {
        const tools = data.tools
            ? data.tools
                  .split(',')
                  .map((tool: string) => tool.trim())
                  .filter((tool: string) => tool.length > 0)
            : [];

        onSubmit({
            type: data.type,
            name: data.name,
            base_url: data.base_url,
            tools
        });
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent>
                <form onSubmit={handleSubmit(onFormSubmit)}>
                    <DialogHeader>
                        <DialogTitle>{app ? 'Edit Application' : 'Add Application'}</DialogTitle>
                        <DialogDescription>
                            {app
                                ? 'Update the application details below.'
                                : 'Fill in the details to create a new application.'}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-6 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="name" className="text-sm font-medium">
                                Name <span className="text-destructive">*</span>
                            </Label>
                            <Input
                                id="name"
                                placeholder="Enter application name"
                                {...register('name')}
                                disabled={isPending}
                                autoFocus
                                className="w-full"
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
                                    <Select value={field.value} onValueChange={field.onChange} disabled={isPending}>
                                        <SelectTrigger id="type" className="w-full" disabled={isPending}>
                                            <SelectValue placeholder="Select application type" />
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
                                type="url"
                                placeholder="https://example.com/api"
                                {...register('base_url')}
                                disabled={isPending}
                                className="w-full"
                            />
                            {errors.base_url && <p className="text-sm text-destructive">{errors.base_url.message}</p>}
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="tools" className="text-sm font-medium">
                                Tools <span className="text-muted-foreground text-xs">(optional)</span>
                            </Label>
                            <Textarea
                                id="tools"
                                placeholder="Enter tools separated by commas&#10;Example: tool1, tool2, tool3"
                                {...register('tools')}
                                disabled={isPending}
                                className="w-full min-h-[80px] resize-none"
                                rows={3}
                            />
                            <p className="text-xs text-muted-foreground">Separate multiple tools with commas</p>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={handleClose} disabled={isPending}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isPending}>
                            {isPending ? 'Saving...' : app ? 'Update' : 'Create'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
