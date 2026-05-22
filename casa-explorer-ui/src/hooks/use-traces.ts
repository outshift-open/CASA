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

import {useQuery, keepPreviousData} from '@tanstack/react-query';
import {traceService} from '@/services/trace.service';
import type {TraceQueryParams} from '@/services/trace.service';

export const useTraces = (params: TraceQueryParams = {}, live = false, enabled = true) => {
    return useQuery({
        queryKey: ['traces', params],
        queryFn: () => traceService.getTraces(params),
        refetchInterval: live ? (query) => (query.state.error ? false : 1000) : false,
        placeholderData: keepPreviousData,
        enabled
    });
};

export const useSession = (userInputId: string | undefined) => {
    return useQuery({
        queryKey: ['session', userInputId],
        queryFn: () => traceService.getSession(userInputId!),
        enabled: !!userInputId,
        staleTime: 30_000
    });
};
