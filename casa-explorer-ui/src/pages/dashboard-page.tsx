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

import {Button} from '@/components/ui/button';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {RefreshCw} from 'lucide-react';
import {useMetrics} from '@/hooks/use-metrics';
import {toast} from 'sonner';
import {StatCards} from '@/components/dashboard/stat-cards';
import {DenyReasonsChart} from '@/components/dashboard/deny-reasons-chart';

export function DashboardPage() {
    const {data, isLoading, error, dataUpdatedAt, refetch} = useMetrics(true);

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Dashboard refreshed successfully');
        } catch {
            toast.error('Failed to refresh dashboard');
        }
    };

    const lastUpdatedLabel = dataUpdatedAt
        ? new Date(dataUpdatedAt).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
          })
        : null;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                    <p className="text-muted-foreground">
                        Overview of your CASA (Continuous Agent Semantic Authorization)
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {lastUpdatedLabel && (
                        <div className="flex items-center text-xs text-muted-foreground">
                            <span>Updated {lastUpdatedLabel} · every 5s</span>
                        </div>
                    )}
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="outline"
                                size="icon"
                                onClick={handleRefresh}
                                disabled={isLoading}
                                className="cursor-pointer"
                                aria-label="Refresh dashboard"
                            >
                                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[180px]">
                            <p>Refresh</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            </div>

            <StatCards data={data} isLoading={isLoading} error={error} />
            <DenyReasonsChart data={data} isLoading={isLoading} />
        </div>
    );
}
