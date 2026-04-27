/**
 * Copyright 2026 Google LLC
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
import type {TraceList} from '@/types/trace.types';

export const traceService = {
    getTraces: async (page = 1, pageSize = 100, masId?: string, all = false): Promise<TraceList> => {
        const {data} = await apiClient.get('/trace', {params: {page, page_size: pageSize, mas_id: masId, all}});
        return data;
    }
};
