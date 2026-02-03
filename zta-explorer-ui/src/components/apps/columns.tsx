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
import {MoreHorizontal, Pencil, Trash2} from 'lucide-react';
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

export const createColumns = (onEdit: (app: App) => void, onDelete: (id: string) => void): ColumnDef<App>[] => [
    {
        accessorKey: 'name',
        header: 'Name',
        cell: ({row}) => <div className="font-medium">{row.getValue('name')}</div>
    },
    {
        accessorKey: 'type',
        header: 'Type',
        cell: ({row}) => {
            const type = row.getValue('type') as AppType;
            return <Badge variant={APP_TYPE_VARIANTS[type]}>{APP_TYPE_LABELS[type]}</Badge>;
        }
    },
    {
        accessorKey: 'base_url',
        header: 'Base URL',
        cell: ({row}) => <div className="text-sm text-muted-foreground">{row.getValue('base_url')}</div>
    },
    {
        accessorKey: 'tools',
        header: 'Tools',
        cell: ({row}) => {
            const tools = row.getValue('tools') as string[];
            return (
                <div className="flex flex-wrap gap-1">
                    {tools && tools.length > 0 ? (
                        tools.slice(0, 3).map((tool, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                                {tool}
                            </Badge>
                        ))
                    ) : (
                        <span className="text-xs text-muted-foreground">None</span>
                    )}
                    {tools && tools.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                            +{tools.length - 3}
                        </Badge>
                    )}
                </div>
            );
        }
    },
    {
        id: 'actions',
        header: () => <div className="w-[70px]"></div>,
        cell: ({row}) => {
            const app = row.original;
            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => onEdit(app)}>
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive" onClick={() => app.id && onDelete(app.id)}>
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        }
    }
];
