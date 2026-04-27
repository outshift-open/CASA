import {useParams} from 'react-router-dom';
import {useMASById, useMASApps} from '@/hooks/use-mas';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MASInfoTab, MASAppsTab, MASTracesTab} from '@/components/mas';
import {Info, Activity, AppWindow, Tags} from 'lucide-react';
import {useState} from 'react';

export function MASDetailPage() {
    const {id} = useParams<{id: string}>();
    const {data: mas, isLoading, error, refetch} = useMASById(id || '');
    useMASApps(id || '');
    const [activeTab, setActiveTab] = useState('info');

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">MAS Details</h1>
                        <p className="text-muted-foreground">View Multi-Agent System</p>
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
                                    <div className="space-y-2">
                                        <CardTitle>{mas.name}</CardTitle>
                                        <CardDescription>
                                            Multi-Agent System configuration and agentic services
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
                                                Agentic Services
                                            </TabsTrigger>
                                            <TabsTrigger
                                                value="scopes"
                                                disabled
                                                className="opacity-40 cursor-not-allowed"
                                            >
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
                                    {activeTab === 'traces' && <MASTracesTab masId={id || ''} />}
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </ApiStateHandler>
            </div>
        </>
    );
}
