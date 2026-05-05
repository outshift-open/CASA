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

import {Skeleton} from '@/components/ui/skeleton';
import {Shield} from 'lucide-react';
import {PieChart, Pie, Cell, Tooltip as ChartTooltip, ResponsiveContainer} from 'recharts';

const CHART_TOOLTIP_STYLE = {
    contentStyle: {
        backgroundColor: '#22252b',
        border: '1px solid rgba(204,204,220,0.2)',
        borderRadius: '6px',
        fontSize: '12px'
    },
    itemStyle: {color: '#ccccdc'},
    labelStyle: {color: '#ccccdc'}
};

export interface DonutChartEntry {
    name: string;
    value: number;
    color: string;
    icon?: React.ElementType;
}

interface DonutChartProps {
    data: DonutChartEntry[];
    loading: boolean;
    emptyIcon?: React.ReactNode;
    emptyText: string;
    unit: string;
    onSegmentClick?: (entry: DonutChartEntry) => void;
}

export function DonutChart({data, loading, emptyIcon, emptyText, unit, onSegmentClick}: DonutChartProps) {
    if (loading) {
        return (
            <div className="flex items-center justify-center h-[120px]">
                <Skeleton className="h-[100px] w-[100px] rounded-full" />
            </div>
        );
    }
    if (data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-[120px] gap-3 text-muted-foreground w-full">
                {emptyIcon ?? <Shield className="h-8 w-8 opacity-40" />}
                <p className="text-sm text-center">{emptyText}</p>
            </div>
        );
    }
    const total = data.reduce((s, d) => s + d.value, 0);
    return (
        <div className="flex items-center justify-center gap-6 h-full">
            <div className="w-[120px] h-[120px] flex-shrink-0 relative">
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
                    <span className="text-xl font-bold tabular-nums">{total}</span>
                </div>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={46}
                            outerRadius={55}
                            paddingAngle={data.length > 1 ? 3 : 0}
                            dataKey="value"
                            onClick={onSegmentClick ? (d) => onSegmentClick(d as DonutChartEntry) : undefined}
                        >
                            {data.map((entry) => (
                                <Cell
                                    key={entry.name}
                                    fill={entry.color}
                                    stroke="none"
                                    style={onSegmentClick ? {cursor: 'pointer'} : undefined}
                                />
                            ))}
                        </Pie>
                        <ChartTooltip
                            {...CHART_TOOLTIP_STYLE}
                            formatter={(value: number, name: string) => [value, name]}
                            offset={20}
                            wrapperStyle={{zIndex: 50}}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
            <div className="flex flex-col gap-3">
                {data.map((entry) => {
                    const pct = Math.round((entry.value / total) * 100);
                    return (
                        <div
                            key={entry.name}
                            className={`flex items-center gap-2.5 group ${onSegmentClick ? 'cursor-pointer' : ''}`}
                            onClick={() => onSegmentClick?.(entry)}
                        >
                            {entry.icon ? (
                                <entry.icon className="h-3.5 w-3.5 flex-shrink-0" style={{color: entry.color}} />
                            ) : (
                                <span
                                    className="h-2.5 w-2.5 rounded-full flex-shrink-0"
                                    style={{backgroundColor: entry.color}}
                                />
                            )}
                            <div className="flex flex-col">
                                <span
                                    className={`text-sm font-medium leading-none ${onSegmentClick ? 'group-hover:underline' : ''}`}
                                >
                                    {entry.name}
                                </span>
                                <span className="text-xs text-muted-foreground mt-1">
                                    {entry.value} {entry.value === 1 ? unit : `${unit}s`} · {pct}%
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
