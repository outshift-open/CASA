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
import type {Scope} from '@/types/scope.types';

export const scopeService = {
    getScopes: async (): Promise<Scope[]> => {
        const {data} = await apiClient.get('/scopes');
        return Array.isArray(data) ? data : [];
    },

    getScopeById: async (id: string): Promise<Scope> => {
        const {data} = await apiClient.get(`/scopes/${id}`);
        return data;
    },

    getMASScopes: async (masId: string): Promise<Scope[]> => {
        const {data} = await apiClient.get('/scopes');
        const scopes = Array.isArray(data) ? data : [];
        return scopes.filter((scope: Scope) => scope.mas_id === masId);
    }
};
