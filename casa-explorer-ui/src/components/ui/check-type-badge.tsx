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

import {Cpu, Sparkles} from 'lucide-react';
import {Badge} from '@/components/ui/badge';
import {cn} from '@/lib/utils';

type CheckType = 'AI_POWERED' | 'DETERMINISTIC';

interface CheckTypeBadgeProps {
    type: CheckType | string | null | undefined;
    className?: string;
    size?: 'sm' | 'md';
}

const config = {
    AI_POWERED: {
        label: 'Semantic',
        icon: Sparkles,
        className: 'border-sky-500/50 text-sky-400'
    },
    DETERMINISTIC: {
        label: 'Deterministic',
        icon: Cpu,
        className: 'border-orange-500/50 text-orange-400'
    }
} as const;

export function CheckTypeBadge({type, className, size = 'md'}: CheckTypeBadgeProps) {
    if (!type || !(type in config)) return null;

    const {label, icon: Icon, className: colorClass} = config[type as CheckType];

    return (
        <Badge
            variant="outline"
            className={cn(
                'font-medium',
                size === 'sm' ? 'text-[9px] h-4 px-1.5 gap-0.5' : 'gap-1',
                colorClass,
                className
            )}
        >
            <Icon className={size === 'sm' ? 'h-2.5 w-2.5' : 'h-3 w-3'} />
            {label}
        </Badge>
    );
}

/** Canonical colors for charts/visualizations (matches badge colors) */
export const checkTypeChartColors: Record<CheckType, string> = {
    DETERMINISTIC: '#F97316', // orange-500
    AI_POWERED: '#0EA5E9' // sky-500
};
