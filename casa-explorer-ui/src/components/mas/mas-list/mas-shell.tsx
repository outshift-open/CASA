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

import {useMemo, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {MASDataTable} from './mas-data-table';
import {MASGridView} from './mas-grid-view';
import {createMASColumns} from './mas-columns';
import type {MASTraceCounts} from './mas-columns';
import {RefreshCw, LayoutGrid, List, Search} from 'lucide-react';
import type {MAS} from '@/types/mas.types';

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

    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    const masApps = useMemo(() => Object.fromEntries(data.map((mas) => [mas.id, mas.apps ?? []])), [data]);

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
                    <MASGridView
                        data={data}
                        total={total}
                        page={page}
                        pageSize={pageSize}
                        isLoading={isLoading}
                        traceCounts={traceCounts}
                        onPageChange={onPageChange}
                    />
                ) : (
                    <MASDataTable
                        columns={columns}
                        data={data}
                        hideSearch
                        searchValue={search}
                        onSearchChange={onSearchChange}
                        serverPage={page}
                        serverPageCount={totalPages}
                        serverTotal={total}
                        onServerPageChange={onPageChange}
                    />
                )}
            </CardContent>
        </Card>
    );
}
