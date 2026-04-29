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

import {useMemo} from 'react';
import {formatDistanceToNow} from 'date-fns';
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip';
import {cn} from '@/lib/utils';

interface DateHoverProps {
    date?: string | number | Date;
    className?: string;
}

export function DateHover({className, date}: DateHoverProps) {
    const dateObj = useMemo(() => {
        try {
            if (!date) return null;
            return new Date(date);
        } catch {
            return null;
        }
    }, [date]);

    const relativeTime = useMemo(() => {
        if (!dateObj || isNaN(dateObj.getTime())) return 'Unknown';
        return formatDistanceToNow(dateObj, {addSuffix: true});
    }, [dateObj]);

    const fullDate = useMemo(() => {
        if (!dateObj || isNaN(dateObj.getTime())) return 'Unknown date';
        return dateObj.toLocaleString('en-GB', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'longOffset',
            hour12: false
        });
    }, [dateObj]);

    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <span className={cn('cursor-default', className)}>{relativeTime}</span>
                </TooltipTrigger>
                <TooltipContent>
                    <p>{fullDate}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}
