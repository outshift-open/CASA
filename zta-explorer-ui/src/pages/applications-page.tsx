import {useApps, useCreateApp, useUpdateApp, useDeleteApp} from '@/hooks/use-apps';
import {useState} from 'react';
import {toast} from 'sonner';
import {Button} from '@/components/ui/button';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle} from '@/components/ui/dialog';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {Textarea} from '@/components/ui/textarea';
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table';
import {Badge} from '@/components/ui/badge';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MoreHorizontal, Plus, Pencil, Trash2, RefreshCw} from 'lucide-react';
import type {App, AppType} from '@/types/app.types';

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agent',
    client: 'Client',
    mcp_server: 'MCP Server'
};

const APP_TYPE_VARIANTS: Record<AppType, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    agent: 'default',
    client: 'secondary',
    mcp_server: 'outline'
};

export function ApplicationsPage() {
    const {data, isLoading, error, refetch} = useApps();
    const createApp = useCreateApp();
    const updateApp = useUpdateApp();
    const deleteApp = useDeleteApp();

    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [deletingAppId, setDeletingAppId] = useState<string | null>(null);
    const [editingApp, setEditingApp] = useState<App | null>(null);
    const [formData, setFormData] = useState({
        type: 'agent' as AppType,
        name: '',
        base_url: '',
        tools: ''
    });

    const handleOpenDialog = (app?: App) => {
        if (app) {
            setEditingApp(app);
            setFormData({
                type: app.type,
                name: app.name,
                base_url: app.base_url,
                tools: app.tools?.join(', ') || ''
            });
        } else {
            setEditingApp(null);
            setFormData({
                type: 'agent',
                name: '',
                base_url: '',
                tools: ''
            });
        }
        setIsDialogOpen(true);
    };

    const handleCloseDialog = () => {
        setIsDialogOpen(false);
        setEditingApp(null);
        setFormData({
            type: 'agent',
            name: '',
            base_url: '',
            tools: ''
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const tools = formData.tools
            .split(',')
            .map((tool) => tool.trim())
            .filter((tool) => tool.length > 0);

        const appData = {
            type: formData.type,
            name: formData.name,
            base_url: formData.base_url,
            tools
        };

        try {
            if (editingApp?.id) {
                await updateApp.mutateAsync({id: editingApp.id, app: appData});
                toast.success('Application updated successfully');
            } else {
                await createApp.mutateAsync(appData);
                toast.success('Application created successfully');
            }
            handleCloseDialog();
        } catch (error) {
            console.error('Failed to save app:', error);
            toast.error(editingApp?.id ? 'Failed to update application' : 'Failed to create application');
        }
    };

    const handleDelete = async (id: string) => {
        setDeletingAppId(id);
        setIsDeleteDialogOpen(true);
    };

    const confirmDelete = async () => {
        if (!deletingAppId) {
            return;
        }

        try {
            await deleteApp.mutateAsync(deletingAppId);
            toast.success('Application deleted successfully');
            setIsDeleteDialogOpen(false);
            setDeletingAppId(null);
        } catch (error) {
            console.error('Failed to delete app:', error);
            toast.error('Failed to delete application');
        }
    };

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Applications refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh apps:', error);
            toast.error('Failed to refresh applications');
        }
    };

    return (
        <>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-muted-foreground">Manage agents, clients, and MCP servers</p>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" size="icon" onClick={handleRefresh} disabled={isLoading}>
                        <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button onClick={() => handleOpenDialog()}>
                        <Plus className="mr-0.5 h-4 w-4" />
                        Add Application
                    </Button>
                </div>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading applications..."
                    errorMessage="Failed to load applications. Please try again."
                    onRetry={() => refetch()}
                >
                    <Card>
                        <CardHeader>
                            <CardTitle>All Applications</CardTitle>
                            <CardDescription>
                                {data?.total || 0} application{data?.total !== 1 ? 's' : ''} registered
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Name</TableHead>
                                        <TableHead>Type</TableHead>
                                        <TableHead>Base URL</TableHead>
                                        <TableHead>Tools</TableHead>
                                        <TableHead className="w-[70px]"></TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {data?.items.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center text-muted-foreground">
                                                No applications found. Create one to get started.
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        data?.items.map((app) => (
                                            <TableRow key={app.id}>
                                                <TableCell className="font-medium">{app.name}</TableCell>
                                                <TableCell>
                                                    <Badge variant={APP_TYPE_VARIANTS[app.type]}>
                                                        {APP_TYPE_LABELS[app.type]}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="text-sm text-muted-foreground">
                                                    {app.base_url}
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex flex-wrap gap-1">
                                                        {app.tools && app.tools.length > 0 ? (
                                                            app.tools.slice(0, 3).map((tool, index) => (
                                                                <Badge key={index} variant="outline" className="text-xs">
                                                                    {tool}
                                                                </Badge>
                                                            ))
                                                        ) : (
                                                            <span className="text-xs text-muted-foreground">None</span>
                                                        )}
                                                        {app.tools && app.tools.length > 3 && (
                                                            <Badge variant="outline" className="text-xs">
                                                                +{app.tools.length - 3}
                                                            </Badge>
                                                        )}
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <DropdownMenu>
                                                        <DropdownMenuTrigger asChild>
                                                            <Button variant="ghost" size="icon">
                                                                <MoreHorizontal className="h-4 w-4" />
                                                            </Button>
                                                        </DropdownMenuTrigger>
                                                        <DropdownMenuContent align="end">
                                                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                                            <DropdownMenuSeparator />
                                                            <DropdownMenuItem onClick={() => handleOpenDialog(app)}>
                                                                <Pencil className="mr-2 h-4 w-4" />
                                                                Edit
                                                            </DropdownMenuItem>
                                                            <DropdownMenuItem
                                                                className="text-destructive"
                                                                onClick={() => app.id && handleDelete(app.id)}
                                                            >
                                                                <Trash2 className="mr-2 h-4 w-4" />
                                                                Delete
                                                            </DropdownMenuItem>
                                                        </DropdownMenuContent>
                                                    </DropdownMenu>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </ApiStateHandler>
            </div>

            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent>
                    <form onSubmit={handleSubmit}>
                        <DialogHeader>
                            <DialogTitle>{editingApp ? 'Edit Application' : 'Add Application'}</DialogTitle>
                            <DialogDescription>
                                {editingApp
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
                                    value={formData.name}
                                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                                    required
                                    className="w-full"
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="type" className="text-sm font-medium">
                                    Type <span className="text-destructive">*</span>
                                </Label>
                                <Select
                                    value={formData.type}
                                    onValueChange={(value: AppType) => setFormData({...formData, type: value})}
                                >
                                    <SelectTrigger id="type" className="w-full">
                                        <SelectValue placeholder="Select application type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="agent">Agent</SelectItem>
                                        <SelectItem value="client">Client</SelectItem>
                                        <SelectItem value="mcp_server">MCP Server</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="base_url" className="text-sm font-medium">
                                    Base URL <span className="text-destructive">*</span>
                                </Label>
                                <Input
                                    id="base_url"
                                    type="url"
                                    placeholder="https://example.com/api"
                                    value={formData.base_url}
                                    onChange={(e) => setFormData({...formData, base_url: e.target.value})}
                                    required
                                    className="w-full"
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="tools" className="text-sm font-medium">
                                    Tools <span className="text-muted-foreground text-xs">(optional)</span>
                                </Label>
                                <Textarea
                                    id="tools"
                                    placeholder="Enter tools separated by commas&#10;Example: tool1, tool2, tool3"
                                    value={formData.tools}
                                    onChange={(e) => setFormData({...formData, tools: e.target.value})}
                                    className="w-full min-h-[80px] resize-none"
                                    rows={3}
                                />
                                <p className="text-xs text-muted-foreground">Separate multiple tools with commas</p>
                            </div>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={handleCloseDialog}>
                                Cancel
                            </Button>
                            <Button type="submit" disabled={createApp.isPending || updateApp.isPending}>
                                {createApp.isPending || updateApp.isPending ? 'Saving...' : editingApp ? 'Update' : 'Create'}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            {/* Delete Confirmation Dialog */}
            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Application</DialogTitle>
                        <DialogDescription>
                            Are you sure you want to delete this application? This action cannot be undone.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button type="button" variant="destructive" onClick={confirmDelete} disabled={deleteApp.isPending}>
                            {deleteApp.isPending ? 'Deleting...' : 'Delete'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </>
    );
}
