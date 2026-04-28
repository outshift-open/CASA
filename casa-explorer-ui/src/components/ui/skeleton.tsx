import {cn} from '@/lib/utils';

function Skeleton({className, ...props}: React.ComponentProps<'div'>) {
    return (
        <div
            data-slot="skeleton"
            className={cn(
                'relative overflow-hidden rounded-md bg-[rgba(255,255,255,0.06)]',
                'before:absolute before:inset-0 before:-translate-x-full',
                'before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent',
                'before:animate-[shimmer_1.5s_infinite]',
                className
            )}
            {...props}
        />
    );
}

export {Skeleton};
