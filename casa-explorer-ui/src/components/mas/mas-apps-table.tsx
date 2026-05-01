/**
 * Copyright 2026 Copyright 2026 Cisco Systems, Inc. and its affiliates
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {useCallback, useMemo, useState} from 'react';
import type React from 'react';
import {useNavigate} from 'react-router-dom';
import {Input} from '@/components/ui/input';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {DataTable} from '@/components/ui/data-table';
import type {ColumnDef} from '@tanstack/react-table';
import {
    ArrowUpDown,
    Search,
    List,
    LayoutGrid,
    Network,
    AppWindow,
    Wrench,
    Copy,
    Info,
    Bot,
    Server,
    X
} from 'lucide-react';
import {TextHover} from '@/components/ui/text-hover';
import {Button} from '@/components/ui/button';
import {Card} from '@/components/ui/card';
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog';
import {Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetClose} from '@/components/ui/sheet';
import {MASGraphView} from '@/components/mas/mas-graph-view';
import {toast} from 'sonner';
import type {MAS} from '@/types/mas.types';
import type {App, AppType, Tool} from '@/types/app.types';
import {AppTypeBadge, APP_TYPE_LABELS, APP_TYPE_CLASSES} from '@/components/ui/app-type-badge';

const APP_TYPE_ICONS: Record<AppType, React.ElementType> = {
    agent: AppWindow,
    client: Network,
    mcp_server: Wrench
};

const APP_TYPE_DETAIL_ICONS: Record<AppType, React.ElementType> = {
    agent: Bot,
    client: AppWindow,
    mcp_server: Server
};

const APP_TYPE_ICON_COLORS: Record<AppType, string> = {
    agent: 'text-purple-400',
    client: 'text-blue-400',
    mcp_server: 'text-cyan-400'
};

function safeJsonPretty(raw: string | undefined | null): string {
    if (!raw) return '{}';
    try {
        return JSON.stringify(JSON.parse(raw), null, 2);
    } catch {
        return raw;
    }
}

interface MASAppsTableProps {
    mas: MAS;
    apps: App[];
}

export function MASAppsTable({mas, apps}: MASAppsTableProps) {
    const navigate = useNavigate();
    const [view, setView] = useState<'table' | 'grid' | 'graph'>('table');
    const [search, setSearch] = useState('');
    const [selectedTypes, setSelectedTypes] = useState<Set<AppType>>(new Set(['agent', 'client', 'mcp_server']));
    const [selectedApp, setSelectedApp] = useState<App | null>(null);
    const [sheetTab, setSheetTab] = useState('info');
    const [toolSearch, setToolSearch] = useState('');
    const [selectedTool, setSelectedTool] = useState<Tool | null>(null);

    const openApp = useCallback((app: App) => {
        setSelectedApp(app);
        setSheetTab('info');
        setToolSearch('');
    }, []);

    const columns = useMemo<ColumnDef<App>[]>(
        () => [
            {
                accessorKey: 'name',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Name <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <TextHover text={row.getValue('name')}>
                            <span
                                className="font-semibold cursor-pointer underline decoration-dotted hover:decoration-solid"
                                onClick={() => openApp(row.original)}
                            >
                                {row.getValue('name')}
                            </span>
                        </TextHover>
                    </div>
                )
            },
            {
                accessorKey: 'type',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Type <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const type = row.getValue('type') as AppType;
                    return (
                        <div className="flex justify-center">
                            <AppTypeBadge type={type} />
                        </div>
                    );
                }
            },
            {
                accessorKey: 'base_url',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Base URL <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <TextHover text={row.getValue('base_url')} maxWidth="max-w-sm">
                            <span className="text-sm text-muted-foreground">{row.getValue('base_url')}</span>
                        </TextHover>
                    </div>
                )
            }
        ],
        [openApp]
    );

    const toggleType = useCallback((type: AppType) => {
        setSelectedTypes((prev) => {
            const next = new Set(prev);
            if (next.has(type)) next.delete(type);
            else next.add(type);
            return next;
        });
    }, []);

    const filteredData = useMemo(() => {
        let result = apps || [];
        result = result.filter((app) => selectedTypes.has(app.type));
        if (search)
            result = result.filter(
                (app) =>
                    app.name.toLowerCase().includes(search.toLowerCase()) ||
                    app.base_url.toLowerCase().includes(search.toLowerCase())
            );
        return result;
    }, [apps, selectedTypes, search]);

    const hasData = apps && apps.length > 0;

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`${label} copied to clipboard`);
    };

    const hasTools = selectedApp?.type === 'mcp_server' && (selectedApp?.tools?.length ?? 0) > 0;

    const filteredTools =
        selectedApp?.tools?.filter(
            (t) =>
                !toolSearch ||
                t.name.toLowerCase().includes(toolSearch.toLowerCase()) ||
                (t.description ?? '').toLowerCase().includes(toolSearch.toLowerCase())
        ) ?? [];

    return (
        <>
            <div className="w-full">
                <div className="mt-4 space-y-3">
                    {hasData && (
                        <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2 flex-1">
                                <div className="relative max-w-xs w-full">
                                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                    <Input
                                        placeholder="Search agentic services..."
                                        value={search}
                                        onChange={(e) => setSearch(e.target.value)}
                                        className="pl-9"
                                    />
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => toggleType('agent')}
                                    className={
                                        selectedTypes.has('agent')
                                            ? 'border-purple-500/50 text-purple-300 bg-purple-500/10'
                                            : 'text-muted-foreground'
                                    }
                                >
                                    <Bot className="h-3 w-3" />
                                    Agent
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => toggleType('client')}
                                    className={
                                        selectedTypes.has('client')
                                            ? 'border-blue-500/50 text-blue-300 bg-blue-500/10'
                                            : 'text-muted-foreground'
                                    }
                                >
                                    <AppWindow className="h-3 w-3" />
                                    Client
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => toggleType('mcp_server')}
                                    className={
                                        selectedTypes.has('mcp_server')
                                            ? 'border-cyan-500/50 text-cyan-300 bg-cyan-500/10'
                                            : 'text-muted-foreground'
                                    }
                                >
                                    <Server className="h-3 w-3" />
                                    MCP Server
                                </Button>
                            </div>
                            <div className="flex items-center gap-2">
                                <ToggleGroup
                                    type="single"
                                    value={view}
                                    onValueChange={(v) => v && setView(v as 'table' | 'grid' | 'graph')}
                                    variant="outline"
                                >
                                    <ToggleGroupItem value="table" aria-label="Table view">
                                        <List className="h-4 w-4" />
                                    </ToggleGroupItem>
                                    <ToggleGroupItem value="grid" aria-label="Grid view">
                                        <LayoutGrid className="h-4 w-4" />
                                    </ToggleGroupItem>
                                    <ToggleGroupItem value="graph" aria-label="Graph view">
                                        <Network className="h-4 w-4" />
                                    </ToggleGroupItem>
                                </ToggleGroup>
                            </div>
                        </div>
                    )}
                    {view !== 'graph' && (
                        <>
                            {view === 'grid' ? (
                                hasData ? (
                                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                        {filteredData.map((app) => {
                                            const Icon = APP_TYPE_ICONS[app.type];
                                            return (
                                                <Card
                                                    key={app.id}
                                                    className="cursor-pointer hover:bg-accent/50 transition-colors p-0"
                                                    onClick={() => openApp(app)}
                                                >
                                                    <div className="flex items-center gap-3 p-3">
                                                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10">
                                                            <Icon className="h-4 w-4 text-primary" />
                                                        </div>
                                                        <div className="min-w-0 flex-1">
                                                            <div className="flex items-center gap-2">
                                                                <p className="text-sm font-semibold truncate">
                                                                    {app.name}
                                                                </p>
                                                                <AppTypeBadge type={app.type} className="shrink-0" />
                                                            </div>
                                                            <p className="text-xs text-muted-foreground truncate">
                                                                {app.base_url}
                                                            </p>
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
                                                No agentic services are registered in this MAS
                                            </p>
                                        </div>
                                    </div>
                                )
                            ) : (
                                <DataTable
                                    columns={columns}
                                    data={filteredData}
                                    hideSearch
                                    searchValue={search}
                                    onSearchChange={setSearch}
                                    onRowClick={(row) => openApp(row)}
                                />
                            )}
                        </>
                    )}
                </div>
                {view === 'graph' && (
                    <div className="mt-4">
                        <MASGraphView
                            mas={mas}
                            apps={apps}
                            onAppClick={openApp}
                            searchTerm={search}
                            selectedTypes={selectedTypes}
                        />
                    </div>
                )}
            </div>

            <Sheet open={!!selectedApp} onOpenChange={(open) => !open && setSelectedApp(null)}>
                <SheetContent
                    side="right"
                    className="w-[800px] sm:max-w-[800px] flex flex-col p-0 gap-0"
                    showCloseButton={false}
                >
                    {selectedApp && (
                        <>
                            <div className="flex items-center justify-between px-6 py-3 border-b">
                                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                    Agentic service
                                </span>
                                <div className="flex items-center gap-1">
                                    <SheetClose asChild>
                                        <Button variant="ghost" size="icon" className="h-7 w-7 cursor-pointer">
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </SheetClose>
                                </div>
                            </div>
                            <SheetHeader className="px-6 pt-5 pb-0">
                                <Tabs value={sheetTab} onValueChange={setSheetTab} className="w-full">
                                    <div className="flex items-center justify-between gap-3">
                                        <div className="flex items-center gap-3 min-w-0">
                                            {(() => {
                                                const Icon = APP_TYPE_DETAIL_ICONS[selectedApp.type];
                                                return (
                                                    <div
                                                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${APP_TYPE_CLASSES[selectedApp.type]}`}
                                                    >
                                                        <Icon
                                                            className={`h-5 w-5 ${APP_TYPE_ICON_COLORS[selectedApp.type]}`}
                                                        />
                                                    </div>
                                                );
                                            })()}
                                            <div className="space-y-1 min-w-0">
                                                <SheetTitle className="text-xl">{selectedApp.name}</SheetTitle>
                                                <SheetDescription>
                                                    {APP_TYPE_LABELS[selectedApp.type]} · Agentic service
                                                </SheetDescription>
                                            </div>
                                        </div>
                                        <TabsList variant="underline" className="w-auto shrink-0 self-end">
                                            <TabsTrigger value="info">
                                                <Info className="mr-1.5 h-3.5 w-3.5" />
                                                Info
                                            </TabsTrigger>
                                            {selectedApp.type === 'mcp_server' && (
                                                <TabsTrigger value="tools">
                                                    <Wrench className="mr-1.5 h-3.5 w-3.5" />
                                                    Tools
                                                    {(selectedApp.tools?.length ?? 0) > 0 && (
                                                        <span className="ml-1.5 text-xs text-muted-foreground">
                                                            {selectedApp.tools.length}
                                                        </span>
                                                    )}
                                                </TabsTrigger>
                                            )}
                                        </TabsList>
                                    </div>
                                </Tabs>
                            </SheetHeader>

                            <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
                                {sheetTab === 'info' && (
                                    <div className="rounded-lg border bg-card p-5">
                                        <div className="grid grid-cols-2 gap-x-6 gap-y-5">
                                            <div className="space-y-1.5">
                                                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                    Type
                                                </p>
                                                <div className="flex items-center gap-2">
                                                    {(() => {
                                                        const Icon = APP_TYPE_DETAIL_ICONS[selectedApp.type];
                                                        return (
                                                            <Icon
                                                                className={`h-4 w-4 ${APP_TYPE_ICON_COLORS[selectedApp.type]}`}
                                                            />
                                                        );
                                                    })()}
                                                    <AppTypeBadge type={selectedApp.type} />
                                                </div>
                                            </div>

                                            <div className="space-y-1.5">
                                                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                    Base URL
                                                </p>
                                                <div className="flex items-center gap-1.5">
                                                    <code className="text-xs font-mono bg-muted px-2 py-1 rounded truncate max-w-[320px]">
                                                        {selectedApp.base_url}
                                                    </code>
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-6 w-6 flex-shrink-0 cursor-pointer"
                                                        onClick={() =>
                                                            copyToClipboard(selectedApp.base_url, 'Base URL')
                                                        }
                                                    >
                                                        <Copy className="h-3 w-3" />
                                                    </Button>
                                                </div>
                                            </div>

                                            <div className="space-y-1.5 col-span-2">
                                                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                    CIMD Endpoint
                                                </p>
                                                <div className="flex items-center gap-1.5">
                                                    {selectedApp.client_id_metadata_url ? (
                                                        <a
                                                            href={selectedApp.client_id_metadata_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-xs font-mono bg-muted px-2 py-1 rounded truncate max-w-[420px] hover:underline"
                                                        >
                                                            {selectedApp.client_id_metadata_url}
                                                        </a>
                                                    ) : (
                                                        <code className="text-xs font-mono bg-muted px-2 py-1 rounded truncate max-w-[420px]">
                                                            {selectedApp.id}
                                                        </code>
                                                    )}
                                                    {(selectedApp.client_id_metadata_url ?? selectedApp.id) && (
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-6 w-6 flex-shrink-0 cursor-pointer"
                                                            onClick={() =>
                                                                copyToClipboard(
                                                                    selectedApp.client_id_metadata_url ?? selectedApp.id!,
                                                                    'CIMD Endpoint'
                                                                )
                                                            }
                                                        >
                                                            <Copy className="h-3 w-3" />
                                                        </Button>
                                                    )}
                                                </div>
                                            </div>

                                            {selectedApp.mas && (
                                                <div className="space-y-1.5 col-span-2">
                                                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                                        Multi-Agent System
                                                    </p>
                                                    <div
                                                        className="flex items-center gap-2 cursor-pointer group w-fit"
                                                        onClick={() => navigate(`/mas/${selectedApp.mas!.id}`)}
                                                    >
                                                        <Network className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                                        <div className="flex flex-col">
                                                            <span className="text-sm font-medium underline decoration-dotted group-hover:decoration-solid">
                                                                {selectedApp.mas.name}
                                                            </span>
                                                            <span className="font-mono text-xs text-muted-foreground">
                                                                {selectedApp.mas.id}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {sheetTab === 'tools' && selectedApp.type === 'mcp_server' && (
                                    <div className="rounded-lg border bg-card p-5 space-y-3">
                                        {!hasTools ? (
                                            <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                                                <Wrench className="h-10 w-10 opacity-40" />
                                                <div className="text-center">
                                                    <p className="text-sm font-medium">No tools defined</p>
                                                    <p className="text-xs mt-1">
                                                        This MCP server has no tools configured
                                                    </p>
                                                </div>
                                            </div>
                                        ) : (
                                            <>
                                                <div className="relative">
                                                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                                    <Input
                                                        placeholder="Search tools..."
                                                        value={toolSearch}
                                                        onChange={(e) => setToolSearch(e.target.value)}
                                                        className="pl-9"
                                                    />
                                                </div>
                                                <div className="space-y-2">
                                                    {filteredTools.map((tool) => (
                                                        <div
                                                            key={tool.id}
                                                            className="p-4 rounded-lg border hover:bg-accent/50 transition-colors cursor-pointer"
                                                            onClick={() => setSelectedTool(tool)}
                                                        >
                                                            <div className="flex items-start gap-3">
                                                                <div className="mt-0.5 p-2 rounded-md bg-primary/10 flex-shrink-0">
                                                                    <Wrench className="h-4 w-4 text-primary" />
                                                                </div>
                                                                <div className="flex-1 min-w-0">
                                                                    <p className="font-semibold text-foreground">
                                                                        {tool.name}
                                                                    </p>
                                                                    {tool.description && (
                                                                        <p className="text-sm text-muted-foreground mt-1">
                                                                            {tool.description}
                                                                        </p>
                                                                    )}
                                                                    {tool.scopes && tool.scopes.length > 0 && (
                                                                        <div className="flex flex-wrap gap-1.5 mt-2">
                                                                            {tool.scopes.map((scope) => (
                                                                                <span
                                                                                    key={scope.id}
                                                                                    className="inline-flex items-center px-2.5 py-1 rounded-md bg-secondary text-secondary-foreground text-xs font-medium"
                                                                                >
                                                                                    {scope.name}
                                                                                </span>
                                                                            ))}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </SheetContent>
            </Sheet>

            <Dialog open={!!selectedTool} onOpenChange={(open) => !open && setSelectedTool(null)}>
                <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <Wrench className="h-5 w-5" />
                            {selectedTool?.name}
                        </DialogTitle>
                        <DialogDescription>{selectedTool?.description}</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-6 mt-4">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold">Input Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="cursor-pointer h-8 px-2"
                                    onClick={() => {
                                        if (selectedTool?.input_schema) {
                                            navigator.clipboard.writeText(selectedTool.input_schema);
                                            toast.success('Input schema copied');
                                        }
                                    }}
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>{safeJsonPretty(selectedTool?.input_schema)}</code>
                            </pre>
                        </div>
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold">Output Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="cursor-pointer h-8 px-2"
                                    onClick={() => {
                                        if (selectedTool?.output_schema) {
                                            navigator.clipboard.writeText(selectedTool.output_schema);
                                            toast.success('Output schema copied');
                                        }
                                    }}
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>{safeJsonPretty(selectedTool?.output_schema)}</code>
                            </pre>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
}
