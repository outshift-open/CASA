import {useMASApps} from '@/hooks/use-mas';
import {MASAppsTable, MASGraphView} from '@/components/mas';
import {Tabs, TabsList, TabsTrigger, TabsContent} from '@/components/ui/tabs';
import {Card, CardContent} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Table, Network, Plus} from 'lucide-react';
import {useNavigate} from 'react-router-dom';
import type {MAS} from '@/types/mas.types';

interface MASInfoTabProps {
    mas: MAS;
}

export function MASInfoTab({mas}: MASInfoTabProps) {
    const navigate = useNavigate();
    const {data: apps, isLoading: appsLoading, error: appsError} = useMASApps(mas.id);

    return (
        <div className="space-y-6">
            <div className="grid gap-4">
                <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Name</p>
                    <p className="text-base">{mas.name}</p>
                </div>
                <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Created</p>
                    <p className="text-base">{new Date(mas.created_at).toLocaleString()}</p>
                </div>
            </div>

            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-muted-foreground">Applications ({apps?.length || 0})</p>
                </div>
                {appsLoading ? (
                    <p className="text-sm text-muted-foreground">Loading applications...</p>
                ) : appsError ? (
                    <p className="text-sm text-destructive">Error loading applications</p>
                ) : apps && apps.length > 0 ? (
                    <Tabs defaultValue="table" className="w-full">
                        <TabsList>
                            <TabsTrigger value="table">
                                <Table className="mr-2 h-4 w-4" />
                                Table
                            </TabsTrigger>
                            <TabsTrigger value="graph">
                                <Network className="mr-2 h-4 w-4" />
                                Graph
                            </TabsTrigger>
                        </TabsList>
                        <TabsContent value="table" className="mt-4">
                            <MASAppsTable apps={apps} />
                        </TabsContent>
                        <TabsContent value="graph" className="mt-4">
                            <MASGraphView mas={mas} apps={apps} />
                        </TabsContent>
                    </Tabs>
                ) : (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex flex-col items-center justify-center py-8 text-center">
                                <div className="rounded-full bg-muted p-3 mb-4">
                                    <Plus className="h-6 w-6 text-muted-foreground" />
                                </div>
                                <h3 className="text-lg font-semibold mb-2">No Applications Yet</h3>
                                <p className="text-sm text-muted-foreground mb-6 max-w-sm">
                                    This Multi-Agent System doesn't have any applications associated with it yet. Create
                                    your first application to get started.
                                </p>
                                <Button onClick={() => navigate('/apps/create')}>
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create Application
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
