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
import {Separator} from '@/components/ui/separator';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Activity, Shield, HelpCircle} from 'lucide-react';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer} from 'recharts';
import {BLOCKING_REASON_LABELS, BLOCKING_REASON_DESCRIPTIONS} from '@/components/traces/event-row';
import type {DashboardStats} from '@/services/metrics.service';

const CHART_TOOLTIP_STYLE = {
    contentStyle: {
        backgroundColor: '#22252b',
        border: '1px solid rgba(204,204,220,0.2)',
        borderRadius: '6px',
        fontSize: '12px'
    }
};

interface DenyReasonsChartProps {
    data: DashboardStats | undefined;
    isLoading: boolean;
}

export function DenyReasonsChart({data, isLoading}: DenyReasonsChartProps) {
    const navigate = useNavigate();

    const blockReasons = (data?.block_reasons ?? []).map((r) => ({
        ...r,
        label: BLOCKING_REASON_LABELS[r.reason as keyof typeof BLOCKING_REASON_LABELS] ?? r.reason,
        description: BLOCKING_REASON_DESCRIPTIONS[r.reason as keyof typeof BLOCKING_REASON_DESCRIPTIONS] ?? ''
    }));

    return (
        <Card className="gap-0 py-0">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 px-4 pt-4 pb-3">
                <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <CardTitle className="text-sm font-medium">Deny Reasons</CardTitle>
                </div>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <HelpCircle className="h-3.5 w-3.5 text-muted-foreground/50 cursor-pointer" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-[180px]">
                        <p className="text-center">
                            Breakdown of why MCP tool calls were denied by the authorization server
                        </p>
                    </TooltipContent>
                </Tooltip>
            </CardHeader>
            <CardContent className="pt-4 px-4 pb-4">
                {isLoading ? (
                    <div className="space-y-3">
                        {Array.from({length: 3}).map((_, i) => (
                            <Skeleton key={i} className="w-full h-8" />
                        ))}
                    </div>
                ) : blockReasons.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-[200px] gap-3 text-muted-foreground">
                        <Shield className="h-8 w-8 opacity-40" />
                        <p className="text-sm">No denied calls recorded yet</p>
                    </div>
                ) : (
                    <>
                        <div style={{height: `${blockReasons.length * 48 + 16}px`}}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={blockReasons}
                                    layout="vertical"
                                    margin={{left: 8, right: 24, top: 4, bottom: 4}}
                                >
                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                        stroke="rgba(204,204,220,0.1)"
                                        horizontal={false}
                                    />
                                    <XAxis
                                        type="number"
                                        allowDecimals={false}
                                        tick={{fill: '#8b8fa8', fontSize: 11}}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    <YAxis
                                        type="category"
                                        dataKey="label"
                                        width={180}
                                        tick={{fill: '#ccccdc', fontSize: 11}}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    <ChartTooltip
                                        cursor={false}
                                        content={({active, payload}) => {
                                            if (!active || !payload?.length) return null;
                                            const d = payload[0].payload as {
                                                label: string;
                                                description: string;
                                                count: number;
                                            };
                                            return (
                                                <div
                                                    style={CHART_TOOLTIP_STYLE.contentStyle}
                                                    className="px-3 py-2 max-w-[260px]"
                                                >
                                                    <p className="font-medium text-[#ccccdc] mb-1">{d.label}</p>
                                                    {d.description && (
                                                        <p className="text-[11px] text-[#8b8fa8] mb-1.5 leading-snug">
                                                            {d.description}
                                                        </p>
                                                    )}
                                                    <p className="text-[#ccccdc]">
                                                        {d.count} denied {d.count === 1 ? 'call' : 'calls'}
                                                    </p>
                                                </div>
                                            );
                                        }}
                                    />
                                    <Bar
                                        dataKey="count"
                                        name="Denied calls"
                                        fill="#ef4444"
                                        radius={[0, 4, 4, 0]}
                                        barSize={14}
                                        style={{cursor: 'pointer'}}
                                        onClick={(d) =>
                                            navigate(
                                                `${PATHS.authRequests.list}?auth=denied&q=${encodeURIComponent((d as {reason: string}).reason)}`
                                            )
                                        }
                                    />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="mt-3">
                            <Separator className="mb-3" />
                            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                                <span className="text-xs text-muted-foreground">Auth Requests</span>
                                {blockReasons.map((r) => (
                                    <button
                                        key={r.reason}
                                        type="button"
                                        className="flex items-center gap-1 text-xs text-primary hover:underline cursor-pointer"
                                        onClick={() =>
                                            navigate(
                                                `${PATHS.authRequests.list}?auth=denied&q=${encodeURIComponent(r.reason)}&from=dashboard`
                                            )
                                        }
                                    >
                                        {r.label}
                                        <span className="text-muted-foreground">({r.count})</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </>
                )}
            </CardContent>
        </Card>
    );
}
