import {apiClient} from '@/lib/api';
import type {MAS} from '@/types/mas.types';
import type {App} from '@/types/app.types';

export const masService = {
    getMAS: async (): Promise<MAS[]> => {
        const {data} = await apiClient.get('/mas');
        return Array.isArray(data) ? data : [];
    },

    getMASById: async (id: string): Promise<MAS> => {
        const {data} = await apiClient.get(`/mas/${id}`);
        return data;
    },

    getMASApps: async (masId: string): Promise<App[]> => {
        const {data} = await apiClient.get(`/mas/${masId}/apps`);
        return Array.isArray(data) ? data : [];
    }
};
