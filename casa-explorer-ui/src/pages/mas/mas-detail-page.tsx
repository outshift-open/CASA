import {useParams, useSearchParams} from 'react-router-dom';
import {useMASById, useMASApps} from '@/hooks/use-mas';
import {useTraces} from '@/hooks/use-traces';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MASInfoTab, MASAppsTab, MASTracesTab, MASDenyConditionsTab} from '@/components/mas';
import {Info, Activity, AppWindow, Tags, ShieldAlert} from 'lucide-react';

const FLAG_DETERMINISTIC_TOOL_SELECTED = 1 << 0;
const FLAG_DETERMINISTIC_LLM_SELECTED_TOOLS = 1 << 1;
const FLAG_AI_POWERED_TOOL_MATCH = 1 << 2;
const TOTAL_CHECKS = 3;

export function MASDetailPage() {
    const {id} = useParams<{id: string}>();
    const [searchParams, setSearchParams] = useSearchParams();
    const {data: mas, isLoading, error, refetch} = useMASById(id || '');
    const {data: apps} = useMASApps(id || '');
    const {data: tracesData} = useTraces(id, 1, 1);

    const VALID_TABS = ['info', 'deny_conditions', 'apps', 'traces'];
    const tabParam = searchParams.get('tab');
    const activeTab = tabParam && VALID_TABS.includes(tabParam) ? tabParam : 'info';

    const handleTabChange = (tab: string) => {
        if (tab === 'info') {
            searchParams.delete('tab');
            setSearchParams(searchParams, {replace: true});
        } else {
            setSearchParams({tab}, {replace: true});
        }
    };

    const enabledChecks = mas?.enabled_tool_checks ?? 0;
    const enabledCount = [
        FLAG_DETERMINISTIC_TOOL_SELECTED,
        FLAG_DETERMINISTIC_LLM_SELECTED_TOOLS,
        FLAG_AI_POWERED_TOOL_MATCH
    ].filter((f) => (enabledChecks & f) !== 0).length;

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
                                    <Tabs value={activeTab} onValueChange={handleTabChange} className="w-auto">
                                        <TabsList>
                                            <TabsTrigger value="info">
                                                <Info className="mr-2 h-4 w-4" />
                                                Info
                                            </TabsTrigger>
                                            <TabsTrigger value="deny_conditions">
                                                <ShieldAlert className="mr-2 h-4 w-4" />
                                                Deny Conditions
                                                <span className="ml-1.5 text-xs text-muted-foreground">
                                                    {enabledCount}/{TOTAL_CHECKS}
                                                </span>
                                            </TabsTrigger>
                                            <TabsTrigger value="apps">
                                                <AppWindow className="mr-2 h-4 w-4" />
                                                Agentic Services
                                                {apps && (
                                                    <span className="ml-1.5 text-xs text-muted-foreground">
                                                        {apps.length}
                                                    </span>
                                                )}
                                            </TabsTrigger>
                                            <TabsTrigger
                                                value="scopes"
                                                disabled
                                                className="opacity-40 cursor-not-allowed"
                                            >
                                                <Tags className="mr-2 h-4 w-4" />
                                                Auth Scopes
                                            </TabsTrigger>
                                            <TabsTrigger value="traces">
                                                <Activity className="mr-2 h-4 w-4" />
                                                Traces
                                                {tracesData && tracesData.total > 0 && (
                                                    <span className="ml-1.5 text-xs text-muted-foreground">
                                                        {tracesData.total}
                                                    </span>
                                                )}
                                            </TabsTrigger>
                                        </TabsList>
                                    </Tabs>
                                </CardHeader>
                                <CardContent>
                                    {activeTab === 'info' && <MASInfoTab mas={mas} onTabChange={handleTabChange} />}
                                    {activeTab === 'deny_conditions' && <MASDenyConditionsTab mas={mas} />}
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
