import {useMemo} from 'react';
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
    onEdit: (app: App) => void;
    onDelete: (id: string) => void;
    onRefresh: () => void;
}

export function ApplicationsTable({data, total, isLoading, onEdit, onDelete, onRefresh}: ApplicationsTableProps) {
    const columns = useMemo(() => createColumns(onEdit, onDelete), [onEdit, onDelete]);

    return (
        <Card>
            <CardHeader>
                <div className="flex items-start justify-between">
                    <div>
                        <CardTitle>All Applications</CardTitle>
                        <CardDescription>
                            {total || 0} application{total !== 1 ? 's' : ''} registered
                        </CardDescription>
                    </div>
                    <Button variant="outline" size="icon" onClick={onRefresh} disabled={isLoading}>
                        <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>
                </div>
            </CardHeader>
            <CardContent>
                <ApplicationsDataTable columns={columns} data={data} searchPlaceholder="Search applications..." />
            </CardContent>
        </Card>
    );
}
