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
import {Card, CardContent} from '@/components/ui/card';
import {CardTableHeader} from '@/components/ui/card-table-header';
import {MASDataTable} from './mas-data-table';
import {MASGridView} from './mas-grid-view';
import {createMASColumns} from './mas-columns';
import type {MASTraceCounts} from './mas-columns';
import {LayoutGrid, List} from 'lucide-react';
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
    onPageSizeChange: (size: number) => void;
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
    onPageSizeChange,
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
            <CardTableHeader
                title="Multi-Agent Systems"
                description={`${total} MAS registered`}
                refresh={{onRefresh, isLoading}}
                search={{value: search, onChange: onSearchChange, placeholder: 'Search by name'}}
                viewToggle={{
                    value: view,
                    onChange: (v) => setView(v as 'table' | 'grid'),
                    options: [
                        {value: 'table', icon: <List className="h-4 w-4" />, label: 'Table View'},
                        {value: 'grid', icon: <LayoutGrid className="h-4 w-4" />, label: 'Grid View'}
                    ]
                }}
            />
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
                        serverPageSize={pageSize}
                        onServerPageChange={onPageChange}
                        onServerPageSizeChange={onPageSizeChange}
                    />
                )}
            </CardContent>
        </Card>
    );
}
