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

import {useMemo, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {MASDataTable} from './mas-data-table';
import {createMASColumns, APP_TYPE_LABELS, APP_TYPE_CLASSES} from './mas-columns';
import type {MASTraceCounts} from './mas-columns';
import {
    RefreshCw,
    LayoutGrid,
    List,
    Network,
    AppWindow,
    Search,
    Activity,
    CheckCircle2,
    XCircle,
    ChevronLeft,
    ChevronRight,
    Loader2
} from 'lucide-react';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import type {MAS} from '@/types/mas.types';
import {DateHover} from '@/components/ui/date-hover';

interface MASTableProps {
    data: MAS[];
    total: number;
    page: number;
    pageSize: number;
    search: string;
    isLoading: boolean;
    onRefresh: () => void;
    onPageChange: (page: number) => void;
    onSearchChange: (q: string) => void;
}

export function MASTable({
    data,
    total,
    page,
    pageSize,
    search,
    isLoading,
    onRefresh,
    onPageChange,
    onSearchChange
}: MASTableProps) {
    const navigate = useNavigate();
    const [view, setView] = useState<'table' | 'grid'>('table');

    const totalPages = Math.ceil(total / pageSize);

    const masApps = useMemo(
        () => Object.fromEntries(data.map((mas) => [mas.id, mas.apps ?? []])),
        [data]
    );

    const traceCounts = useMemo(
        () =>
            Object.fromEntries(
                data.map((mas) => [
                    mas.id,
                    {
                        traces: mas.traces?.traces ?? 0,
                        allowed: mas.traces?.allowed ?? 0,
                        denied: mas.traces?.denied ?? 0
                    } satisfies MASTraceCounts
                ])
            ),
        [data]
    );

    const columns = useMemo(
        () => createMASColumns(navigate, masApps, {}, {}, traceCounts, {}),
        [navigate, masApps, traceCounts]
    );

    const hasData = data && data.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-center justify-between">
                    <div className="space-y-2">
                        <CardTitle>Multi-Agent Systems</CardTitle>
                        <CardDescription>{total} MAS registered</CardDescription>
                    </div>
                    {!isLoading && (
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="outline"
                                    size="icon"
                                    onClick={onRefresh}
                                    className="cursor-pointer"
                                    aria-label="Refresh MAS"
                                >
                                    <RefreshCw className="h-4 w-4" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Refresh</p>
                            </TooltipContent>
                        </Tooltip>
                    )}
                </div>
                <div className="flex items-center justify-between gap-2 mt-2">
                    <div className="relative w-1/2">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Search by name"
                            value={search}
                            onChange={(e) => onSearchChange(e.target.value)}
                            className="pl-9"
                        />
                    </div>
                    <ToggleGroup
                        type="single"
                        value={view}
                        onValueChange={(v) => v && setView(v as 'table' | 'grid')}
                        variant="outline"
                    >
                        <ToggleGroupItem value="table" aria-label="Table view">
                            <List className="h-4 w-4" />
                        </ToggleGroupItem>
                        <ToggleGroupItem value="grid" aria-label="Grid view">
                            <LayoutGrid className="h-4 w-4" />
                        </ToggleGroupItem>
                    </ToggleGroup>
                </div>
            </CardHeader>
            <CardContent>
                {view === 'grid' ? (
                    hasData ? (
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
                                        onClick={() => navigate(`/mas/${mas.id}`)}
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
                                                                    (a, i, arr) =>
                                                                        arr.findIndex((b) => b.id === a.id) === i
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
                    ) : (
                        <div className="flex flex-col items-center justify-center py-12 gap-3">
                            <Network className="h-10 w-10 text-muted-foreground opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No Multi-Agent Systems</p>
                                <p className="text-xs text-muted-foreground mt-1">Register a MAS to get started</p>
                            </div>
                        </div>
                    )
                ) : (
                    <MASDataTable
                        columns={columns}
                        data={data}
                        hideSearch
                        searchValue={search}
                        onSearchChange={onSearchChange}
                    />
                )}

                {totalPages > 1 && (
                    <div className="flex items-center justify-between pt-4 border-t mt-4">
                        <p className="text-xs text-muted-foreground">
                            Page {page} of {totalPages} · {total} total
                        </p>
                        <div className="flex items-center gap-1">
                            <Button
                                variant="outline"
                                size="icon"
                                className="h-7 w-7"
                                disabled={page <= 1}
                                onClick={() => onPageChange(page - 1)}
                            >
                                <ChevronLeft className="h-3.5 w-3.5" />
                            </Button>
                            <Button
                                variant="outline"
                                size="icon"
                                className="h-7 w-7"
                                disabled={page >= totalPages}
                                onClick={() => onPageChange(page + 1)}
                            >
                                <ChevronRight className="h-3.5 w-3.5" />
                            </Button>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
