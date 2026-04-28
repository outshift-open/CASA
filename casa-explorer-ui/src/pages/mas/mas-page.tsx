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

import {useMAS} from '@/hooks/use-mas';
import {toast} from 'sonner';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MASTable} from '@/components/mas';

export function MASPage() {
    const {data, isLoading, error, refetch} = useMAS();

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('MAS refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh MAS:', error);
            toast.error('Failed to refresh MAS');
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Multi-Agent Systems</h1>
                    <p className="text-muted-foreground">Multi-agent systems registered in this workspace.</p>
                </div>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading MAS..."
                    errorMessage="Failed to load MAS. Please try again."
                    onRetry={() => refetch()}
                >
                    <MASTable
                        data={data || []}
                        total={data?.length || 0}
                        isLoading={isLoading}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>
        </div>
    );
}
