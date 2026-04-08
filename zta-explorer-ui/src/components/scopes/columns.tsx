import {ColumnDef} from '@tanstack/react-table';
import {Button} from '@/components/ui/button';
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
import type {Scope} from '@/types/scope.types';

export const createColumns = (navigate: (path: string) => void): ColumnDef<Scope>[] => [
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
                            onClick={() => navigate(`/scopes/${row.original.id}`)}
                        >
                            {name}
                        </div>
                    </TextHover>
                </div>
            );
        }
    },
    {
        accessorKey: 'id',
        header: ({column}) => {
            return (
                <div className="flex justify-center">
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                        className="cursor-pointer"
                    >
                        Scope ID
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => {
            const id = row.getValue('id') as string;
            return (
                <div className="flex justify-center">
                    <TextHover text={id} maxWidth="max-w-xs">
                        <div className="text-xs font-mono text-muted-foreground truncate">{id}</div>
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
            const scope = row.original;
            const mas = scope.mas;

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
            const scope = row.original;
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
                            <DropdownMenuItem
                                onClick={() => navigate(`/scopes/${scope.id}`)}
                                className="cursor-pointer"
                            >
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
