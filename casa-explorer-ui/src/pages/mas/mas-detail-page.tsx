/**
 * Copyright 2026 Copyright 2026 Cisco Systems, Inc. and its affiliates
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {useParams, useSearchParams} from 'react-router-dom';
import {useMASById} from '@/hooks/use-mas';
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
                    isError={!!error}
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
                                        <TabsList variant="underline">
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
                                                {mas.apps?.length > 0 && (
                                                    <span className="ml-1.5 text-xs text-muted-foreground">
                                                        {mas.apps.length}
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
                                                {(mas.traces?.traces ?? 0) > 0 && (
                                                    <span className="ml-1.5 text-xs text-muted-foreground">
                                                        {mas.traces?.traces}
                                                    </span>
                                                )}
                                            </TabsTrigger>
                                        </TabsList>
                                    </Tabs>
                                </CardHeader>
                                <CardContent>
                                    {activeTab === 'info' && (
                                        <MASInfoTab
                                            mas={mas}
                                            traceTotal={mas.traces?.traces ?? 0}
                                            onTabChange={handleTabChange}
                                        />
                                    )}
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
