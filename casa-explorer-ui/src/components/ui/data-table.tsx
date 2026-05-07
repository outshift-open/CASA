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

/* eslint-disable react-hooks/incompatible-library */
import {useState, ReactNode} from 'react';
import {
    ColumnDef,
    ColumnFiltersState,
    SortingState,
    VisibilityState,
    flexRender,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable
} from '@tanstack/react-table';
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {ChevronLeft, ChevronRight, Search, Inbox} from 'lucide-react';
import {cn} from '@/lib/utils';

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    searchPlaceholder?: string;
    hideSearch?: boolean;
    hidePagination?: boolean;
    emptyState?: ReactNode;
    filterSlot?: ReactNode;
    searchValue?: string;
    onSearchChange?: (value: string) => void;
    onRowClick?: (row: TData) => void;
    getRowClassName?: (row: TData) => string;
    // Server-side pagination
    serverPage?: number;
    serverPageCount?: number;
    serverTotal?: number;
    onServerPageChange?: (page: number) => void;
}

export function DataTable<TData, TValue>({
    columns,
    data,
    searchPlaceholder = 'Search...',
    hideSearch = false,
    hidePagination = false,
    emptyState,
    filterSlot,
    searchValue,
    onSearchChange,
    onRowClick,
    getRowClassName,
    serverPage,
    serverPageCount,
    serverTotal,
    onServerPageChange
}: DataTableProps<TData, TValue>) {
    const isServerPaginated =
        serverPage !== undefined && serverPageCount !== undefined && onServerPageChange !== undefined;
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
    const [internalFilter, setInternalFilter] = useState('');
    const isControlled = searchValue !== undefined && onSearchChange !== undefined;
    const globalFilter = isControlled ? searchValue : internalFilter;

    const handleGlobalFilterChange = (updater: string | ((old: string) => string)) => {
        const next = typeof updater === 'function' ? updater(globalFilter) : updater;
        if (isControlled) {
            onSearchChange!(next);
        } else {
            setInternalFilter(next);
        }
    };

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        ...(hidePagination ? {} : {getPaginationRowModel: getPaginationRowModel()}),
        manualPagination: hidePagination,
        onSortingChange: setSorting,
        getSortedRowModel: getSortedRowModel(),
        onColumnFiltersChange: setColumnFilters,
        getFilteredRowModel: getFilteredRowModel(),
        onColumnVisibilityChange: setColumnVisibility,
        onGlobalFilterChange: handleGlobalFilterChange,
        globalFilterFn: 'includesString',
        state: {
            sorting,
            columnFilters,
            columnVisibility,
            globalFilter
        }
    });

    const defaultEmptyState = (
        <div className="flex flex-col items-center justify-center py-8 gap-3 text-muted-foreground">
            <Inbox className="h-8 w-8 opacity-40" />
            <div className="text-center">
                <p className="text-sm font-medium">No results found</p>
                {globalFilter && <p className="text-xs mt-1">Try adjusting your search</p>}
            </div>
        </div>
    );

    return (
        <div className="space-y-4">
            {!hideSearch && (
                <div className="flex items-center gap-2">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder={searchPlaceholder}
                            value={globalFilter ?? ''}
                            onChange={(event) => handleGlobalFilterChange(String(event.target.value))}
                            className="pl-9"
                        />
                    </div>
                    {filterSlot}
                </div>
            )}
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id}>
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(header.column.columnDef.header, header.getContext())}
                                        </TableHead>
                                    );
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow
                                    key={row.id}
                                    data-state={row.getIsSelected() && 'selected'}
                                    className={cn(
                                        'transition-colors hover:bg-muted/50',
                                        onRowClick && 'cursor-pointer',
                                        getRowClassName?.(row.original)
                                    )}
                                    onClick={() => onRowClick?.(row.original)}
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell key={cell.id}>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">
                                    {emptyState || defaultEmptyState}
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>
            {!hidePagination && (
                <div className="flex items-center justify-between px-2">
                    {isServerPaginated ? (
                        <>
                            <p className="text-xs text-muted-foreground">
                                Page {serverPage} of {serverPageCount}
                                {serverTotal !== undefined && <> · {serverTotal} total</>}
                            </p>
                            <div className="flex items-center space-x-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => onServerPageChange(serverPage - 1)}
                                    disabled={serverPage <= 1}
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => onServerPageChange(serverPage + 1)}
                                    disabled={serverPage >= serverPageCount}
                                >
                                    <ChevronRight className="h-4 w-4" />
                                </Button>
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2">
                                    <p className="text-sm text-muted-foreground">Rows per page</p>
                                    <Select
                                        value={`${table.getState().pagination.pageSize}`}
                                        onValueChange={(value) => {
                                            table.setPageSize(Number(value));
                                        }}
                                    >
                                        <SelectTrigger className="h-8 w-[70px]">
                                            <SelectValue placeholder={table.getState().pagination.pageSize} />
                                        </SelectTrigger>
                                        <SelectContent side="top">
                                            {[10, 20, 30, 40, 50].map((pageSize) => (
                                                <SelectItem key={pageSize} value={`${pageSize}`}>
                                                    {pageSize}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="text-sm text-muted-foreground">
                                    {table.getFilteredRowModel().rows.length} of {table.getCoreRowModel().rows.length}{' '}
                                    row(s)
                                </div>
                            </div>
                            {table.getPageCount() > 1 && (
                                <div className="flex items-center space-x-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => table.previousPage()}
                                        disabled={!table.getCanPreviousPage()}
                                    >
                                        <ChevronLeft className="h-4 w-4" />
                                    </Button>
                                    <div className="text-sm font-medium">
                                        {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
                                    </div>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => table.nextPage()}
                                        disabled={!table.getCanNextPage()}
                                    >
                                        <ChevronRight className="h-4 w-4" />
                                    </Button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
