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

import * as React from 'react';
import {cva, type VariantProps} from 'class-variance-authority';
import {Slot} from 'radix-ui';

import {cn} from '@/lib/utils';

const badgeVariants = cva(
    'inline-flex items-center justify-center rounded-full border border-transparent px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden',
    {
        variants: {
            variant: {
                default: 'bg-primary text-primary-foreground [a&]:hover:bg-primary/90',
                secondary: 'bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90',
                destructive: 'bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20',
                outline: 'border-border text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground',
                ghost: '[a&]:hover:bg-accent [a&]:hover:text-accent-foreground',
                link: 'text-primary underline-offset-4 [a&]:hover:underline'
            }
        },
        defaultVariants: {
            variant: 'default'
        }
    }
);

function Badge({
    className,
    variant = 'default',
    asChild = false,
    ...props
}: React.ComponentProps<'span'> & VariantProps<typeof badgeVariants> & {asChild?: boolean}) {
    const Comp = asChild ? Slot.Root : 'span';

    return (
        <Comp data-slot="badge" data-variant={variant} className={cn(badgeVariants({variant}), className)} {...props} />
    );
}

export {Badge, badgeVariants};
