import {ColumnDef} from '@tanstack/react-table';
import {DataTable} from '@/components/ui/data-table';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';

interface ApplicationsDataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    searchPlaceholder?: string;
    hideSearch?: boolean;
    typeFilter?: string;
    onTypeFilterChange?: (value: string) => void;
    searchValue?: string;
    onSearchChange?: (value: string) => void;
}

export function ApplicationsDataTable<TData, TValue>({
    columns,
    data,
    searchPlaceholder = 'Search...',
    hideSearch = false,
    typeFilter = 'all',
    onTypeFilterChange,
    searchValue,
    onSearchChange
}: ApplicationsDataTableProps<TData, TValue>) {
    const emptyState = (
        <div className="flex flex-col items-center justify-center gap-2">
            <p className="text-sm font-medium">No applications found</p>
            <p className="text-xs text-muted-foreground">Get started by creating a new application</p>
        </div>
    );

    const filterSlot = onTypeFilterChange ? (
        <Select value={typeFilter} onValueChange={onTypeFilterChange}>
            <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="All types" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="all">All types</SelectItem>
                <SelectItem value="agent">Agent</SelectItem>
                <SelectItem value="client">Client</SelectItem>
                <SelectItem value="mcp_server">MCP Server</SelectItem>
            </SelectContent>
        </Select>
    ) : undefined;

    return (
        <DataTable
            columns={columns}
            data={data}
            searchPlaceholder={searchPlaceholder}
            hideSearch={hideSearch}
            emptyState={emptyState}
            filterSlot={filterSlot}
            searchValue={searchValue}
            onSearchChange={onSearchChange}
        />
    );
}
