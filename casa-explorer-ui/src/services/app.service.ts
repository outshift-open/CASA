import {apiClient} from '@/lib/api';
import type {App, AppListResponse} from '@/types/app.types';

export const appService = {
    getApps: async (): Promise<AppListResponse> => {
        const {data} = await apiClient.get('/apps');
        return {
            items: Array.isArray(data) ? data : [],
            total: Array.isArray(data) ? data.length : 0
        };
    },

    getAppById: async (id: string): Promise<App> => {
        const {data} = await apiClient.get(`/apps/${id}`);
        return data;
    }
};
