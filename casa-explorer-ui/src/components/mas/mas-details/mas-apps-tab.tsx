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

import {useMASApps} from '@/hooks/use-mas';
import {MASAppsTable} from '@/components/mas';
import {Card, CardContent} from '@/components/ui/card';
import {Skeleton} from '@/components/ui/skeleton';
import {AppWindow} from 'lucide-react';
import type {MAS} from '@/types/mas.types';

interface MASAppsTabProps {
    mas: MAS;
}

export function MASAppsTab({mas}: MASAppsTabProps) {
    const {data: apps, isLoading: appsLoading, error: appsError} = useMASApps(mas.id);

    return (
        <div className="space-y-4">
            <div>
                <p className="text-lg font-semibold">Agentic Services</p>
                <p className="text-sm text-muted-foreground">
                    {apps?.length || 0} agentic service{apps?.length !== 1 ? 's' : ''} configured
                </p>
            </div>

            {appsLoading ? (
                <div className="space-y-3">
                    {Array.from({length: 3}).map((_, i) => (
                        <Skeleton key={i} className="w-full h-10" />
                    ))}
                </div>
            ) : appsError ? (
                <Card>
                    <CardContent className="pt-6">
                        <p className="text-sm text-destructive text-center py-8">Error loading agentic services</p>
                    </CardContent>
                </Card>
            ) : apps && apps.length > 0 ? (
                <MASAppsTable mas={mas} apps={apps} />
            ) : (
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                            <AppWindow className="h-10 w-10 opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No agentic services</p>
                                <p className="text-xs mt-1">
                                    This MAS doesn't have any agentic services associated with it
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
