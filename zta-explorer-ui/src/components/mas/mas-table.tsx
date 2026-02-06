import {useMemo} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {MASDataTable} from './mas-data-table';
import {createMASColumns} from './mas-columns';
import {RefreshCw} from 'lucide-react';
import type {MAS} from '@/types/mas.types';

interface MASTableProps {
    data: MAS[];
    total: number;
    isLoading: boolean;
    onEdit: (mas: MAS) => void;
    onDelete: (id: string) => void;
    onRefresh: () => void;
}

export function MASTable({data, total, isLoading, onEdit, onDelete, onRefresh}: MASTableProps) {
    const navigate = useNavigate();
    const columns = useMemo(() => createMASColumns(onEdit, onDelete, navigate), [onEdit, onDelete, navigate]);
    const hasData = data && data.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-2">
                        <CardTitle>Multi-Agent Systems</CardTitle>
                        <CardDescription>
                            {total || 0} MAS {total !== 1 ? 'registered' : 'registered'}
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
                {hasData ? (
                    <MASDataTable columns={columns} data={data} searchPlaceholder="Search MAS..." />
                ) : (
                    <MASDataTable columns={columns} data={data} searchPlaceholder="Search MAS..." hideSearch />
                )}
            </CardContent>
        </Card>
    );
}
