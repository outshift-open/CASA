import {apiClient} from '@/lib/api';
import type {App, AppListResponse, CreateAppRequest, UpdateAppRequest} from '@/types/app.types';

export const appService = {
    getApps: async (): Promise<AppListResponse> => {
        const {data} = await apiClient.get('/apps');
        return {
            items: Array.isArray(data) ? data : [],
            total: Array.isArray(data) ? data.length : 0
        };
    },

    createApp: async (app: CreateAppRequest): Promise<App> => {
        const {data} = await apiClient.post('/apps', app);
        return data;
    },

    updateApp: async (id: string, app: UpdateAppRequest): Promise<App> => {
        const {data} = await apiClient.put(`/apps/${id}`, app);
        return data;
    },

    deleteApp: async (id: string): Promise<void> => {
        await apiClient.delete(`/apps/${id}`);
    }
};
