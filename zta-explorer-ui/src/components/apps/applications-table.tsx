import {useMemo, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {ApplicationsDataTable} from './applications-data-table';
import {createColumns} from './columns';
import {RefreshCw} from 'lucide-react';
import type {App} from '@/types/app.types';

interface ApplicationsTableProps {
    data: App[];
    total: number;
    isLoading: boolean;
    onDelete: (id: string) => void;
    onRefresh: () => void;
}

export function ApplicationsTable({data, total, isLoading, onDelete, onRefresh}: ApplicationsTableProps) {
    const navigate = useNavigate();
    const columns = useMemo(() => createColumns(onDelete, navigate), [onDelete, navigate]);
    const [typeFilter, setTypeFilter] = useState<string>('all');

    const filteredData = useMemo(() => {
        if (typeFilter === 'all') return data;
        return data.filter((app) => app.type === typeFilter);
    }, [data, typeFilter]);

    const hasOriginalData = data && data.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-2">
                        <CardTitle>All Applications</CardTitle>
                        <CardDescription>
                            {total || 0} application{total !== 1 ? 's' : ''} registered
                        </CardDescription>
                    </div>
                    {!isLoading && (
                        <Button variant="outline" size="icon" onClick={onRefresh} className="cursor-pointer">
                            <RefreshCw className="h-4 w-4" />
                        </Button>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                {hasOriginalData ? (
                    <ApplicationsDataTable
                        columns={columns}
                        data={filteredData}
                        searchPlaceholder="Search applications..."
                        typeFilter={typeFilter}
                        onTypeFilterChange={setTypeFilter}
                    />
                ) : (
                    <ApplicationsDataTable
                        columns={columns}
                        data={filteredData}
                        searchPlaceholder="Search applications..."
                        hideSearch
                    />
                )}
            </CardContent>
        </Card>
    );
}
