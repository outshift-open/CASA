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

import {ReactNode} from 'react';
import {CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {RefreshCw, Search} from 'lucide-react';

export interface CardTableHeaderFilterOption {
    value: string;
    label: string;
}

export interface CardTableHeaderFilter {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    width?: string;
    options: CardTableHeaderFilterOption[];
}

export interface CardTableHeaderViewToggleOption {
    value: string;
    icon: ReactNode;
    label: string;
}

export interface CardTableHeaderProps {
    title: string;
    description: ReactNode;
    refresh?: {
        onRefresh: () => void;
        isLoading?: boolean;
        tooltip?: string;
    };
    search?: {
        value: string;
        onChange: (value: string) => void;
        placeholder?: string;
    };
    filters?: CardTableHeaderFilter[];
    viewToggle?: {
        value: string;
        onChange: (value: string) => void;
        options: CardTableHeaderViewToggleOption[];
    };
    actions?: ReactNode;
}

export function CardTableHeader({
    title,
    description,
    refresh,
    search,
    filters,
    viewToggle,
    actions
}: CardTableHeaderProps) {
    const hasSecondRow = search || (filters && filters.length > 0) || viewToggle || actions;

    return (
        <CardHeader className="px-6">
            <div className="flex items-center justify-between">
                <div className="space-y-2">
                    <CardTitle>{title}</CardTitle>
                    <CardDescription>{description}</CardDescription>
                </div>
                {refresh && (
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="outline"
                                size="icon"
                                onClick={refresh.onRefresh}
                                disabled={refresh.isLoading}
                                className="cursor-pointer"
                                aria-label={refresh.tooltip ?? 'Refresh'}
                            >
                                <RefreshCw className={`h-4 w-4 ${refresh.isLoading ? 'animate-spin' : ''}`} />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>{refresh.tooltip ?? 'Refresh'}</p>
                        </TooltipContent>
                    </Tooltip>
                )}
            </div>
            {hasSecondRow && (
                <div className="flex items-center justify-between gap-2 mt-2">
                    {search ? (
                        <div className="relative w-1/2">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                placeholder={search.placeholder ?? 'Search...'}
                                value={search.value}
                                onChange={(e) => search.onChange(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                    ) : (
                        <div />
                    )}
                    <div className="flex items-center gap-2">
                        {filters?.map((filter, i) => (
                            <Select key={i} value={filter.value} onValueChange={filter.onChange}>
                                <SelectTrigger className={filter.width ?? 'w-auto min-w-[140px]'}>
                                    <SelectValue placeholder={filter.placeholder} />
                                </SelectTrigger>
                                <SelectContent>
                                    {filter.options.map((opt) => (
                                        <SelectItem key={opt.value} value={opt.value}>
                                            {opt.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        ))}
                        {viewToggle && (
                            <ToggleGroup
                                type="single"
                                value={viewToggle.value}
                                onValueChange={(v) => v && viewToggle.onChange(v)}
                                variant="outline"
                            >
                                {viewToggle.options.map((opt) => (
                                    <ToggleGroupItem key={opt.value} value={opt.value} aria-label={opt.label}>
                                        {opt.icon}
                                    </ToggleGroupItem>
                                ))}
                            </ToggleGroup>
                        )}
                        {actions}
                    </div>
                </div>
            )}
        </CardHeader>
    );
}
