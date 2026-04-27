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
