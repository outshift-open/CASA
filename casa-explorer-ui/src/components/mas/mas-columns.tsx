/**
 * Copyright 2026 Google LLC
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
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {MoreHorizontal, ArrowUpDown, Eye, Loader2, AlertCircle} from 'lucide-react';
import type {MAS} from '@/types/mas.types';
import type {App} from '@/types/app.types';
import {DateHover} from '@/components/ui/date-hover';

export const createMASColumns = (
    navigate: (path: string) => void,
    masApps: Record<string, App[]> = {},
    countsLoading: Record<string, boolean> = {},
    countsError: Record<string, boolean> = {}
): ColumnDef<MAS>[] => [
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
                            onClick={() => navigate(`/mas/${row.original.id}`)}
                        >
                            {name}
                        </div>
                    </TextHover>
                </div>
            );
        }
    },
    {
        accessorKey: 'apps',
        header: ({column}) => {
            return (
                <div className="flex justify-center">
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                        className="cursor-pointer"
                    >
                        Agentic Services
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => {
            const masId = row.original.id;
            const isLoading = countsLoading[masId];
            const hasError = countsError[masId];
            const apps = masApps[masId] ?? [];
            const count = apps.length;

            return (
                <div className="flex justify-center">
                    {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    ) : hasError ? (
                        <TextHover text="Error loading count">
                            <AlertCircle className="h-4 w-4 text-destructive" />
                        </TextHover>
                    ) : (
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <div>
                                    <Badge variant="secondary" className="cursor-help">
                                        {count}
                                    </Badge>
                                </div>
                            </TooltipTrigger>
                            <TooltipContent className="max-w-sm p-3">
                                {count === 0 ? (
                                    <p className="text-sm text-muted-foreground italic">
                                        No agentic services configured
                                    </p>
                                ) : (
                                    <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto">
                                        {apps.map((app) => (
                                            <Badge
                                                key={app.id}
                                                variant="secondary"
                                                className="text-xs font-medium px-2 py-0.5 cursor-pointer hover:bg-secondary/80 transition-colors"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/agentic-services/${app.id}`);
                                                }}
                                            >
                                                {app.name}
                                            </Badge>
                                        ))}
                                    </div>
                                )}
                            </TooltipContent>
                        </Tooltip>
                    )}
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
        accessorKey: 'created_at',
        header: ({column}) => {
            return (
                <div className="flex justify-center">
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                        className="cursor-pointer"
                    >
                        Created
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => (
            <div className="flex justify-center">
                <DateHover date={row.getValue('created_at')} className="text-sm" />
            </div>
        )
    },
    {
        id: 'actions',
        header: () => <div className="text-center">Actions</div>,
        cell: ({row}) => {
            const mas = row.original;
            return (
                <div className="flex justify-center">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0 cursor-pointer">
                                <span className="sr-only">Open menu</span>
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => navigate(`/mas/${mas.id}`)} className="cursor-pointer">
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
