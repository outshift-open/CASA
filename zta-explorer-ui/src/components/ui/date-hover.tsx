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
        return dateObj.toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'short'
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
