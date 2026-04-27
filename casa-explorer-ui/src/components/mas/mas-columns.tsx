import {ColumnDef} from '@tanstack/react-table';
import {Button} from '@/components/ui/button';
import {TextHover} from '@/components/ui/text-hover';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {ArrowUpDown, Loader2, AlertCircle, AppWindow, Activity, CheckCircle2, XCircle} from 'lucide-react';
import type {MAS} from '@/types/mas.types';
import type {App, AppType} from '@/types/app.types';
import {DateHover} from '@/components/ui/date-hover';

export interface MASTraceCounts {
    traces: number;
    allowed: number;
    denied: number;
}

export const APP_TYPE_LABELS: Record<AppType, string> = {
    client: 'Client',
    agent: 'Agent',
    mcp_server: 'MCP'
};

export const APP_TYPE_CLASSES: Record<AppType, string> = {
    client: 'bg-blue-600 text-white',
    agent: 'bg-purple-600 text-white',
    mcp_server: 'bg-cyan-600 text-white'
};

export const createMASColumns = (
    navigate: (path: string) => void,
    masApps: Record<string, App[]> = {},
    countsLoading: Record<string, boolean> = {},
    countsError: Record<string, boolean> = {},
    traceCounts: Record<string, MASTraceCounts> = {},
    traceCountsLoading: Record<string, boolean> = {}
): ColumnDef<MAS>[] => [
    {
        accessorKey: 'name',
        header: ({column}) => (
            <div className="flex justify-center">
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                    className="cursor-pointer px-0 font-medium"
                >
                    Name
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({row}) => {
            const name = row.getValue('name') as string;
            return (
                <div className="flex justify-center">
                    <div
                        className="font-medium cursor-pointer hover:underline"
                        onClick={() => navigate(`/mas/${row.original.id}`)}
                    >
                        {name}
                    </div>
                </div>
            );
        }
    },
    {
        accessorKey: 'apps',
        header: ({column}) => (
            <div className="flex justify-center">
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                    className="cursor-pointer px-0 font-medium"
                >
                    Agentic Services
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({row}) => {
            const masId = row.original.id;
            const isLoading = countsLoading[masId];
            const hasError = countsError[masId];
            const apps = masApps[masId] ?? [];
            const count = apps.length;

            if (isLoading)
                return (
                    <div className="flex justify-center">
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    </div>
                );
            if (hasError)
                return (
                    <div className="flex justify-center">
                        <TextHover text="Error loading count">
                            <AlertCircle className="h-4 w-4 text-destructive" />
                        </TextHover>
                    </div>
                );

            return (
                <div className="flex justify-center">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center gap-1.5 text-sm cursor-help">
                                <AppWindow className="h-3.5 w-3.5 text-muted-foreground" />
                                <span>{count}</span>
                            </div>
                        </TooltipTrigger>
                        <TooltipContent className="p-2">
                            {count === 0 ? (
                                <p className="text-xs text-muted-foreground italic">No agentic services configured</p>
                            ) : (
                                <div className="flex flex-col gap-1.5 max-w-[200px]">
                                    {apps
                                        .filter((app, i, arr) => arr.findIndex((a) => a.id === app.id) === i)
                                        .map((app) => (
                                            <span
                                                key={app.id}
                                                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${APP_TYPE_CLASSES[app.type]}`}
                                            >
                                                <span className="text-[9px] uppercase tracking-wide opacity-70">
                                                    {APP_TYPE_LABELS[app.type]}
                                                </span>
                                                {app.name}
                                            </span>
                                        ))}
                                </div>
                            )}
                        </TooltipContent>
                    </Tooltip>
                </div>
            );
        },
        sortingFn: (rowA, rowB) => {
            const countA = masApps[rowA.original.id]?.length ?? 0;
            const countB = masApps[rowB.original.id]?.length ?? 0;
            return countA - countB;
        }
    },
    {
        id: 'auth_scopes',
        header: () => (
            <div className="flex justify-center">
                <span className="font-medium text-muted-foreground">Auth Scopes</span>
            </div>
        ),
        cell: () => (
            <div className="flex justify-center">
                <span className="text-sm text-muted-foreground">—</span>
            </div>
        )
    },
    {
        id: 'traces',
        header: ({column}) => (
            <div className="flex justify-center">
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                    className="cursor-pointer px-0 font-medium"
                >
                    Traces
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({row}) => {
            const masId = row.original.id;
            const isLoading = traceCountsLoading[masId];
            const counts = traceCounts[masId];

            if (isLoading)
                return (
                    <div className="flex justify-center">
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    </div>
                );

            return (
                <div className="flex justify-center">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center gap-1.5 text-sm cursor-help">
                                <Activity className="h-3.5 w-3.5 text-muted-foreground" />
                                <span>{counts?.traces ?? 0}</span>
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p className="text-xs">Trace sessions recorded for this MAS.</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            );
        },
        sortingFn: (rowA, rowB) => {
            const a = traceCounts[rowA.original.id]?.traces ?? 0;
            const b = traceCounts[rowB.original.id]?.traces ?? 0;
            return a - b;
        }
    },
    {
        id: 'authorizations',
        header: ({column}) => (
            <div className="flex justify-center">
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                    className="cursor-pointer px-0 font-medium"
                >
                    Authorizations
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({row}) => {
            const masId = row.original.id;
            const isLoading = traceCountsLoading[masId];
            const counts = traceCounts[masId];

            if (isLoading)
                return (
                    <div className="flex justify-center">
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    </div>
                );

            const allowed = counts?.allowed ?? 0;
            const denied = counts?.denied ?? 0;

            return (
                <div className="flex justify-center">
                    <div className="flex items-center gap-3 text-sm">
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <div className="flex items-center gap-1 cursor-help">
                                    <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                                    <span>{allowed}</span>
                                </div>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className="text-xs">Allowed MCP tool calls</p>
                            </TooltipContent>
                        </Tooltip>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <div className="flex items-center gap-1 cursor-help">
                                    <XCircle className="h-3.5 w-3.5 text-red-500" />
                                    <span>{denied}</span>
                                </div>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className="text-xs">Denied MCP tool calls</p>
                            </TooltipContent>
                        </Tooltip>
                    </div>
                </div>
            );
        },
        sortingFn: (rowA, rowB) => {
            const a = (traceCounts[rowA.original.id]?.allowed ?? 0) + (traceCounts[rowA.original.id]?.denied ?? 0);
            const b = (traceCounts[rowB.original.id]?.allowed ?? 0) + (traceCounts[rowB.original.id]?.denied ?? 0);
            return a - b;
        }
    },
    {
        accessorKey: 'created_at',
        header: ({column}) => (
            <div className="flex justify-center">
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                    className="cursor-pointer px-0 font-medium"
                >
                    Created
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({row}) => (
            <div className="flex justify-center">
                <DateHover date={row.getValue('created_at')} className="text-sm" />
            </div>
        )
    }
];
