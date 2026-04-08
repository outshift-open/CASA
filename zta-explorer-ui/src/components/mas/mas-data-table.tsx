import {ColumnDef} from '@tanstack/react-table';
import {DataTable} from '@/components/ui/data-table';

interface MASDataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    searchPlaceholder?: string;
    hideSearch?: boolean;
    searchValue?: string;
    onSearchChange?: (value: string) => void;
}

export function MASDataTable<TData, TValue>({
    columns,
    data,
    searchPlaceholder = 'Search...',
    hideSearch = false,
    searchValue,
    onSearchChange
}: MASDataTableProps<TData, TValue>) {
    const emptyState = (
        <div className="flex flex-col items-center justify-center text-muted-foreground">
            <p>No Multi-Agent Systems yet.</p>
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
        />
    );
}
