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

'use client';

import * as React from 'react';
import {cva, type VariantProps} from 'class-variance-authority';
import {Tabs as TabsPrimitive} from 'radix-ui';

import {cn} from '@/lib/utils';

function Tabs({className, orientation = 'horizontal', ...props}: React.ComponentProps<typeof TabsPrimitive.Root>) {
    return (
        <TabsPrimitive.Root
            data-slot="tabs"
            data-orientation={orientation}
            orientation={orientation}
            className={cn('group/tabs flex gap-2 data-[orientation=horizontal]:flex-col', className)}
            {...props}
        />
    );
}

const tabsListVariants = cva(
    'group/tabs-list text-muted-foreground inline-flex w-fit items-center group-data-[orientation=vertical]/tabs:h-fit group-data-[orientation=vertical]/tabs:flex-col',
    {
        variants: {
            variant: {
                default:
                    'rounded-lg p-[3px] group-data-[orientation=horizontal]/tabs:h-9 bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.07)] justify-center',
                line: 'rounded-none gap-1 bg-transparent justify-center',
                underline:
                    'rounded-none bg-transparent border-b border-[rgba(255,255,255,0.07)] gap-0 w-full justify-start h-11'
            }
        },
        defaultVariants: {
            variant: 'default'
        }
    }
);

function TabsList({
    className,
    variant = 'default',
    ...props
}: React.ComponentProps<typeof TabsPrimitive.List> & VariantProps<typeof tabsListVariants>) {
    return (
        <TabsPrimitive.List
            data-slot="tabs-list"
            data-variant={variant}
            className={cn(tabsListVariants({variant}), className)}
            {...props}
        />
    );
}

function TabsTrigger({className, ...props}: React.ComponentProps<typeof TabsPrimitive.Trigger>) {
    return (
        <TabsPrimitive.Trigger
            data-slot="tabs-trigger"
            className={cn(
                "cursor-pointer focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:outline-ring text-foreground/60 hover:text-foreground relative inline-flex items-center gap-1.5 rounded-md border border-transparent px-2 py-1 text-sm font-medium whitespace-nowrap transition-all group-data-[orientation=vertical]/tabs:w-full group-data-[orientation=vertical]/tabs:justify-start focus-visible:ring-[3px] focus-visible:outline-1 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
                // default variant
                'group-data-[variant=default]/tabs-list:h-[calc(100%-1px)] group-data-[variant=default]/tabs-list:flex-1 group-data-[variant=default]/tabs-list:justify-center group-data-[variant=default]/tabs-list:data-[state=active]:shadow-sm',
                'group-data-[variant=default]/tabs-list:data-[state=active]:bg-[rgba(255,255,255,0.10)] group-data-[variant=default]/tabs-list:data-[state=active]:text-[rgba(255,255,255,0.94)] group-data-[variant=default]/tabs-list:data-[state=active]:border-[rgba(255,255,255,0.12)]',
                // line variant
                'group-data-[variant=line]/tabs-list:bg-transparent group-data-[variant=line]/tabs-list:data-[state=active]:bg-transparent group-data-[variant=line]/tabs-list:data-[state=active]:border-transparent group-data-[variant=line]/tabs-list:data-[state=active]:shadow-none',
                'after:bg-[#00BCEB] after:absolute after:opacity-0 after:transition-opacity group-data-[orientation=horizontal]/tabs:after:inset-x-0 group-data-[orientation=horizontal]/tabs:after:bottom-[-5px] group-data-[orientation=horizontal]/tabs:after:h-0.5 group-data-[orientation=vertical]/tabs:after:inset-y-0 group-data-[orientation=vertical]/tabs:after:-right-1 group-data-[orientation=vertical]/tabs:after:w-0.5 group-data-[variant=line]/tabs-list:data-[state=active]:after:opacity-100',
                // underline variant
                'group-data-[variant=underline]/tabs-list:rounded-none group-data-[variant=underline]/tabs-list:border-0 group-data-[variant=underline]/tabs-list:px-4 group-data-[variant=underline]/tabs-list:h-11 group-data-[variant=underline]/tabs-list:bg-transparent group-data-[variant=underline]/tabs-list:data-[state=active]:bg-transparent group-data-[variant=underline]/tabs-list:data-[state=active]:text-foreground group-data-[variant=underline]/tabs-list:data-[state=active]:shadow-none group-data-[variant=underline]/tabs-list:data-[state=inactive]:hover:text-foreground/80',
                'group-data-[variant=underline]/tabs-list:after:bottom-0 group-data-[variant=underline]/tabs-list:after:h-0.5 group-data-[variant=underline]/tabs-list:after:inset-x-0 group-data-[variant=underline]/tabs-list:after:absolute group-data-[variant=underline]/tabs-list:after:bg-[#00BCEB] group-data-[variant=underline]/tabs-list:after:opacity-0 group-data-[variant=underline]/tabs-list:after:transition-opacity group-data-[variant=underline]/tabs-list:data-[state=active]:after:opacity-100',
                className
            )}
            {...props}
        />
    );
}

function TabsContent({className, ...props}: React.ComponentProps<typeof TabsPrimitive.Content>) {
    return (
        <TabsPrimitive.Content data-slot="tabs-content" className={cn('flex-1 outline-none', className)} {...props} />
    );
}

export {Tabs, TabsList, TabsTrigger, TabsContent, tabsListVariants};
