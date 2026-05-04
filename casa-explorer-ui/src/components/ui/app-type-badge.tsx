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

import {cn} from '@/lib/utils';
import type {AppType} from '@/types/app.types';

export const APP_TYPE_LABELS: Record<AppType, string> = {
    client: 'Client',
    agent: 'Agent',
    mcp_server: 'MCP'
};

// Accessible colors: sufficient contrast on both light and dark backgrounds.
// Uses border+text (outline style) so they work inside tooltips and on any surface.
export const APP_TYPE_CLASSES: Record<AppType, string> = {
    client: 'bg-blue-500/15 text-blue-300 border border-blue-500/40',
    agent: 'bg-purple-500/15 text-purple-300 border border-purple-500/40',
    mcp_server: 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40'
};

interface AppTypeBadgeProps {
    type: AppType;
    name?: string;
    className?: string;
}

/** Pill showing app type label + optional name. Used in tooltips and inline chips. */
export function AppTypeBadge({type, name, className}: AppTypeBadgeProps) {
    return (
        <span
            className={cn(
                'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
                APP_TYPE_CLASSES[type],
                className
            )}
        >
            <span className="text-[9px] uppercase tracking-wide opacity-80">{APP_TYPE_LABELS[type]}</span>
            {name && <span className="font-semibold">{name}</span>}
        </span>
    );
}
