import {ColumnDef} from '@tanstack/react-table';
import {DataTable} from '@/components/ui/data-table';

interface MASDataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    searchPlaceholder?: string;
    hideSearch?: boolean;
}

export function MASDataTable<TData, TValue>({
    columns,
    data,
    searchPlaceholder = 'Search...',
    hideSearch = false
}: MASDataTableProps<TData, TValue>) {
    const emptyState = (
        <div className="flex flex-col items-center justify-center text-muted-foreground">
            <p>No Multi-Agent Systems yet.</p>
            <p className="text-sm">Create your first MAS to get started.</p>
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
