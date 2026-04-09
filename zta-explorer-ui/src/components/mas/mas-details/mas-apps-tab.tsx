import {useMASApps} from '@/hooks/use-mas';
import {MASAppsTable, MASGraphView} from '@/components/mas';
import {Tabs, TabsList, TabsTrigger, TabsContent} from '@/components/ui/tabs';
import {Card, CardContent} from '@/components/ui/card';
import {Skeleton} from '@/components/ui/skeleton';
import {Table, Network, AppWindow} from 'lucide-react';
import type {MAS} from '@/types/mas.types';

interface MASAppsTabProps {
    mas: MAS;
}

export function MASAppsTab({mas}: MASAppsTabProps) {
    const {data: apps, isLoading: appsLoading, error: appsError} = useMASApps(mas.id);

    return (
        <div className="space-y-4">
            <div>
                <p className="text-lg font-semibold">Applications</p>
                <p className="text-sm text-muted-foreground">
                    {apps?.length || 0} application{apps?.length !== 1 ? 's' : ''} configured
                </p>
            </div>

            {appsLoading ? (
                <div className="space-y-3">
                    {Array.from({length: 3}).map((_, i) => (
                        <Skeleton key={i} className="w-full h-10" />
                    ))}
                </div>
            ) : appsError ? (
                <Card>
                    <CardContent className="pt-6">
                        <p className="text-sm text-destructive text-center py-8">Error loading applications</p>
                    </CardContent>
                </Card>
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
                                <AppWindow className="h-6 w-6 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No Applications</h3>
                            <p className="text-sm text-muted-foreground max-w-sm">
                                This Multi-Agent System doesn't have any applications associated with it.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
