import {memo} from 'react';
import {Handle, Position} from 'reactflow';
import {Bot, AppWindow, Server} from 'lucide-react';
import {Badge} from '@/components/ui/badge';
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip';
import {cn} from '@/lib/utils';
import type {AppType} from '@/types/app.types';
import type {Tool} from '@/types/app.types';

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
        tools?: Tool[];
        onClick: () => void;
        isHighlighted?: boolean;
    };
}

export const MASGraphNode = memo(({data}: MASGraphNodeProps) => {
    const Icon = APP_TYPE_ICONS[data.type];

    return (
        <TooltipProvider>
            <Tooltip delayDuration={300}>
                <TooltipTrigger asChild>
                    <div
                        className={cn(
                            'bg-card text-card-foreground rounded-xl border shadow-md',
                            'px-4 py-3 min-w-[180px] cursor-pointer',
                            'hover:shadow-lg hover:border-primary/50 transition-all',
                            data.isHighlighted && 'ring-2 ring-primary shadow-primary/50'
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
                </TooltipTrigger>
                <TooltipContent side="right" className="max-w-xs">
                    <div className="space-y-2">
                        <div className="font-semibold">{data.name}</div>
                        <div className="text-xs text-muted-foreground">{APP_TYPE_LABELS[data.type]}</div>
                        {data.tools && data.tools.length > 0 ? (
                            <div className="mt-2">
                                <div className="text-xs font-medium mb-1">Tools:</div>
                                <ul className="text-xs space-y-1">
                                    {data.tools.slice(0, 5).map((tool, idx) => (
                                        <li key={idx} className="truncate">
                                            • {tool.name}
                                            {tool.scopes && tool.scopes.length > 0 && (
                                                <span className="text-muted-foreground ml-1">
                                                    ({tool.scopes.map((s) => s.name).join(', ')})
                                                </span>
                                            )}
                                        </li>
                                    ))}
                                    {data.tools.length > 5 && (
                                        <li className="text-muted-foreground">...and {data.tools.length - 5} more</li>
                                    )}
                                </ul>
                            </div>
                        ) : (
                            <div className="text-xs text-muted-foreground">No tools configured</div>
                        )}
                    </div>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
});

MASGraphNode.displayName = 'MASGraphNode';
