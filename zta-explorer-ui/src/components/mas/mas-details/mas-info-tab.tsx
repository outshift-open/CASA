import {useMASApps} from '@/hooks/use-mas';
import {MASAppsTable} from '@/components/mas';
import {Tabs, TabsList, TabsTrigger, TabsContent} from '@/components/ui/tabs';
import {Table, Network} from 'lucide-react';
import type {MAS} from '@/types/mas.types';

interface MASInfoTabProps {
    mas: MAS;
}

export function MASInfoTab({mas}: MASInfoTabProps) {
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
                            <div className="flex items-center justify-center py-12 text-muted-foreground">
                                <p>Graph view coming soon...</p>
                            </div>
                        </TabsContent>
                    </Tabs>
                ) : (
                    <p className="text-sm text-muted-foreground">No applications associated with this MAS</p>
                )}
            </div>
        </div>
    );
}
