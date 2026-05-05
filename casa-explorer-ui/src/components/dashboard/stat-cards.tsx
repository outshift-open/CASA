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

import {useNavigate} from 'react-router-dom';
import {PATHS} from '@/router/paths';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Skeleton} from '@/components/ui/skeleton';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Activity, ShieldAlert, Network, Tags, HelpCircle, Shield, Cpu, Sparkles} from 'lucide-react';
import {checkTypeChartColors} from '@/components/ui/check-type-badge';
import {DonutChart} from './donut-chart';
import type {DashboardStats} from '@/services/metrics.service';

interface StatCardsProps {
    data: DashboardStats | undefined;
    isLoading: boolean;
    error: unknown;
}

export function StatCards({data, isLoading, error}: StatCardsProps) {
    const navigate = useNavigate();

    const mcpDonutData = [
        {name: 'Allowed', value: data?.mcp_calls_allowed ?? 0, color: '#00B98E'},
        {name: 'Denied', value: data?.mcp_calls_denied ?? 0, color: '#E2415B'}
    ].filter((d) => d.value > 0);

    const blockTypeData = [
        {
            name: 'Deterministic',
            value: data?.deterministic_blocks ?? 0,
            color: checkTypeChartColors.DETERMINISTIC,
            icon: Cpu
        },
        {name: 'Semantic', value: data?.ai_powered_blocks ?? 0, color: checkTypeChartColors.AI_POWERED, icon: Sparkles}
    ].filter((d) => d.value > 0);

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card className="gap-0 flex flex-col py-0">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 py-4">
                    <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-muted-foreground" />
                        <CardTitle className="text-sm font-medium">Auth Requests</CardTitle>
                    </div>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[180px]">
                            <p className="text-center">
                                OAuth2 token requests issued to agents, showing allowed vs denied MCP tool calls
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </CardHeader>
                <CardContent className="flex-1 flex items-center justify-center px-4 py-4">
                    <DonutChart
                        data={mcpDonutData}
                        loading={isLoading}
                        emptyIcon={<Shield className="h-8 w-8 opacity-40" />}
                        emptyText="No tool calls recorded yet"
                        unit="call"
                        onSegmentClick={(entry) => {
                            const auth = entry.name === 'Allowed' ? 'allowed' : 'denied';
                            navigate(`${PATHS.authRequests.list}?auth=${auth}&from=dashboard`);
                        }}
                    />
                </CardContent>
            </Card>

            <Card className="gap-0 flex flex-col py-0">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                    <div className="flex items-center gap-2">
                        <ShieldAlert className="h-4 w-4 text-muted-foreground" />
                        <CardTitle className="text-sm font-medium">Deny Type</CardTitle>
                    </div>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[180px]">
                            <p className="text-center">
                                How denied calls were caught — deterministic rules (scope, params) vs semantic
                                AI-powered intent verification
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </CardHeader>
                <CardContent className="flex-1 flex items-center justify-center px-4 py-4">
                    <DonutChart
                        data={blockTypeData}
                        loading={isLoading}
                        emptyIcon={<Shield className="h-8 w-8 opacity-40" />}
                        emptyText="No denied calls recorded yet"
                        unit="block"
                        onSegmentClick={(entry) => {
                            const denyType = entry.name === 'Semantic' ? 'AI_POWERED' : 'DETERMINISTIC';
                            navigate(`${PATHS.authRequests.list}?auth=denied&denyType=${denyType}&from=dashboard`);
                        }}
                    />
                </CardContent>
            </Card>

            <Card
                className="gap-0 flex flex-col cursor-pointer hover:bg-accent transition-colors py-0"
                onClick={() => navigate(PATHS.mas.list)}
            >
                <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                    <div className="flex items-center gap-2">
                        <Network className="h-4 w-4 text-muted-foreground" />
                        <CardTitle className="text-sm font-medium">Multi-Agent Systems</CardTitle>
                    </div>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[180px]">
                            <p className="text-center">
                                Multi-Agent Systems grouping agents, clients, and MCP servers under a shared
                                authorization policy
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </CardHeader>
                <CardContent className="pt-4 px-4 pb-4">
                    {isLoading ? (
                        <Skeleton className="h-8 w-16" />
                    ) : error ? (
                        <div className="text-sm text-destructive">Error</div>
                    ) : (
                        <div className="text-2xl font-bold">{data?.total_mas ?? 0}</div>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">Configured MAS</p>
                </CardContent>
            </Card>

            <Card className="gap-0 flex flex-col opacity-50 cursor-not-allowed py-0">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                    <div className="flex items-center gap-2">
                        <Tags className="h-4 w-4 text-muted-foreground" />
                        <CardTitle className="text-sm font-medium">Auth Scopes</CardTitle>
                    </div>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[180px]">
                            <p className="text-center">
                                Fine-grained OAuth2 scopes controlling which MCP tools each agent is permitted to call
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </CardHeader>
                <CardContent className="pt-4 px-4 pb-4">
                    <div className="text-2xl font-bold text-muted-foreground">—</div>
                    <p className="text-xs text-muted-foreground mt-1">Coming soon</p>
                </CardContent>
            </Card>
        </div>
    );
}
