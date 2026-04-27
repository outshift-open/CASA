import {useMemo, useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {ScopesDataTable} from './scopes-data-table';
import {createColumns} from './columns';
import {RefreshCw, LayoutGrid, List, Tags, Network, Search} from 'lucide-react';
import type {Scope} from '@/types/scope.types';
import type {MAS} from '@/types/mas.types';
import {masService} from '@/services/mas.service';

interface ScopesTableProps {
    data: Scope[];
    total: number;
    isLoading: boolean;
    onRefresh: () => void;
}

export function ScopesTable({data, total, isLoading, onRefresh}: ScopesTableProps) {
    const navigate = useNavigate();
    const [view, setView] = useState<'table' | 'grid'>('table');
    const [search, setSearch] = useState('');
    const [enrichedScopes, setEnrichedScopes] = useState<Scope[]>([]);

    useEffect(() => {
        const fetchMASData = async () => {
            if (!data || data.length === 0) {
                setEnrichedScopes([]);
                return;
            }

            const masCache: Record<string, MAS> = {};

            const enriched = await Promise.all(
                data.map(async (scope) => {
                    if (scope.mas) return scope;
                    if (masCache[scope.mas_id]) return {...scope, mas: masCache[scope.mas_id]};
                    try {
                        const mas = await masService.getMASById(scope.mas_id);
                        masCache[scope.mas_id] = mas;
                        return {...scope, mas};
                    } catch {
                        return scope;
                    }
                })
            );

            setEnrichedScopes(enriched);
        };

        fetchMASData();
    }, [data]);

    const columns = useMemo(() => createColumns(navigate), [navigate]);

    const filteredScopes = search
        ? enrichedScopes.filter(
              (s) =>
                  s.name.toLowerCase().includes(search.toLowerCase()) ||
                  s.id.toLowerCase().includes(search.toLowerCase())
          )
        : enrichedScopes;

    const hasData = enrichedScopes.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-center justify-between">
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
                {hasData && (
                    <div className="flex items-center justify-between gap-2 mt-2">
                        <div className="relative w-1/2">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                placeholder="Search scopes..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                        <ToggleGroup
                            type="single"
                            value={view}
                            onValueChange={(v) => v && setView(v as 'table' | 'grid')}
                            variant="outline"
                        >
                            <ToggleGroupItem value="table" aria-label="Table view">
                                <List className="h-4 w-4" />
                            </ToggleGroupItem>
                            <ToggleGroupItem value="grid" aria-label="Grid view">
                                <LayoutGrid className="h-4 w-4" />
                            </ToggleGroupItem>
                        </ToggleGroup>
                    </div>
                )}
            </CardHeader>
            <CardContent>
                {view === 'grid' ? (
                    hasData ? (
                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                            {filteredScopes.map((scope) => (
                                <Card
                                    key={scope.id}
                                    className="cursor-pointer hover:bg-accent/50 transition-colors p-0"
                                    onClick={() => navigate(`/scopes/${scope.id}`)}
                                >
                                    <div className="flex items-center gap-3 p-3">
                                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10">
                                            <Tags className="h-4 w-4 text-primary" />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <p className="text-sm font-semibold truncate">{scope.name}</p>
                                            <p className="text-xs text-muted-foreground font-mono truncate">
                                                {scope.id}
                                            </p>
                                        </div>
                                        {scope.mas && (
                                            <div className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
                                                <Network className="h-3 w-3" />
                                                <span className="truncate max-w-[80px]">{scope.mas.name}</span>
                                            </div>
                                        )}
                                    </div>
                                </Card>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-12 gap-3">
                            <Tags className="h-10 w-10 text-muted-foreground opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No scopes found</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Create scopes to control MAS authorization
                                </p>
                            </div>
                        </div>
                    )
                ) : (
                    <ScopesDataTable
                        columns={columns}
                        data={enrichedScopes}
                        hideSearch
                        searchValue={search}
                        onSearchChange={setSearch}
                    />
                )}
            </CardContent>
        </Card>
    );
}
