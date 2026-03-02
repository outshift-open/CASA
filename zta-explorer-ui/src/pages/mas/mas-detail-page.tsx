import {useParams, useNavigate} from 'react-router-dom';
import {useMASById, useDeleteMAS, useMASApps} from '@/hooks/use-mas';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MASDeleteDialog, MASInfoTab, MASAppsTab, MASScopesTab, MASTracesTab} from '@/components/mas';
import {Pencil, Trash2, Info, Activity, AppWindow, Tags} from 'lucide-react';
import {toast} from 'sonner';
import {useState} from 'react';

export function MASDetailPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: mas, isLoading, error, refetch} = useMASById(id || '');
    const {data: apps} = useMASApps(id || '');
    const deleteMAS = useDeleteMAS();
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('info');

    const handleDelete = async () => {
        if (!id) return;

        try {
            await deleteMAS.mutateAsync(id);
            toast.success('MAS deleted successfully');
            navigate('/mas');
        } catch (error) {
            console.error('Failed to delete MAS:', error);
            toast.error('Failed to delete MAS');
        }
    };

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">MAS Details</h1>
                        <p className="text-muted-foreground">View and manage Multi-Agent System</p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            onClick={() => navigate(`/mas/${id}/edit`)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !mas}
                        >
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={() => setIsDeleteDialogOpen(true)}
                            className="cursor-pointer"
                            disabled={isLoading || !!error || !mas}
                        >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                        </Button>
                    </div>
                </div>

                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error || !mas}
                    error={error as Error}
                    loadingMessage="Loading MAS..."
                    errorMessage="Failed to load MAS. Please try again."
                    onRetry={() => refetch()}
                >
                    {mas && (
                        <div className="grid gap-6">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                                    <div>
                                        <CardTitle>{mas.name}</CardTitle>
                                        <CardDescription>
                                            Multi-Agent System configuration and applications
                                        </CardDescription>
                                    </div>
                                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-auto">
                                        <TabsList>
                                            <TabsTrigger value="info">
                                                <Info className="mr-2 h-4 w-4" />
                                                Info
                                            </TabsTrigger>
                                            <TabsTrigger value="apps">
                                                <AppWindow className="mr-2 h-4 w-4" />
                                                Applications
                                            </TabsTrigger>
                                            <TabsTrigger value="scopes">
                                                <Tags className="mr-2 h-4 w-4" />
                                                Scopes
                                            </TabsTrigger>
                                            <TabsTrigger value="traces">
                                                <Activity className="mr-2 h-4 w-4" />
                                                Traces
                                            </TabsTrigger>
                                        </TabsList>
                                    </Tabs>
                                </CardHeader>
                                <CardContent>
                                    {activeTab === 'info' && <MASInfoTab mas={mas} />}
                                    {activeTab === 'apps' && <MASAppsTab mas={mas} />}
                                    {activeTab === 'scopes' && <MASScopesTab mas={mas} />}
                                    {activeTab === 'traces' && <MASTracesTab />}
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </ApiStateHandler>
            </div>

            <MASDeleteDialog
                open={isDeleteDialogOpen}
                isPending={deleteMAS.isPending}
                masName={mas?.name || ''}
                appCount={apps?.length || 0}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDelete}
            />
        </>
    );
}
