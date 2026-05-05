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

import {apiClient} from '@/lib/api';

export interface BlockReasonStat {
    reason: string;
    count: number;
}

export interface DashboardStats {
    total_mas: number;
    token_requests: number;
    mcp_calls_allowed: number;
    mcp_calls_denied: number;
    total_mcp_calls: number;
    deterministic_blocks: number;
    ai_powered_blocks: number;
    block_reasons: BlockReasonStat[];
}

export const metricsService = {
    getMetrics: async (): Promise<DashboardStats> => {
        const {data} = await apiClient.get('/metrics');
        return data;
    }
};
