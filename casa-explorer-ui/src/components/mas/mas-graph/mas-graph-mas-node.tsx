/**
 * Copyright 2026 Cisco Systems, Inc. and its affiliates
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
import {Handle, Position} from '@xyflow/react';
import {Network} from 'lucide-react';

interface MASGraphMASNodeProps {
    data: {
        name: string;
        appCount: number;
    };
}

export const MASGraphMASNode = memo(({data}: MASGraphMASNodeProps) => {
    return (
        <div className="relative" style={{width: 260}}>
            {/* Outer glow ring */}
            <div
                className="absolute inset-0 rounded-2xl"
                style={{
                    background: 'transparent',
                    boxShadow:
                        '0 0 0 1px rgba(0,188,235,0.20), 0 0 48px rgba(0,188,235,0.12), 0 0 96px rgba(0,100,160,0.08)',
                    borderRadius: 16
                }}
            />

            {/* Main card */}
            <div
                className="relative rounded-2xl overflow-hidden"
                style={{
                    background: 'linear-gradient(145deg, rgb(0,30,60) 0%, rgb(0,15,40) 60%, rgb(2,8,20) 100%)',
                    border: '1px solid rgba(0,188,235,0.40)',
                    boxShadow: 'inset 0 1px 0 rgba(0,188,235,0.15), inset 0 -1px 0 rgba(0,0,0,0.3)'
                }}
            >
                {/* Scan line accent at top */}
                <div
                    className="absolute top-0 left-0 right-0 h-px"
                    style={{
                        background: 'linear-gradient(90deg, transparent 0%, rgba(0,188,235,0.8) 50%, transparent 100%)'
                    }}
                />

                {/* Corner accents */}
                <div className="absolute top-2 left-2 w-3 h-3 border-t border-l border-[rgba(0,188,235,0.5)] rounded-tl" />
                <div className="absolute top-2 right-2 w-3 h-3 border-t border-r border-[rgba(0,188,235,0.5)] rounded-tr" />
                <div className="absolute bottom-2 left-2 w-3 h-3 border-b border-l border-[rgba(0,188,235,0.5)] rounded-bl" />
                <div className="absolute bottom-2 right-2 w-3 h-3 border-b border-r border-[rgba(0,188,235,0.5)] rounded-br" />

                <div className="px-5 py-4 flex flex-col items-center gap-3">
                    {/* Icon with orbital ring */}
                    <div className="relative">
                        <div
                            className="w-12 h-12 rounded-xl flex items-center justify-center"
                            style={{
                                background: 'linear-gradient(135deg, rgba(0,100,160,0.6) 0%, rgba(0,60,100,0.4) 100%)',
                                border: '1px solid rgba(0,188,235,0.35)',
                                boxShadow: '0 0 16px rgba(0,188,235,0.20), inset 0 1px 0 rgba(0,188,235,0.15)'
                            }}
                        >
                            <Network className="w-6 h-6" style={{color: '#00BCEB'}} strokeWidth={1.5} />
                        </div>
                        {/* Pulse dot */}
                        <div
                            className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full"
                            style={{
                                background: '#00BCEB',
                                boxShadow: '0 0 6px rgba(0,188,235,0.8)',
                                animation: 'mas-pulse 2s ease-in-out infinite'
                            }}
                        />
                    </div>

                    {/* Label */}
                    <div className="text-center space-y-0.5">
                        <div
                            className="text-[9px] font-bold uppercase tracking-[0.2em]"
                            style={{color: 'rgba(0,188,235,0.65)'}}
                        >
                            Multi-Agent System
                        </div>
                        <div className="font-bold text-sm text-white/95 truncate w-full" title={data.name}>
                            {data.name}
                        </div>
                        <div className="text-[11px]" style={{color: 'rgba(0,188,235,0.55)'}}>
                            {data.appCount} {data.appCount === 1 ? 'service' : 'services'}
                        </div>
                    </div>
                </div>

                {/* Bottom scan line */}
                <div
                    className="absolute bottom-0 left-0 right-0 h-px"
                    style={{
                        background: 'linear-gradient(90deg, transparent 0%, rgba(0,188,235,0.4) 50%, transparent 100%)'
                    }}
                />
            </div>

            <Handle type="source" position={Position.Top} id="top" className="opacity-0 !w-2 !h-2" />
            <Handle type="source" position={Position.Right} id="right" className="opacity-0 !w-2 !h-2" />
            <Handle type="source" position={Position.Bottom} id="bottom" className="opacity-0 !w-2 !h-2" />
            <Handle type="source" position={Position.Left} id="left" className="opacity-0 !w-2 !h-2" />
        </div>
    );
});

MASGraphMASNode.displayName = 'MASGraphMASNode';
