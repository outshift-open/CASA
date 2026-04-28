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

import {ColumnDef} from '@tanstack/react-table';
import {useNavigate} from 'react-router-dom';
import {DataTable} from '@/components/ui/data-table';
import {Tags} from 'lucide-react';

interface ScopesDataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    searchPlaceholder?: string;
    hideSearch?: boolean;
    searchValue?: string;
    onSearchChange?: (value: string) => void;
}

export function ScopesDataTable<TData, TValue extends {id?: string}>({
    columns,
    data,
    searchPlaceholder = 'Search...',
    hideSearch = false,
    searchValue,
    onSearchChange
}: ScopesDataTableProps<TData, TValue>) {
    const navigate = useNavigate();
    const emptyState = (
        <div className="flex flex-col items-center justify-center py-8 gap-3">
            <Tags className="h-10 w-10 text-muted-foreground opacity-40" />
            <div className="text-center">
                <p className="text-sm font-medium">No scopes found</p>
                <p className="text-xs text-muted-foreground mt-1">Create scopes to control MAS authorization</p>
            </div>
        </div>
    );

    return (
        <DataTable
            columns={columns}
            data={data}
            searchPlaceholder={searchPlaceholder}
            hideSearch={hideSearch}
            emptyState={emptyState}
            searchValue={searchValue}
            onSearchChange={onSearchChange}
            onRowClick={(row) => {
                const r = row as {id?: string};
                if (r.id) navigate(`/scopes/${r.id}`);
            }}
        />
    );
}
