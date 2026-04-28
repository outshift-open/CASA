/**
 * Copyright 2026 Cisco Systems, Inc. and its affiliates
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

import {ColumnDef} from '@tanstack/react-table';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {TextHover} from '@/components/ui/text-hover';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {MoreHorizontal, ArrowUpDown, Eye, Network} from 'lucide-react';
import type {App, AppType} from '@/types/app.types';

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agent',
    client: 'Client',
    mcp_server: 'MCP Server'
};

const APP_TYPE_VARIANTS: Record<AppType, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    agent: 'default',
    client: 'secondary',
    mcp_server: 'outline'
};

export const createColumns = (navigate: (path: string) => void): ColumnDef<App>[] => [
    {
        accessorKey: 'name',
        header: ({column}) => {
            return (
                <div className="flex justify-center">
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                        className="cursor-pointer"
                    >
                        Name
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => {
            const name = row.getValue('name') as string;
            return (
                <div className="flex justify-center">
                    <TextHover text={name}>
                        <div
                            className="font-semibold cursor-pointer underline decoration-dotted hover:decoration-solid"
                            onClick={() => navigate(`/apps/${row.original.id}`)}
                        >
                            {name}
                        </div>
                    </TextHover>
                </div>
            );
        }
    },
    {
        accessorKey: 'type',
        header: ({column}) => {
            return (
                <div className="flex justify-center">
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                        className="cursor-pointer"
                    >
                        Type
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => {
            const type = row.getValue('type') as AppType;
            return (
                <div className="flex justify-center">
                    <Badge variant={APP_TYPE_VARIANTS[type]}>{APP_TYPE_LABELS[type]}</Badge>
                </div>
            );
        }
    },
    {
        accessorKey: 'base_url',
        header: ({column}) => {
            return (
                <div className="flex justify-center">
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                        className="cursor-pointer"
                    >
                        Base URL
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => {
            const baseUrl = row.getValue('base_url') as string;
            return (
                <div className="flex justify-center">
                    <TextHover text={baseUrl} maxWidth="max-w-sm">
                        <div className="text-sm text-muted-foreground">{baseUrl}</div>
                    </TextHover>
                </div>
            );
        }
    },
    {
        accessorKey: 'mas_id',
        header: ({column}) => {
            return (
                <div className="flex justify-center">
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                        className="cursor-pointer"
                    >
                        Multi-Agent System
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => {
            const app = row.original;
            const mas = app.mas;

            if (!mas) {
                return (
                    <div className="flex justify-center">
                        <span className="text-muted-foreground text-sm">-</span>
                    </div>
                );
            }

            return (
                <div className="flex justify-center">
                    <TextHover text={mas.name} maxWidth="max-w-[200px]">
                        <div
                            className="flex items-center gap-1.5 cursor-pointer hover:decoration-solid min-w-0"
                            onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/mas/${mas.id}`);
                            }}
                        >
                            <Network className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                            <span className="text-xs font-semibold underline decoration-dotted truncate">
                                {mas.name}
                            </span>
                        </div>
                    </TextHover>
                </div>
            );
        }
    },
    {
        id: 'actions',
        header: () => <div className="text-center">Actions</div>,
        cell: ({row}) => {
            const app = row.original;
            return (
                <div className="flex justify-center">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="cursor-pointer">
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => navigate(`/apps/${app.id}`)} className="cursor-pointer">
                                <Eye className="mr-2 h-4 w-4" />
                                View Details
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            );
        }
    }
];
