import {useMemo, useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {MASDataTable} from './mas-data-table';
import {createMASColumns} from './mas-columns';
import {RefreshCw} from 'lucide-react';
import type {MAS} from '@/types/mas.types';
import type {App} from '@/types/app.types';
import type {Scope} from '@/types/scope.types';
import {masService} from '@/services/mas.service';
import {scopeService} from '@/services/scope.service';

interface MASTableProps {
    data: MAS[];
    total: number;
    isLoading: boolean;
    onDelete: (id: string, appCount: number) => void;
    onRefresh: () => void;
}

export function MASTable({data, total, isLoading, onDelete, onRefresh}: MASTableProps) {
    const navigate = useNavigate();
    const [masApps, setMasApps] = useState<Record<string, App[]>>({});
    const [masScopes, setMasScopes] = useState<Record<string, Scope[]>>({});
    const [countsLoading, setCountsLoading] = useState<Record<string, boolean>>({});
    const [countsError, setCountsError] = useState<Record<string, boolean>>({});

    // Fetch apps and scopes for each MAS
    useEffect(() => {
        if (!data || data.length === 0) return;

        const fetchData = async () => {
            // Initialize loading state for all MAS
            const loadingState: Record<string, boolean> = {};
            data.forEach((mas) => {
                loadingState[mas.id] = true;
            });
            setCountsLoading(loadingState);

            const appsData: Record<string, App[]> = {};
            const scopesData: Record<string, Scope[]> = {};
            const errors: Record<string, boolean> = {};
            const loading: Record<string, boolean> = {};

            for (const mas of data) {
                try {
                    const [apps, scopes] = await Promise.all([
                        masService.getMASApps(mas.id),
                        scopeService.getMASScopes(mas.id)
                    ]);
                    appsData[mas.id] = apps;
                    scopesData[mas.id] = scopes;
                    errors[mas.id] = false;
                } catch {
                    appsData[mas.id] = [];
                    scopesData[mas.id] = [];
                    errors[mas.id] = true;
                }
                loading[mas.id] = false;
            }

            setMasApps(appsData);
            setMasScopes(scopesData);
            setCountsError(errors);
            setCountsLoading(loading);
        };

        fetchData();
    }, [data]);

    const columns = useMemo(
        () => createMASColumns(onDelete, navigate, masApps, masScopes, countsLoading, countsError),
        [onDelete, navigate, masApps, masScopes, countsLoading, countsError]
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
