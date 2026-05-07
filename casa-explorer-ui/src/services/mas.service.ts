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

import {apiClient} from '@/lib/api';
import type {MAS, MASListResponse} from '@/types/mas.types';
import type {App} from '@/types/app.types';

export interface MASQueryParams {
    page?: number;
    page_size?: number;
    q?: string;
    include_metrics?: boolean;
}

export const masService = {
    getMAS: async (params?: MASQueryParams): Promise<MASListResponse> => {
        const {data} = await apiClient.get('/mas', {params});
        return data;
    },

    getMASById: async (id: string, params?: {include_metrics?: boolean}): Promise<MAS> => {
        const {data} = await apiClient.get(`/mas/${id}`, {params});
        return data;
    },

    getMASApps: async (masId: string): Promise<App[]> => {
        const {data} = await apiClient.get(`/mas/${masId}/apps`);
        return Array.isArray(data) ? data : [];
    },

    updateMAS: async (masId: string, payload: {name: string; enabled_tool_checks?: number}): Promise<MAS> => {
        const {data} = await apiClient.post(`/mas/${masId}`, payload);
        return data;
    }
};
