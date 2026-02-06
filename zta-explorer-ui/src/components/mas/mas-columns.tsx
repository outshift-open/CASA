import {ColumnDef} from '@tanstack/react-table';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {MoreHorizontal, Pencil, Trash2, ArrowUpDown, Eye} from 'lucide-react';
import type {MAS} from '@/types/mas.types';
import {DateHover} from '@/components/ui/date-hover';

export const createMASColumns = (
    onEdit: (mas: MAS) => void,
    onDelete: (id: string) => void,
    navigate: (path: string) => void
): ColumnDef<MAS>[] => [
    {
        accessorKey: 'name',
        header: ({column}) => {
            return (
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                    className="cursor-pointer"
                >
                    Name
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        cell: ({row}) => {
            return (
                <div
                    className="font-medium cursor-pointer hover:underline"
                    onClick={() => navigate(`/mas/${row.original.id}`)}
                >
                    {row.getValue('name')}
                </div>
            );
        }
    },
    {
        accessorKey: 'apps',
        header: 'Applications',
        cell: ({row}) => {
            const apps = row.getValue('apps') as MAS['apps'];
            return (
                <div className="flex flex-wrap gap-1">
                    {apps && apps.length > 0 ? (
                        <>
                            {apps.slice(0, 3).map((app) => (
                                <Badge key={app.id} variant="secondary" className="text-xs">
                                    {app.name}
                                </Badge>
                            ))}
                            {apps.length > 3 && (
                                <Badge variant="outline" className="text-xs">
                                    +{apps.length - 3} more
                                </Badge>
                            )}
                        </>
                    ) : (
                        <span className="text-xs text-muted-foreground">No apps</span>
                    )}
                </div>
            );
        }
    },
    {
        accessorKey: 'created_at',
        header: ({column}) => {
            return (
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                    className="cursor-pointer"
                >
                    Created
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        cell: ({row}) => <DateHover date={row.getValue('created_at')} className="text-sm" />
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
