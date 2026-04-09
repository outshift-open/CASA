import {apiClient} from '@/lib/api';
import type {TraceList} from '@/types/trace.types';

export const traceService = {
    getTraces: async (page = 1, pageSize = 100): Promise<TraceList> => {
        const {data} = await apiClient.get('/trace', {params: {page, page_size: pageSize}});
        return data;
    }
};
