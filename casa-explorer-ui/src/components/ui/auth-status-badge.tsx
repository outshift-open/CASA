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

import {CheckCircle2, XCircle} from 'lucide-react';
import {Badge} from '@/components/ui/badge';
import {cn} from '@/lib/utils';

interface AuthStatusBadgeProps {
    blocked: boolean;
    className?: string;
    size?: 'sm' | 'md';
}

export function AuthStatusBadge({blocked, className, size = 'md'}: AuthStatusBadgeProps) {
    return (
        <Badge
            variant="outline"
            className={cn(
                blocked ? 'border-red-500/50 text-red-400' : 'border-green-500/50 text-green-400',
                size === 'sm' ? 'text-[10px] h-4 px-1.5' : 'gap-1',
                className
            )}
        >
            {size === 'md' && (blocked ? <XCircle className="h-3 w-3" /> : <CheckCircle2 className="h-3 w-3" />)}
            {blocked ? 'Denied' : 'Allowed'}
        </Badge>
    );
}
