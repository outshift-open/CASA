import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip';

interface TextHoverProps {
    children: React.ReactNode;
    text: string;
    className?: string;
    maxWidth?: string;
}

export function TextHover({children, text, className, maxWidth = 'max-w-xs'}: TextHoverProps) {
    return (
        <TooltipProvider>
            <Tooltip delayDuration={300}>
                <TooltipTrigger asChild>
                    <div className={`truncate ${maxWidth} ${className || ''}`}>{children}</div>
                </TooltipTrigger>
                <TooltipContent side="left" className="max-w-md break-words">
                    <p>{text}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}
