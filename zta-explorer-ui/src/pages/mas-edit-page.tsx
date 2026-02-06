import {useParams, useNavigate} from 'react-router-dom';
import {useMAS, useUpdateMAS} from '@/hooks/use-mas';
import {useApps} from '@/hooks/use-apps';
import {useState, useEffect} from 'react';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Checkbox} from '@/components/ui/checkbox';
import {Badge} from '@/components/ui/badge';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {ApiStateHandler} from '@/components/api-state-handler';
import {Search} from 'lucide-react';
import {toast} from 'sonner';
import {masSchema, type MASFormData} from '@/lib/validations/mas.schema';

export function MASEditPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: masData, isLoading, error, refetch} = useMAS();
    const {data: appsData} = useApps();
    const updateMAS = useUpdateMAS();

    const mas = masData?.find((m) => m.id === id);

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

    useEffect(() => {
        if (mas) {
            reset({
                name: mas.name || ''
            });
            setSelectedAppIds(new Set(mas.apps?.map((app) => app.id).filter((id): id is string => !!id) || []));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [mas]);

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

    const onSubmit = async (data: MASFormData) => {
        if (!id) return;

        if (selectedAppIds.size < 2) {
            setAppSelectionError('A Multi-Agent System requires at least 2 applications');
            return;
        }

        try {
            await updateMAS.mutateAsync({
                id,
                name: data.name,
                app_ids: Array.from(selectedAppIds)
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
                            <p className="text-muted-foreground">Update MAS configuration</p>
                        </div>
                        <Card>
                            <CardHeader>
                                <CardTitle>MAS Details</CardTitle>
                                <CardDescription>Update the Multi-Agent System configuration below</CardDescription>
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
                                            />
                                            {errors.name && (
                                                <p className="text-sm text-destructive">{errors.name.message}</p>
                                            )}
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
                                                            disabled={updateMAS.isPending}
                                                        />
                                                    </div>
                                                    <Select
                                                        value={typeFilter}
                                                        onValueChange={setTypeFilter}
                                                        disabled={updateMAS.isPending}
                                                    >
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
                                            <div className="border rounded-md">
                                                {filteredApps.length > 0 && (
                                                    <label
                                                        htmlFor="select-all-edit"
                                                        className="flex items-center gap-3 p-4 border-b bg-muted/50 hover:bg-muted cursor-pointer transition-colors"
                                                    >
                                                        <Checkbox
                                                            id="select-all-edit"
                                                            checked={
                                                                filteredApps.length > 0 &&
                                                                filteredApps.every(
                                                                    (app) => app.id && selectedAppIds.has(app.id)
                                                                )
                                                            }
                                                            onCheckedChange={(checked) => {
                                                                if (checked) {
                                                                    const newSelected = new Set(selectedAppIds);
                                                                    filteredApps.forEach(
                                                                        (app) => app.id && newSelected.add(app.id)
                                                                    );
                                                                    setSelectedAppIds(newSelected);
                                                                } else {
                                                                    const newSelected = new Set(selectedAppIds);
                                                                    filteredApps.forEach(
                                                                        (app) => app.id && newSelected.delete(app.id)
                                                                    );
                                                                    setSelectedAppIds(newSelected);
                                                                }
                                                                setAppSelectionError('');
                                                            }}
                                                            disabled={updateMAS.isPending}
                                                        />
                                                        <span className="text-sm font-semibold">Select All</span>
                                                    </label>
                                                )}
                                                <div className="max-h-[300px] overflow-y-auto">
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
                                                                        onCheckedChange={() =>
                                                                            app.id && toggleApp(app.id)
                                                                        }
                                                                        disabled={updateMAS.isPending}
                                                                    />
                                                                    <div className="flex-1 min-w-0">
                                                                        <div className="flex items-center gap-2 mb-1.5">
                                                                            <span className="text-sm font-semibold truncate">
                                                                                {app.name}
                                                                            </span>
                                                                            <Badge
                                                                                variant="secondary"
                                                                                className="text-xs shrink-0"
                                                                            >
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
                                            </div>
                                            {appSelectionError && (
                                                <p className="text-sm text-destructive">{appSelectionError}</p>
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
