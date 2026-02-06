import {useMemo, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {ApplicationsDataTable} from '@/components/apps/applications-data-table';
import {createColumns} from '@/components/apps/columns';
import type {App} from '@/types/app.types';

interface MASAppsTableProps {
    apps: App[];
}

export function MASAppsTable({apps}: MASAppsTableProps) {
    const navigate = useNavigate();
    const [typeFilter, setTypeFilter] = useState<string>('all');

    // Create columns without the delete functionality and MAS column
    const columns = useMemo(() => {
        const allColumns = createColumns(() => {}, navigate);
        // Filter out the actions column and mas_id column
        return allColumns.filter((col) => col.id !== 'actions' && 'accessorKey' in col && col.accessorKey !== 'mas_id');
    }, [navigate]);

    const filteredData = useMemo(() => {
        if (typeFilter === 'all') return apps || [];
        return (apps || []).filter((app) => app.type === typeFilter);
    }, [apps, typeFilter]);

    const hasData = apps && apps.length > 0;

    return (
        <ApplicationsDataTable
            columns={columns}
            data={filteredData}
            searchPlaceholder="Search applications..."
            hideSearch={!hasData}
            typeFilter={typeFilter}
            onTypeFilterChange={setTypeFilter}
        />
    );
}
