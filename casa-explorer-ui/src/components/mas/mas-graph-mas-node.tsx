import {memo} from 'react';
import {Handle, Position} from 'reactflow';
import {Network} from 'lucide-react';
import {cn} from '@/lib/utils';

interface MASGraphMASNodeProps {
    data: {
        name: string;
        appCount: number;
    };
}

export const MASGraphMASNode = memo(({data}: MASGraphMASNodeProps) => {
    return (
        <div
            className={cn(
                'bg-primary text-primary-foreground rounded-xl border-2 border-primary shadow-lg',
                'px-6 py-4 min-w-[200px]'
            )}
        >
            <div className="flex flex-col items-center gap-2">
                <Network className="h-8 w-8" />
                <div className="text-center">
                    <div className="font-bold text-lg">{data.name}</div>
                    <div className="text-sm opacity-90">
                        {data.appCount} {data.appCount === 1 ? 'Agentic Service' : 'Agentic Services'}
                    </div>
                </div>
            </div>
            <Handle type="source" position={Position.Top} id="top" className="opacity-0" />
            <Handle type="source" position={Position.Right} id="right" className="opacity-0" />
            <Handle type="source" position={Position.Bottom} id="bottom" className="opacity-0" />
            <Handle type="source" position={Position.Left} id="left" className="opacity-0" />
        </div>
    );
});

MASGraphMASNode.displayName = 'MASGraphMASNode';
