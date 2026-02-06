import {useEffect, useState} from 'react';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {z} from 'zod';
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
import {Checkbox} from '@/components/ui/checkbox';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {useApps} from '@/hooks/use-apps';
import type {MAS} from '@/types/mas.types';
import {Badge} from '@/components/ui/badge';
import {Search} from 'lucide-react';

const masSchema = z.object({
    name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters')
});

type MASFormData = z.infer<typeof masSchema>;

interface MASFormDialogProps {
    open: boolean;
    mas: MAS | null;
    isPending: boolean;
    onClose: () => void;
    onSubmit: (data: {name: string; app_ids: string[]}) => void;
}

export function MASFormDialog({open, mas, isPending, onClose, onSubmit}: MASFormDialogProps) {
    const {data: appsData} = useApps();
    const [selectedAppIds, setSelectedAppIds] = useState<Set<string>>(new Set());
    const [appSelectionError, setAppSelectionError] = useState<string>('');
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [typeFilter, setTypeFilter] = useState<string>('all');

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

    const handleClose = (open: boolean) => {
        if (!open) {
            onClose();
        }
    };

    const handleCancelClick = () => {
        onClose();
    };

    // Reset form when dialog opens
    useEffect(() => {
        if (open) {
            reset({
                name: mas?.name || ''
            });
            setSelectedAppIds(new Set(mas?.apps?.map((app) => app.id).filter((id): id is string => !!id) || []));
            setAppSelectionError('');
            setSearchQuery('');
            setTypeFilter('all');
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [open, mas]);

    const toggleApp = (appId: string) => {
        const newSelected = new Set(selectedAppIds);
        if (newSelected.has(appId)) {
            newSelected.delete(appId);
        } else {
            newSelected.add(appId);
        }
        setSelectedAppIds(newSelected);
        setAppSelectionError('');
    };

    const filteredApps =
        appsData?.items?.filter((app) => {
            // Type filter
            if (typeFilter !== 'all' && app.type !== typeFilter) {
                return false;
            }

            // Search filter
            if (!searchQuery) return true;
            const query = searchQuery.toLowerCase();
            return (
                app.name.toLowerCase().includes(query) ||
                app.type.toLowerCase().includes(query) ||
                app.base_url?.toLowerCase().includes(query)
            );
        }) || [];

    const onFormSubmit = (data: MASFormData) => {
        if (selectedAppIds.size < 2) {
            setAppSelectionError('A Multi-Agent System requires at least 2 applications');
            return;
        }
        onSubmit({
            name: data.name,
            app_ids: Array.from(selectedAppIds)
        });
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
                <form onSubmit={handleSubmit(onFormSubmit)} className="flex flex-col h-full">
                    <DialogHeader>
                        <DialogTitle>{mas ? 'Edit MAS' : 'Create MAS'}</DialogTitle>
                        <DialogDescription>
                            {mas
                                ? 'Update the Multi-Agent System details below.'
                                : 'Fill in the details to create a new Multi-Agent System.'}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-6 py-4 overflow-y-auto flex-1">
                        <div className="grid gap-2">
                            <Label htmlFor="name" className="text-sm font-medium">
                                Name <span className="text-destructive">*</span>
                            </Label>
                            <Input
                                id="name"
                                placeholder="Enter MAS name"
                                {...register('name')}
                                disabled={isPending}
                                autoFocus
                                className="w-full"
                            />
                            {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
                        </div>

                        <div className="grid gap-2">
                            <Label className="text-sm font-medium">
                                Applications <span className="text-destructive">*</span>{' '}
                                <span className="text-muted-foreground text-xs">
                                    ({selectedAppIds.size} selected, minimum 2 required)
                                </span>
                            </Label>
                            {appsData?.items && appsData.items.length > 0 && (
                                <div className="flex gap-2">
                                    <div className="relative flex-1">
                                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                        <Input
                                            placeholder="Search applications..."
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value)}
                                            className="pl-9"
                                            disabled={isPending}
                                        />
                                    </div>
                                    <Select value={typeFilter} onValueChange={setTypeFilter} disabled={isPending}>
                                        <SelectTrigger className="w-[150px]">
                                            <SelectValue placeholder="All types" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All types</SelectItem>
                                            <SelectItem value="agent">Agent</SelectItem>
                                            <SelectItem value="client">Client</SelectItem>
                                            <SelectItem value="mcp_server">MCP Server</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            )}
                            <div className="border rounded-md max-h-[300px] overflow-y-auto">
                                {filteredApps.length > 0 ? (
                                    <div className="divide-y">
                                        {filteredApps.map((app) => (
                                            <label
                                                key={app.id}
                                                htmlFor={`app-${app.id}`}
                                                className="flex items-center gap-3 p-4 hover:bg-accent cursor-pointer transition-colors"
                                            >
                                                <Checkbox
                                                    id={`app-${app.id}`}
                                                    checked={!!app.id && selectedAppIds.has(app.id)}
                                                    onCheckedChange={() => app.id && toggleApp(app.id)}
                                                    disabled={isPending}
                                                />
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1.5">
                                                        <span className="text-sm font-semibold truncate">
                                                            {app.name}
                                                        </span>
                                                        <Badge variant="secondary" className="text-xs shrink-0">
                                                            {app.type}
                                                        </Badge>
                                                    </div>
                                                    <p className="text-xs text-muted-foreground truncate">
                                                        {app.base_url}
                                                    </p>
                                                </div>
                                            </label>
                                        ))}
                                    </div>
                                ) : appsData?.items && appsData.items.length > 0 ? (
                                    <p className="text-sm text-muted-foreground text-center py-8">
                                        No applications match your search.
                                    </p>
                                ) : (
                                    <p className="text-sm text-muted-foreground text-center py-8">
                                        No applications available. Create an application first.
                                    </p>
                                )}
                            </div>
                            {appSelectionError && <p className="text-sm text-destructive">{appSelectionError}</p>}
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={handleCancelClick} disabled={isPending}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isPending}>
                            {isPending ? 'Saving...' : mas ? 'Update' : 'Create'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
