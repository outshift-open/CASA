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
import type {Trace, TraceList} from '@/types/trace.types';

export interface TraceQueryParams {
    page?: number;
    pageSize?: number;
    masId?: string;
    all?: boolean;
    sortAsc?: boolean;
    userInputId?: string;
    blocked?: boolean;
    q?: string;
    eventType?: string;
    blockingType?: string;
}

export const traceService = {
    getSession: async (userInputId: string): Promise<Trace[]> => {
        const {data} = await apiClient.get(`/trace/session/${userInputId}`);
        return data;
    },

    getTraces: async (params: TraceQueryParams = {}): Promise<TraceList> => {
        const {
            page = 1,
            pageSize = 20,
            masId,
            all = false,
            sortAsc = false,
            userInputId,
            blocked,
            q,
            eventType,
            blockingType
        } = params;
        const {data} = await apiClient.get('/trace', {
            params: {
                page,
                page_size: pageSize,
                mas_id: masId,
                all,
                sort_asc: sortAsc,
                user_input_id: userInputId,
                blocked,
                q,
                event_type: eventType,
                blocking_type: blockingType
            }
        });
        return data;
    }
};
