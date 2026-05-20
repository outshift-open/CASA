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

import {memo, useState} from 'react';
import {Handle, Position} from '@xyflow/react';
import {Bot, AppWindow, Server, Wrench} from 'lucide-react';
import {cn} from '@/lib/utils';
import type {AppType} from '@/types/app.types';
import type {Tool} from '@/types/app.types';
import {APP_TYPE_LABELS} from '@/components/ui/app-type-badge';
import {getAppColor} from '@/lib/app-colors';

const APP_TYPE_ICON: Record<
    AppType,
    React.ComponentType<{className?: string; strokeWidth?: number; style?: React.CSSProperties}>
> = {
    agent: Bot,
    client: AppWindow,
    mcp_server: Server
};

function hexToRgba(hex: string, alpha: number): string {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r},${g},${b},${alpha})`;
}

interface MASGraphNodeProps {
    data: {
        name: string;
        type: AppType;
        toolCount: number;
        tools?: Tool[];
        appId?: string;
        isHighlighted?: boolean;
    };
}

export const MASGraphNode = memo(({data}: MASGraphNodeProps) => {
    const Icon = APP_TYPE_ICON[data.type];
    const [hovered, setHovered] = useState(false);

    const TYPE_COLOR: Record<AppType, string> = {agent: '', mcp_server: '#22d3ee', client: '#60a5fa'};
    const accent =
        data.type === 'agent' && data.appId ? getAppColor(data.appId, data.type) : TYPE_COLOR[data.type] || '#22d3ee';
    const glow = hexToRgba(accent, 0.18);
    const border = hexToRgba(accent, 0.35);

    const borderColor = data.isHighlighted || hovered ? accent : border;
    const shadow = data.isHighlighted
        ? `0 0 0 2px ${accent}55, 0 0 32px ${glow}, inset 0 1px 0 rgba(255,255,255,0.05)`
        : hovered
          ? `0 0 0 1px ${accent}33, 0 0 28px ${glow}, 0 8px 32px rgba(0,0,0,0.5)`
          : `0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04)`;

    return (
        <div
            className={cn('relative rounded-2xl', data.isHighlighted && 'mas-graph-node--highlighted')}
            style={{
                width: 200,
                background: 'linear-gradient(135deg, rgb(8,14,28) 0%, rgb(10,16,32) 100%)',
                border: `1px solid ${borderColor}`,
                boxShadow: shadow,
                transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
                transition: 'box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease'
            }}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
        >
            <Handle type="target" position={Position.Top} id="top" style={{opacity: 0, width: 8, height: 8}} />
            <Handle
                type="target"
                position={Position.Top}
                id="top-left"
                style={{opacity: 0, width: 8, height: 8, left: '33%'}}
            />
            <Handle
                type="target"
                position={Position.Top}
                id="top-right"
                style={{opacity: 0, width: 8, height: 8, left: '67%'}}
            />
            <Handle type="source" position={Position.Bottom} id="bottom" style={{opacity: 0, width: 8, height: 8}} />
            <Handle
                type="source"
                position={Position.Bottom}
                id="bottom-left"
                style={{opacity: 0, width: 8, height: 8, left: '33%'}}
            />
            <Handle
                type="source"
                position={Position.Bottom}
                id="bottom-right"
                style={{opacity: 0, width: 8, height: 8, left: '67%'}}
            />
            <Handle type="source" position={Position.Right} id="right" style={{opacity: 0, width: 8, height: 8}} />
            <Handle
                type="target"
                position={Position.Right}
                id="right-target"
                style={{opacity: 0, width: 8, height: 8}}
            />
            <Handle type="source" position={Position.Left} id="left" style={{opacity: 0, width: 8, height: 8}} />
            <Handle type="target" position={Position.Left} id="left-target" style={{opacity: 0, width: 8, height: 8}} />

            {/* Top accent line */}
            <div
                className="absolute top-0 left-4 right-4 h-px rounded-full"
                style={{
                    background: `linear-gradient(90deg, transparent, ${accent}99, transparent)`,
                    opacity: hovered ? 1 : 0.5,
                    transition: 'opacity 0.15s ease'
                }}
            />

            <div className="px-4 py-3.5 flex flex-col gap-3">
                <div className="flex items-center justify-between">
                    <div
                        className="flex items-center justify-center w-8 h-8 rounded-lg"
                        style={{background: glow, border: `1px solid ${border}`}}
                    >
                        <Icon className="w-4 h-4" style={{color: accent}} strokeWidth={1.5} />
                    </div>
                    <span
                        className="text-[9px] font-semibold uppercase tracking-widest px-2 py-0.5 rounded-full"
                        style={{color: accent, background: glow, border: `1px solid ${border}`}}
                    >
                        {APP_TYPE_LABELS[data.type]}
                    </span>
                </div>

                <div className="font-semibold text-sm leading-tight text-white/90 truncate" title={data.name}>
                    {data.name}
                </div>

                {data.type === 'mcp_server' && (
                    <div className="flex items-center gap-1.5 pt-0.5 border-t border-white/5">
                        <Wrench className="w-3 h-3 text-white/30" strokeWidth={1.5} />
                        <span className="text-[11px] text-white/40">
                            {data.toolCount} {data.toolCount === 1 ? 'tool' : 'tools'}
                        </span>
                    </div>
                )}
            </div>

            {/* Tooltip on hover — rendered as absolute overlay to avoid interfering with drag */}
            {hovered && data.type === 'mcp_server' && data.tools && data.tools.length > 0 && (
                <div
                    className="absolute left-full ml-3 top-0 z-50 w-56 rounded-xl overflow-hidden pointer-events-none"
                    style={{
                        background: 'rgba(6,11,22,0.98)',
                        border: `1px solid ${border}`,
                        backdropFilter: 'blur(12px)',
                        boxShadow: `0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px ${border}`
                    }}
                >
                    <div
                        className="px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest"
                        style={{
                            background: `linear-gradient(90deg, transparent, ${accent}22, transparent)`,
                            color: accent,
                            borderBottom: `1px solid ${border}`
                        }}
                    >
                        {data.tools.length} Tools
                    </div>
                    <ul className="p-3 space-y-1.5">
                        {data.tools.slice(0, 6).map((tool, idx) => (
                            <li key={idx} className="flex items-start gap-1.5 text-xs">
                                <span
                                    className="mt-1.5 w-1 h-1 rounded-full flex-shrink-0"
                                    style={{background: accent}}
                                />
                                <span className="text-white/75 truncate">{tool.name}</span>
                            </li>
                        ))}
                        {data.tools.length > 6 && (
                            <li className="text-xs text-white/30 pl-2.5">+{data.tools.length - 6} more</li>
                        )}
                    </ul>
                </div>
            )}
        </div>
    );
});

MASGraphNode.displayName = 'MASGraphNode';
