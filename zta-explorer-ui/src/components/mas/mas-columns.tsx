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
import {MoreHorizontal, Pencil, Trash2, ArrowUpDown, Eye, Loader2, AlertCircle} from 'lucide-react';
import type {MAS} from '@/types/mas.types';
import {DateHover} from '@/components/ui/date-hover';

export const createMASColumns = (
    onEdit: (mas: MAS) => void,
    onDelete: (id: string) => void,
    navigate: (path: string) => void,
    appCounts: Record<string, number> = {},
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
                        Apps
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            );
        },
        cell: ({row}) => {
            const masId = row.original.id;
            const isLoading = countsLoading[masId];
            const hasError = countsError[masId];
            const count = appCounts[masId] ?? 0;

            return (
                <div className="flex justify-center">
                    {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    ) : hasError ? (
                        <TextHover text="Error loading count">
                            <AlertCircle className="h-4 w-4 text-destructive" />
                        </TextHover>
                    ) : (
                        <Badge variant="secondary">{count}</Badge>
                    )}
                </div>
            );
        },
        sortingFn: (rowA, rowB) => {
            const countA = appCounts[rowA.original.id] ?? 0;
            const countB = appCounts[rowB.original.id] ?? 0;
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
                            <DropdownMenuItem
                                onClick={() => navigate(`/mas/${mas.id}/edit`)}
                                className="cursor-pointer"
                            >
                                <Pencil className="mr-2 h-4 w-4" />
                                Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem
                                onClick={() => onDelete(mas.id)}
                                className="text-destructive cursor-pointer"
                            >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            );
        }
    }
];
