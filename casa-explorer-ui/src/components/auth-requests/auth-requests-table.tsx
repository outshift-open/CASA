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

import {useMemo} from 'react';
import {Card, CardContent} from '@/components/ui/card';
import {CardTableHeader} from '@/components/ui/card-table-header';
import {DataTable} from '@/components/ui/data-table';
import {Skeleton} from '@/components/ui/skeleton';
import {Shield} from 'lucide-react';
import {useAuthRequestColumns, type AuthRequest} from './auth-request-columns';
import type {AppNames} from '@/components/traces/event-row';
import {BlockingType} from '@/types/trace.types';

interface MASOption {
    id: string;
    name: string;
}

interface AuthRequestsTableProps {
    rows: AuthRequest[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
    isLoading: boolean;
    isFetching: boolean;
    search: string;
    authFilter: string;
    masFilter: string;
    denyTypeFilter: string;
    masList: MASOption[];
    masMap: Record<string, string>;
    appNames: AppNames;
    selectedUserInputId: string | null;
    selectedTraceId: string | null;
    onRefresh: () => void;
    onSearchChange: (value: string | null) => void;
    onAuthFilterChange: (value: string) => void;
    onMasFilterChange: (value: string) => void;
    onDenyTypeFilterChange: (value: string) => void;
    onPageChange: (page: number) => void;
    onPageSizeChange: (size: number) => void;
    onRowClick: (row: AuthRequest) => void;
}

export function AuthRequestsTable({
    rows,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    isFetching,
    search,
    authFilter,
    masFilter,
    denyTypeFilter,
    masList,
    masMap,
    appNames,
    selectedUserInputId,
    selectedTraceId,
    onRefresh,
    onSearchChange,
    onAuthFilterChange,
    onMasFilterChange,
    onDenyTypeFilterChange,
    onPageChange,
    onPageSizeChange,
    onRowClick
}: AuthRequestsTableProps) {
    const columns = useAuthRequestColumns(masMap, appNames);

    const masFilterOptions = useMemo(
        () => [{value: 'all', label: 'All MAS'}, ...masList.map((m) => ({value: m.id, label: m.name}))],
        [masList]
    );

    return (
        <Card>
            <CardTableHeader
                title="Auth Requests"
                description={isLoading ? 'Loading...' : `${total} request${total !== 1 ? 's' : ''} recorded`}
                refresh={{onRefresh, isLoading: isLoading || isFetching}}
                search={{
                    value: search,
                    onChange: (v) => onSearchChange(v || null),
                    placeholder: 'Filter by tool name...'
                }}
                filters={[
                    {
                        value: authFilter,
                        onChange: onAuthFilterChange,
                        options: [
                            {value: 'all', label: 'All Authorizations'},
                            {value: 'allowed', label: 'Allowed Only'},
                            {value: 'denied', label: 'Denied Only'}
                        ]
                    },
                    {
                        value: masFilter,
                        onChange: onMasFilterChange,
                        options: masFilterOptions
                    },
                    {
                        value: denyTypeFilter,
                        onChange: onDenyTypeFilterChange,
                        options: [
                            {value: 'all', label: 'Any Deny Type'},
                            {value: BlockingType.Deterministic, label: 'Deterministic'},
                            {value: BlockingType.AIPowered, label: 'Semantic'}
                        ]
                    }
                ]}
            />
            <CardContent>
                {isLoading ? (
                    <div className="space-y-2">
                        {Array.from({length: 5}).map((_, i) => (
                            <Skeleton key={i} className="h-12 w-full" />
                        ))}
                    </div>
                ) : rows.length === 0 && !isFetching ? (
                    <div className="flex flex-col items-center justify-center py-12 gap-3">
                        <Shield className="h-10 w-10 text-muted-foreground opacity-40" />
                        <div className="text-center">
                            <p className="text-sm font-medium">No auth requests yet</p>
                            <p className="text-xs text-muted-foreground mt-1">
                                MCP tool authorization activity will appear here
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className={isFetching ? 'opacity-60 pointer-events-none' : undefined}>
                        <DataTable
                            columns={columns}
                            data={rows}
                            hideSearch
                            onRowClick={onRowClick}
                            getRowClassName={(row) => {
                                if (row.id === selectedTraceId || row.userInputId === selectedUserInputId)
                                    return 'border-l-2 border-b-0';
                                return '';
                            }}
                            getRowStyle={(row) => {
                                if (row.id === selectedTraceId)
                                    return {
                                        borderLeftColor: 'rgba(0,188,235,0.9)',
                                        backgroundColor: 'rgba(0,188,235,0.07)'
                                    };
                                if (row.userInputId === selectedUserInputId)
                                    return {borderLeftColor: 'rgba(0,188,235,0.3)'};
                                return {};
                            }}
                            serverPage={page}
                            serverPageCount={totalPages}
                            serverTotal={total}
                            serverPageSize={pageSize}
                            onServerPageChange={onPageChange}
                            onServerPageSizeChange={onPageSizeChange}
                        />
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
