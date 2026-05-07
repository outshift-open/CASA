/**
 * Copyright 2026 Cisco Systems, Inc. and its affiliates
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
import {Card} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Network, AppWindow, Activity, CheckCircle2, XCircle, ChevronLeft, ChevronRight, Loader2} from 'lucide-react';
import {DateHover} from '@/components/ui/date-hover';
import {APP_TYPE_LABELS, APP_TYPE_CLASSES} from './mas-columns';
import type {MASTraceCounts} from './mas-columns';
import type {MAS} from '@/types/mas.types';

interface MASGridViewProps {
    data: MAS[];
    total: number;
    page: number;
    pageSize: number;
    isLoading: boolean;
    traceCounts: Record<string, MASTraceCounts>;
    onPageChange: (page: number) => void;
}

export function MASGridView({data, total, page, pageSize, isLoading, traceCounts, onPageChange}: MASGridViewProps) {
    const navigate = useNavigate();
    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    if (data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
                <Network className="h-10 w-10 text-muted-foreground opacity-40" />
                <div className="text-center">
                    <p className="text-sm font-medium">No Multi-Agent Systems</p>
                    <p className="text-xs text-muted-foreground mt-1">Register a MAS to get started</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="relative">
                {isLoading && (
                    <div className="absolute inset-0 z-10 flex items-center justify-center rounded-lg bg-background/60 backdrop-blur-sm">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>
                )}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {data.map((mas) => {
                        const apps = mas.apps ?? [];
                        const traces = traceCounts[mas.id];
                        return (
                            <Card
                                key={mas.id}
                                className="cursor-pointer hover:bg-accent/50 transition-colors p-0"
                                onClick={() => navigate(PATHS.mas.detail(mas.id))}
                            >
                                <div className="flex items-center gap-2 px-3 pt-2.5 pb-0.5">
                                    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-primary/10">
                                        <Network className="h-3 w-3 text-primary" />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <p className="text-sm font-semibold truncate">{mas.name}</p>
                                        <DateHover
                                            date={mas.created_at}
                                            className="text-[11px] text-muted-foreground"
                                        />
                                    </div>
                                </div>
                                <div className="flex items-center justify-center gap-3 px-3 pb-1.5 text-xs text-muted-foreground">
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div className="flex items-center gap-1 cursor-help">
                                                <AppWindow className="h-3 w-3" />
                                                <span>{apps.length}</span>
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent className="p-2">
                                            {apps.length === 0 ? (
                                                <p className="text-xs italic">No agentic services configured</p>
                                            ) : (
                                                <div className="flex flex-col gap-1.5 max-w-[320px]">
                                                    {apps
                                                        .filter(
                                                            (a, i, arr) => arr.findIndex((b) => b.id === a.id) === i
                                                        )
                                                        .map((app) => (
                                                            <span
                                                                key={app.id}
                                                                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${APP_TYPE_CLASSES[app.type]}`}
                                                            >
                                                                <span className="text-[9px] uppercase tracking-wide opacity-70">
                                                                    {APP_TYPE_LABELS[app.type]}
                                                                </span>
                                                                {app.name}
                                                            </span>
                                                        ))}
                                                </div>
                                            )}
                                        </TooltipContent>
                                    </Tooltip>
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div className="flex items-center gap-1 cursor-help">
                                                <Activity className="h-3 w-3" />
                                                <span>{traces?.traces ?? 0}</span>
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p className="text-xs">Trace sessions recorded for this MAS.</p>
                                        </TooltipContent>
                                    </Tooltip>
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div className="flex items-center gap-1 cursor-help">
                                                <CheckCircle2 className="h-3 w-3 text-green-500" />
                                                <span>{traces?.allowed ?? 0}</span>
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p className="text-xs">Allowed MCP tool calls</p>
                                        </TooltipContent>
                                    </Tooltip>
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div className="flex items-center gap-1 cursor-help">
                                                <XCircle className="h-3 w-3 text-red-500" />
                                                <span>{traces?.denied ?? 0}</span>
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p className="text-xs">Denied MCP tool calls</p>
                                        </TooltipContent>
                                    </Tooltip>
                                </div>
                            </Card>
                        );
                    })}
                </div>
            </div>

            <div className="flex items-center justify-between px-2">
                <p className="text-xs text-muted-foreground">
                    Page {page} of {totalPages} · {total} total
                </p>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" onClick={() => onPageChange(page - 1)} disabled={page <= 1}>
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onPageChange(page + 1)}
                        disabled={page >= totalPages}
                    >
                        <ChevronRight className="h-4 w-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
}
