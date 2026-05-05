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
                'text-primary-foreground rounded-xl border-2 shadow-lg',
                'px-6 py-4 min-w-[200px]',
                'bg-gradient-to-br from-[#006B8A] to-[#00BCEB] border-[#00BCEB] shadow-[0_0_24px_rgba(0,188,235,0.30)]'
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
