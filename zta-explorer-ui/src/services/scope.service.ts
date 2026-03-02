import {apiClient} from '@/lib/api';
import type {Scope, ScopeCreateRequest, ScopeUpdateRequest} from '@/types/scope.types';

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
    },

    createScope: async (request: ScopeCreateRequest): Promise<Scope> => {
        const {data} = await apiClient.post('/scopes', request);
        return data;
    },

    updateScope: async (id: string, request: ScopeUpdateRequest): Promise<Scope> => {
        const {data} = await apiClient.put(`/scopes/${id}`, request);
        return data;
    },

    deleteScope: async (id: string): Promise<void> => {
        await apiClient.delete(`/scopes/${id}`);
    }
};
