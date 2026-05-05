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

import {useQuery, useMutation, useQueryClient, keepPreviousData} from '@tanstack/react-query';
import {masService} from '@/services/mas.service';
import type {MASQueryParams} from '@/services/mas.service';

export const useMAS = (params?: MASQueryParams) => {
    return useQuery({
        queryKey: ['mas', params],
        queryFn: () => masService.getMAS(params),
        placeholderData: keepPreviousData
    });
};

export const useMASById = (id: string) => {
    return useQuery({
        queryKey: ['mas', id],
        queryFn: () => masService.getMASById(id, {include_metrics: true}),
        enabled: !!id
    });
};

export const useMASApps = (masId: string, live = false) => {
    return useQuery({
        queryKey: ['mas', masId, 'apps'],
        queryFn: () => masService.getMASApps(masId),
        enabled: !!masId,
        refetchInterval: live ? 1000 : false
    });
};

export const useUpdateMAS = (masId: string) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (payload: {name: string; enabled_tool_checks?: number}) => masService.updateMAS(masId, payload),
        onSuccess: (updated) => {
            queryClient.setQueryData(['mas', masId], updated);
            queryClient.invalidateQueries({queryKey: ['mas']});
        }
    });
};
