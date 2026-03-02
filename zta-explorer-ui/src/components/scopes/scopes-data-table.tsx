import {ColumnDef} from '@tanstack/react-table';
import {DataTable} from '@/components/ui/data-table';

interface ScopesDataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    searchPlaceholder?: string;
    hideSearch?: boolean;
}

export function ScopesDataTable<TData, TValue>({
    columns,
    data,
    searchPlaceholder = 'Search...',
    hideSearch = false
}: ScopesDataTableProps<TData, TValue>) {
    const emptyState = (
        <div className="flex flex-col items-center justify-center gap-2">
            <p className="text-sm font-medium">No scopes found</p>
            <p className="text-xs text-muted-foreground">Get started by creating a new scope</p>
        </div>
    );

    return (
        <DataTable
            columns={columns}
            data={data}
            searchPlaceholder={searchPlaceholder}
            hideSearch={hideSearch}
            emptyState={emptyState}
        />
    );
}
