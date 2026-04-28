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

import {useScopes} from '@/hooks/use-scopes';
import {toast} from 'sonner';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ScopesTable} from '@/components/scopes';

export function ScopesPage() {
    const {data, isLoading, error, refetch} = useScopes();

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Scopes refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh scopes:', error);
            toast.error('Failed to refresh scopes');
        }
    };

    const scopes = Array.isArray(data) ? data : [];

    return (
        <div>
            <div className="flex items-center justify-betwee pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Scopes</h1>
                    <p className="text-muted-foreground">Authorization scopes for Multi-Agent Systems</p>
                </div>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading scopes..."
                    errorMessage="Failed to load scopes. Please try again."
                    onRetry={() => refetch()}
                >
                    <ScopesTable data={scopes} total={scopes.length} isLoading={isLoading} onRefresh={handleRefresh} />
                </ApiStateHandler>
            </div>
        </div>
    );
}
