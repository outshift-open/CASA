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

import {useNavigate} from 'react-router-dom';
import {useMemo} from 'react';
import {PATHS} from '@/router/paths';
import {Button} from '@/components/ui/button';
import {CheckTypeBadge} from '@/components/ui/check-type-badge';
import {AuthStatusBadge} from '@/components/ui/auth-status-badge';
import {DateHover} from '@/components/ui/date-hover';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {Network, ArrowUpDown} from 'lucide-react';
import type {ColumnDef} from '@tanstack/react-table';
import type {BlockingReason} from '@/types/trace.types';
import {BLOCKING_REASON_LABELS, BLOCKING_REASON_DESCRIPTIONS} from '@/components/traces/event-row';
import type {AppNames} from '@/components/traces/event-row';

export interface AuthRequest {
    id: string;
    userInputId: string;
    tool: string;
    callerAppId: string | null;
    calleeAppId: string | null;
    masId: string | null;
    blocked: boolean;
    blockingType: string | null;
    blockingReason: BlockingReason | null;
    createdAt: string;
}

export function useAuthRequestColumns(
    masMap: Record<string, string>,
    appNames: AppNames = {}
): ColumnDef<AuthRequest>[] {
    const navigate = useNavigate();

    return useMemo<ColumnDef<AuthRequest>[]>(
        () => [
            {
                accessorKey: 'tool',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Tool <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <code className="font-mono text-sm font-medium">{row.getValue('tool')}</code>
                    </div>
                )
            },
            {
                accessorKey: 'callerAppId',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Caller <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const id = row.getValue('callerAppId') as string | null;
                    const name = id ? (appNames[id]?.name ?? id) : '—';
                    return (
                        <div className="flex justify-center">
                            <span className="text-sm text-muted-foreground">{name}</span>
                        </div>
                    );
                }
            },
            {
                accessorKey: 'calleeAppId',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            MCP Server <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const id = row.getValue('calleeAppId') as string | null;
                    const name = id ? (appNames[id]?.name ?? id) : '—';
                    return (
                        <div className="flex justify-center">
                            <span className="text-sm text-muted-foreground">{name}</span>
                        </div>
                    );
                }
            },
            {
                accessorKey: 'masId',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            MAS <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const req = row.original;
                    const masName = req.masId ? (masMap[req.masId] ?? req.masId) : null;
                    if (!masName)
                        return (
                            <div className="flex justify-center">
                                <span className="text-muted-foreground">—</span>
                            </div>
                        );
                    return (
                        <div className="flex justify-center">
                            <button
                                type="button"
                                className="flex items-center gap-1.5 text-sm hover:underline cursor-pointer"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (req.masId) navigate(PATHS.mas.detail(req.masId));
                                }}
                            >
                                <Network className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                                <span className="truncate max-w-[160px]">{masName}</span>
                            </button>
                        </div>
                    );
                }
            },
            {
                accessorKey: 'blocked',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Authorization <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <AuthStatusBadge blocked={row.getValue('blocked') as boolean} />
                    </div>
                )
            },
            {
                accessorKey: 'blockingType',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Deny Type <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const type = row.getValue('blockingType') as string | null;
                    return (
                        <div className="flex justify-center">
                            {!type ? <span className="text-muted-foreground">—</span> : <CheckTypeBadge type={type} />}
                        </div>
                    );
                }
            },
            {
                accessorKey: 'blockingReason',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Deny Reason <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => {
                    const reason = row.getValue('blockingReason') as BlockingReason | null;
                    if (!reason)
                        return (
                            <div className="flex justify-center">
                                <span className="text-muted-foreground">—</span>
                            </div>
                        );
                    const label = BLOCKING_REASON_LABELS[reason] ?? reason;
                    const desc = BLOCKING_REASON_DESCRIPTIONS[reason];
                    return (
                        <div className="flex justify-center">
                            {desc ? (
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <span className="text-sm cursor-default">{label}</span>
                                    </TooltipTrigger>
                                    <TooltipContent className="max-w-[240px]">
                                        <p>{desc}</p>
                                    </TooltipContent>
                                </Tooltip>
                            ) : (
                                <span className="text-sm">{label}</span>
                            )}
                        </div>
                    );
                }
            },
            {
                accessorKey: 'createdAt',
                header: ({column}) => (
                    <div className="flex justify-center">
                        <Button
                            variant="ghost"
                            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                            className="cursor-pointer"
                        >
                            Created At <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                ),
                cell: ({row}) => (
                    <div className="flex justify-center">
                        <DateHover date={row.getValue('createdAt')} className="text-sm" />
                    </div>
                )
            }
        ],
        [navigate, masMap, appNames]
    );
}
