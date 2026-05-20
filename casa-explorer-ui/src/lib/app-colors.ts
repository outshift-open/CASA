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

import type {AppType} from '@/types/app.types';

function hashId(id: string): number {
    let h = 0;
    for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
    return h;
}

// Hex palettes mirror the Tailwind class palettes in event-row
const AGENT_HEX_PALETTE = ['#a78bfa', '#e879f9', '#f472b6', '#fb7185', '#fb923c', '#facc15', '#a3e635', '#34d399'];
const MCP_HEX_PALETTE = ['#22d3ee', '#2dd4bf', '#38bdf8', '#818cf8'];
const CLIENT_HEX_PALETTE = ['#60a5fa', '#93c5fd', '#bfdbfe'];

const AGENT_TAILWIND_PALETTE = [
    'text-violet-400',
    'text-fuchsia-400',
    'text-pink-400',
    'text-rose-400',
    'text-orange-400',
    'text-yellow-400',
    'text-lime-400',
    'text-emerald-400'
];
const MCP_TAILWIND_PALETTE = ['text-cyan-400', 'text-teal-400', 'text-sky-400', 'text-indigo-400'];
const CLIENT_TAILWIND_PALETTE = ['text-blue-400', 'text-blue-300', 'text-blue-200'];

/** Returns a hex color for a specific app instance — consistent across graph and traces. */
export function getAppColor(id: string, type: AppType): string {
    const h = hashId(id);
    if (type === 'agent') return AGENT_HEX_PALETTE[h % AGENT_HEX_PALETTE.length];
    if (type === 'mcp_server') return MCP_HEX_PALETTE[h % MCP_HEX_PALETTE.length];
    return CLIENT_HEX_PALETTE[h % CLIENT_HEX_PALETTE.length];
}

/** Returns a Tailwind text color class for a specific app instance — used in trace rows. */
export function getAppColorClass(id: string, type: AppType): string {
    const h = hashId(id);
    if (type === 'agent') return AGENT_TAILWIND_PALETTE[h % AGENT_TAILWIND_PALETTE.length];
    if (type === 'mcp_server') return MCP_TAILWIND_PALETTE[h % MCP_TAILWIND_PALETTE.length];
    return CLIENT_TAILWIND_PALETTE[h % CLIENT_TAILWIND_PALETTE.length];
}
