import {memo} from 'react';
import {Handle, Position} from 'reactflow';
import {Bot, AppWindow, Server} from 'lucide-react';
import {Badge} from '@/components/ui/badge';
import {cn} from '@/lib/utils';
import type {AppType} from '@/types/app.types';

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

const APP_TYPE_ICONS: Record<AppType, React.ComponentType<{className?: string}>> = {
    agent: Bot,
    client: AppWindow,
    mcp_server: Server
};

interface MASGraphNodeProps {
    data: {
        name: string;
        type: AppType;
        toolCount: number;
        onClick: () => void;
    };
}

export const MASGraphNode = memo(({data}: MASGraphNodeProps) => {
    const Icon = APP_TYPE_ICONS[data.type];

    return (
        <div
            className={cn(
                'bg-card text-card-foreground rounded-xl border shadow-md',
                'px-4 py-3 min-w-[180px] cursor-pointer',
                'hover:shadow-lg hover:border-primary/50 transition-all'
            )}
            onClick={data.onClick}
        >
            <Handle type="target" position={Position.Top} id="top" className="opacity-0" />
            <Handle type="target" position={Position.Right} id="right" className="opacity-0" />
            <Handle type="target" position={Position.Bottom} id="bottom" className="opacity-0" />
            <Handle type="target" position={Position.Left} id="left" className="opacity-0" />

            <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between gap-2">
                    <Icon className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    <Badge variant={APP_TYPE_VARIANTS[data.type]} className="text-xs">
                        {APP_TYPE_LABELS[data.type]}
                    </Badge>
                </div>
                <div className="font-semibold text-sm truncate">{data.name}</div>
                <div className="text-xs text-muted-foreground">
                    {data.toolCount} {data.toolCount === 1 ? 'tool' : 'tools'}
                </div>
            </div>
        </div>
    );
});

MASGraphNode.displayName = 'MASGraphNode';
