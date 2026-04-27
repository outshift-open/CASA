import * as React from 'react';
import {cva, type VariantProps} from 'class-variance-authority';
import {Slot} from 'radix-ui';

import {cn} from '@/lib/utils';

const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all cursor-pointer disabled:cursor-not-allowed disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
    {
        variants: {
            variant: {
                default:
                    'bg-primary text-primary-foreground hover:bg-primary/90 ioc:hover:shadow-[0_0_16px_rgba(43,130,246,0.35)]',
                destructive:
                    'bg-destructive text-white hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60',
                outline:
                    'border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50 ioc:bg-transparent ioc:border-[rgba(255,255,255,0.07)] ioc:text-[rgba(255,255,255,0.55)] ioc:hover:border-[rgba(255,255,255,0.20)] ioc:hover:text-[rgba(255,255,255,0.94)] ioc:hover:bg-transparent',
                secondary:
                    'bg-secondary text-secondary-foreground hover:bg-secondary/80 ioc:bg-[rgba(255,255,255,0.06)] ioc:border ioc:border-[rgba(255,255,255,0.07)] ioc:hover:bg-[rgba(255,255,255,0.10)]',
                ghost: 'hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50 ioc:text-[rgba(255,255,255,0.55)] ioc:hover:bg-[rgba(255,255,255,0.06)] ioc:hover:text-[rgba(255,255,255,0.94)]',
                link: 'text-primary underline-offset-4 hover:underline'
            },
            size: {
                default: 'h-9 px-4 py-2 has-[>svg]:px-3',
                xs: "h-6 gap-1 rounded-md px-2 text-xs has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3",
                sm: 'h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5',
                lg: 'h-10 rounded-md px-6 has-[>svg]:px-4',
                icon: 'size-9',
                'icon-xs': "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3",
                'icon-sm': 'size-8',
                'icon-lg': 'size-10'
            }
        },
        defaultVariants: {
            variant: 'default',
            size: 'default'
        }
    }
);

function Button({
    className,
    variant = 'default',
    size = 'default',
    asChild = false,
    ...props
}: React.ComponentProps<'button'> &
    VariantProps<typeof buttonVariants> & {
        asChild?: boolean;
    }) {
    const Comp = asChild ? Slot.Root : 'button';

    return (
        <Comp
            data-slot="button"
            data-variant={variant}
            data-size={size}
            className={cn(buttonVariants({variant, size, className}))}
            {...props}
        />
    );
}

export {Button, buttonVariants};
