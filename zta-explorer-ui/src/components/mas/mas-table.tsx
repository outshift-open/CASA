import {useMemo, useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {MASDataTable} from './mas-data-table';
import {createMASColumns} from './mas-columns';
import {RefreshCw, LayoutGrid, List, Network, AppWindow, Tags, AlertCircle, Loader2, Search} from 'lucide-react';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import type {MAS} from '@/types/mas.types';
import type {App} from '@/types/app.types';
import type {Scope} from '@/types/scope.types';
import {masService} from '@/services/mas.service';
import {scopeService} from '@/services/scope.service';

interface MASTableProps {
    data: MAS[];
    total: number;
    isLoading: boolean;
    onRefresh: () => void;
}

export function MASTable({data, total, isLoading, onRefresh}: MASTableProps) {
    const navigate = useNavigate();
    const [view, setView] = useState<'table' | 'grid'>('table');
    const [search, setSearch] = useState('');
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
        () => createMASColumns(navigate, masApps, masScopes, countsLoading, countsError),
        [navigate, masApps, masScopes, countsLoading, countsError]
    );
    const filteredData = search
        ? data.filter(
              (mas) =>
                  mas.name.toLowerCase().includes(search.toLowerCase()) ||
                  mas.id.toLowerCase().includes(search.toLowerCase())
          )
        : data;
    const hasData = data && data.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-center justify-between">
                    <div className="space-y-2">
                        <CardTitle>Multi-Agent Systems</CardTitle>
                        <CardDescription>
                            {total || 0} {total === 1 ? 'system' : 'systems'} registered
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
                                    aria-label="Refresh MAS"
                                >
                                    <RefreshCw className="h-4 w-4" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Refresh MAS</p>
                            </TooltipContent>
                        </Tooltip>
                    )}
                </div>
                {hasData && (
                    <div className="flex items-center justify-between gap-2 mt-2">
                        <div className="relative w-1/2">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                placeholder="Search MAS..."
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
                            {filteredData.map((mas) => {
                                const apps = masApps[mas.id] ?? [];
                                const scopes = masScopes[mas.id] ?? [];
                                const loading = countsLoading[mas.id];
                                const hasError = countsError[mas.id];
                                return (
                                    <Card
                                        key={mas.id}
                                        className="cursor-pointer hover:bg-accent/50 transition-colors"
                                        onClick={() => navigate(`/mas/${mas.id}`)}
                                    >
                                        <div className="flex items-center gap-3 p-3">
                                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10">
                                                <Network className="h-4 w-4 text-primary" />
                                            </div>
                                            <div className="min-w-0 flex-1">
                                                <p className="text-sm font-semibold truncate">{mas.name}</p>
                                                <p className="text-xs text-muted-foreground font-mono truncate">
                                                    {mas.id}
                                                </p>
                                            </div>
                                            <div className="flex items-center gap-2 shrink-0">
                                                {loading ? (
                                                    <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                                                ) : hasError ? (
                                                    <AlertCircle className="h-3.5 w-3.5 text-destructive" />
                                                ) : (
                                                    <>
                                                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                                            <AppWindow className="h-3 w-3" />
                                                            <span>{apps.length}</span>
                                                        </div>
                                                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                                            <Tags className="h-3 w-3" />
                                                            <span>{scopes.length}</span>
                                                        </div>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    </Card>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-12 gap-3">
                            <Network className="h-10 w-10 text-muted-foreground opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No Multi-Agent Systems</p>
                                <p className="text-xs text-muted-foreground mt-1">Register a MAS to get started</p>
                            </div>
                        </div>
                    )
                ) : (
                    <MASDataTable
                        columns={columns}
                        data={data}
                        hideSearch
                        searchValue={search}
                        onSearchChange={setSearch}
                    />
                )}
            </CardContent>
        </Card>
    );
}
