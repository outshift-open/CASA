import {useMemo, useState} from 'react';
import type React from 'react';
import {useNavigate} from 'react-router-dom';
import {Input} from '@/components/ui/input';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {ApplicationsDataTable} from '@/components/apps/applications-data-table';
import {createColumns} from '@/components/apps/columns';
import {Search, List, LayoutGrid, AppWindow, Network, Wrench} from 'lucide-react';
import {Badge} from '@/components/ui/badge';
import {Card} from '@/components/ui/card';
import type {App, AppType} from '@/types/app.types';

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agent',
    client: 'Client',
    mcp_server: 'MCP Server'
};

const APP_TYPE_VARIANTS: Record<AppType, 'default' | 'secondary' | 'outline'> = {
    agent: 'default',
    client: 'secondary',
    mcp_server: 'outline'
};

const APP_TYPE_ICONS: Record<AppType, React.ElementType> = {
    agent: AppWindow,
    client: Network,
    mcp_server: Wrench
};

interface MASAppsTableProps {
    apps: App[];
}

export function MASAppsTable({apps}: MASAppsTableProps) {
    const navigate = useNavigate();
    const [view, setView] = useState<'table' | 'grid'>('table');
    const [search, setSearch] = useState('');
    const [typeFilter, setTypeFilter] = useState<string>('all');

    const columns = useMemo(() => {
        const allColumns = createColumns(navigate);
        return allColumns.filter((col) => col.id !== 'actions' && 'accessorKey' in col && col.accessorKey !== 'mas_id');
    }, [navigate]);

    const filteredData = useMemo(() => {
        let result = apps || [];
        if (typeFilter !== 'all') result = result.filter((app) => app.type === typeFilter);
        if (search)
            result = result.filter(
                (app) =>
                    app.name.toLowerCase().includes(search.toLowerCase()) ||
                    app.base_url.toLowerCase().includes(search.toLowerCase())
            );
        return result;
    }, [apps, typeFilter, search]);

    const hasData = apps && apps.length > 0;

    return (
        <div className="space-y-3">
            {hasData && (
                <div className="flex items-center justify-between gap-2">
                    <div className="relative w-1/2">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Search applications..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-9"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <Select value={typeFilter} onValueChange={setTypeFilter}>
                            <SelectTrigger className="w-[140px]">
                                <SelectValue placeholder="All types" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All types</SelectItem>
                                <SelectItem value="agent">Agent</SelectItem>
                                <SelectItem value="client">Client</SelectItem>
                                <SelectItem value="mcp_server">MCP Server</SelectItem>
                            </SelectContent>
                        </Select>
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
                </div>
            )}
            {view === 'grid' ? (
                hasData ? (
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {filteredData.map((app) => {
                            const Icon = APP_TYPE_ICONS[app.type];
                            return (
                                <Card
                                    key={app.id}
                                    className="cursor-pointer hover:bg-accent/50 transition-colors"
                                    onClick={() => navigate(`/apps/${app.id}`)}
                                >
                                    <div className="flex items-center gap-3 p-3">
                                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10">
                                            <Icon className="h-4 w-4 text-primary" />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <div className="flex items-center gap-2">
                                                <p className="text-sm font-semibold truncate">{app.name}</p>
                                                <Badge
                                                    variant={APP_TYPE_VARIANTS[app.type]}
                                                    className="text-xs shrink-0"
                                                >
                                                    {APP_TYPE_LABELS[app.type]}
                                                </Badge>
                                            </div>
                                            <p className="text-xs text-muted-foreground truncate">{app.base_url}</p>
                                        </div>
                                        <div className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
                                            <Wrench className="h-3 w-3" />
                                            <span>{app.tools.length}</span>
                                        </div>
                                    </div>
                                </Card>
                            );
                        })}
                    </div>
                ) : (
                    <div className="py-12 text-center text-sm text-muted-foreground">No applications found</div>
                )
            ) : (
                <ApplicationsDataTable
                    columns={columns}
                    data={filteredData}
                    hideSearch
                    searchValue={search}
                    onSearchChange={setSearch}
                    typeFilter={typeFilter}
                    onTypeFilterChange={setTypeFilter}
                />
            )}
        </div>
    );
}
