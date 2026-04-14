import {useMemo, useState} from 'react';
import type React from 'react';
import {Input} from '@/components/ui/input';
import {useNavigate} from 'react-router-dom';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {ApplicationsDataTable} from './applications-data-table';
import {createColumns} from './columns';
import {RefreshCw, LayoutGrid, List, AppWindow, Network, Wrench, Search} from 'lucide-react';
import type {App, AppType} from '@/types/app.types';

interface ApplicationsTableProps {
    data: App[];
    total: number;
    isLoading: boolean;
    onRefresh: () => void;
}

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

export function ApplicationsTable({data, total, isLoading, onRefresh}: ApplicationsTableProps) {
    const navigate = useNavigate();
    const columns = useMemo(() => createColumns(navigate), [navigate]);
    const [view, setView] = useState<'table' | 'grid'>('table');
    const [search, setSearch] = useState('');
    const [typeFilter, setTypeFilter] = useState<string>('all');

    const filteredData = useMemo(() => {
        let result = data;
        if (typeFilter !== 'all') result = result.filter((app) => app.type === typeFilter);
        if (search)
            result = result.filter(
                (app) =>
                    app.name.toLowerCase().includes(search.toLowerCase()) ||
                    app.base_url.toLowerCase().includes(search.toLowerCase())
            );
        return result;
    }, [data, typeFilter, search]);

    const hasOriginalData = data && data.length > 0;

    return (
        <Card>
            <CardHeader className="px-6">
                <div className="flex items-center justify-between">
                    <div className="space-y-2">
                        <CardTitle>All Agentic Services</CardTitle>
                        <CardDescription>
                            {total || 0} agentic service{total !== 1 ? 's' : ''} registered
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
                                    aria-label="Refresh agentic services"
                                >
                                    <RefreshCw className="h-4 w-4" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Refresh agentic services</p>
                            </TooltipContent>
                        </Tooltip>
                    )}
                </div>
                {hasOriginalData && (
                    <div className="flex items-center justify-between gap-2 mt-2">
                        <div className="relative w-1/2">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                placeholder="Search agentic services..."
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
            </CardHeader>
            <CardContent>
                {view === 'grid' ? (
                    hasOriginalData ? (
                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                            {filteredData.map((app) => {
                                const Icon = APP_TYPE_ICONS[app.type];
                                return (
                                    <Card
                                        key={app.id}
                                        className="cursor-pointer hover:bg-accent/50 transition-colors p-0"
                                        onClick={() => navigate(`/agentic-services/${app.id}`)}
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
                        <div className="flex flex-col items-center justify-center py-12 gap-3">
                            <AppWindow className="h-10 w-10 text-muted-foreground opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No agentic services found</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Add agents, clients or MCP servers to a MAS
                                </p>
                            </div>
                        </div>
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
            </CardContent>
        </Card>
    );
}
