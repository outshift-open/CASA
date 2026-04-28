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

import {useApps} from '@/hooks/use-apps';
import {toast} from 'sonner';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ApplicationsTable} from '@/components/apps';

export function ApplicationsPage() {
    const {data, isLoading, error, refetch} = useApps();

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Agentic Services refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh agentic services:', error);
            toast.error('Failed to refresh agentic services');
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Agentic Services</h1>
                    <p className="text-muted-foreground">Agents, clients, and MCP servers</p>
                </div>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading agentic services..."
                    errorMessage="Failed to load agentic services. Please try again."
                    onRetry={() => refetch()}
                >
                    <ApplicationsTable
                        data={data?.items || []}
                        total={data?.total || 0}
                        isLoading={isLoading}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>
        </div>
    );
}
