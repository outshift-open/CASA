import {useMemo, useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {MASDataTable} from './mas-data-table';
import {createMASColumns} from './mas-columns';
import {RefreshCw} from 'lucide-react';
import type {MAS} from '@/types/mas.types';
import {masService} from '@/services/mas.service';

interface MASTableProps {
    data: MAS[];
    total: number;
    isLoading: boolean;
    onDelete: (id: string, appCount: number) => void;
    onRefresh: () => void;
}

export function MASTable({data, total, isLoading, onDelete, onRefresh}: MASTableProps) {
    const navigate = useNavigate();
    const [appCounts, setAppCounts] = useState<Record<string, number>>({});
    const [countsLoading, setCountsLoading] = useState<Record<string, boolean>>({});
    const [countsError, setCountsError] = useState<Record<string, boolean>>({});

    // Fetch app counts for each MAS
    useEffect(() => {
        if (!data || data.length === 0) return;

        const fetchAppCounts = async () => {
            // Initialize loading state for all MAS
            const loadingState: Record<string, boolean> = {};
            data.forEach((mas) => {
                loadingState[mas.id] = true;
            });
            setCountsLoading(loadingState);

            const counts: Record<string, number> = {};
            const errors: Record<string, boolean> = {};
            const loading: Record<string, boolean> = {};

            for (const mas of data) {
                try {
                    const apps = await masService.getMASApps(mas.id);
                    counts[mas.id] = apps.length;
                    errors[mas.id] = false;
                } catch {
                    counts[mas.id] = 0;
                    errors[mas.id] = true;
                }
                loading[mas.id] = false;
            }

            setAppCounts(counts);
            setCountsError(errors);
            setCountsLoading(loading);
        };

        fetchAppCounts();
    }, [data]);

    const columns = useMemo(
        () => createMASColumns(onDelete, navigate, appCounts, countsLoading, countsError),
        [onDelete, navigate, appCounts, countsLoading, countsError]
    );
    const hasData = data && data.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-2">
                        <CardTitle>Multi-Agent Systems</CardTitle>
                        <CardDescription>
                            {total || 0} {total === 1 ? 'system' : 'systems'} registered
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
