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
                        <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                            <AppWindow className="h-10 w-10 opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No applications</p>
                                <p className="text-xs mt-1">
                                    This MAS doesn't have any applications associated with it
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
