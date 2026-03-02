import {useMemo} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {ScopesDataTable} from './scopes-data-table';
import {createColumns} from './columns';
import {RefreshCw} from 'lucide-react';
import type {Scope} from '@/types/scope.types';

interface ScopesTableProps {
    data: Scope[];
    total: number;
    isLoading: boolean;
    onDelete: (id: string) => void;
    onRefresh: () => void;
}

export function ScopesTable({data, total, isLoading, onDelete, onRefresh}: ScopesTableProps) {
    const navigate = useNavigate();
    const columns = useMemo(() => createColumns(onDelete, navigate), [onDelete, navigate]);

    const hasData = data && data.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-2">
                        <CardTitle>All Scopes</CardTitle>
                        <CardDescription>
                            {total || 0} scope{total !== 1 ? 's' : ''} registered
                        </CardDescription>
                    </div>
                    {!isLoading && (
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="outline"
                                    size="icon"
                                    onClick={onRefresh}
                                    className="cursor-pointer"
                                    aria-label="Refresh scopes"
                                >
                                    <RefreshCw className="h-4 w-4" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Refresh scopes</p>
                            </TooltipContent>
                        </Tooltip>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                <ScopesDataTable
                    columns={columns}
                    data={data}
                    searchPlaceholder="Search scopes..."
                    hideSearch={!hasData}
                />
            </CardContent>
        </Card>
    );
}
