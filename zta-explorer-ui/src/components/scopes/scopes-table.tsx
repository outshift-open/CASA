import {useMemo, useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {ScopesDataTable} from './scopes-data-table';
import {createColumns} from './columns';
import {RefreshCw} from 'lucide-react';
import type {Scope} from '@/types/scope.types';
import type {MAS} from '@/types/mas.types';
import {masService} from '@/services/mas.service';

interface ScopesTableProps {
    data: Scope[];
    total: number;
    isLoading: boolean;
    onDelete: (id: string) => void;
    onRefresh: () => void;
}

export function ScopesTable({data, total, isLoading, onDelete, onRefresh}: ScopesTableProps) {
    const navigate = useNavigate();
    const [enrichedScopes, setEnrichedScopes] = useState<Scope[]>([]);

    // Fetch MAS data for each scope
    useEffect(() => {
        const fetchMASData = async () => {
            if (!data || data.length === 0) {
                setEnrichedScopes([]);
                return;
            }

            const masCache: Record<string, MAS> = {};

            const enriched = await Promise.all(
                data.map(async (scope) => {
                    // Skip if already has MAS data
                    if (scope.mas) {
                        return scope;
                    }

                    // Check cache first
                    if (masCache[scope.mas_id]) {
                        return {...scope, mas: masCache[scope.mas_id]};
                    }

                    // Fetch MAS data
                    try {
                        const mas = await masService.getMASById(scope.mas_id);
                        masCache[scope.mas_id] = mas;
                        return {...scope, mas};
                    } catch (error) {
                        console.error(`Failed to fetch MAS for scope ${scope.id}:`, error);
                        return scope;
                    }
                })
            );

            setEnrichedScopes(enriched);
        };

        fetchMASData();
    }, [data]);

    const columns = useMemo(() => createColumns(onDelete, navigate), [onDelete, navigate]);

    const hasData = enrichedScopes && enrichedScopes.length > 0;

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
                    data={enrichedScopes}
                    searchPlaceholder="Search scopes..."
                    hideSearch={!hasData}
                />
            </CardContent>
        </Card>
    );
}
