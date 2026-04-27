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

import {useQuery} from '@tanstack/react-query';
import {scopeService} from '@/services/scope.service';

export function useScopes() {
    return useQuery({
        queryKey: ['scopes'],
        queryFn: scopeService.getScopes
    });
}

export function useMASScopes(masId: string) {
    return useQuery({
        queryKey: ['scopes', 'mas', masId],
        queryFn: () => scopeService.getMASScopes(masId),
        enabled: !!masId
    });
}

export function useScopeById(id: string) {
    return useQuery({
        queryKey: ['scopes', id],
        queryFn: () => scopeService.getScopeById(id),
        enabled: !!id
    });
}
