import {apiClient} from '@/lib/api';
import type {MAS, CreateMASRequest, UpdateMASRequest, BindAppsRequest} from '@/types/mas.types';

export const masService = {
    getMAS: async (): Promise<MAS[]> => {
        const {data} = await apiClient.get('/mas');
        return Array.isArray(data) ? data : [];
    },

    getMASById: async (id: string): Promise<MAS> => {
        const {data} = await apiClient.get(`/mas/${id}`);
        return data;
    },

    createMAS: async (mas: CreateMASRequest): Promise<MAS> => {
        const {data} = await apiClient.put('/mas', mas);
        return data;
    },

    bindApps: async (masId: string, request: BindAppsRequest): Promise<void> => {
        await apiClient.post(`/mas/${masId}/bind_apps`, request);
    },

    updateMAS: async (masId: string, mas: UpdateMASRequest): Promise<MAS> => {
        const {data} = await apiClient.post(`/mas/${masId}`, mas);
        return data;
    },

    deleteMAS: async (masId: string): Promise<void> => {
        await apiClient.delete(`/mas/${masId}`);
    }
};
