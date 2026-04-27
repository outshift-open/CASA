import {useQuery} from '@tanstack/react-query';
import {traceService} from '@/services/trace.service';

export const useTraces = (masId?: string, page = 1, pageSize = 100, all = false, live = false) => {
    return useQuery({
        queryKey: ['traces', masId, page, pageSize, all],
        queryFn: () => traceService.getTraces(page, pageSize, masId, all),
        refetchInterval: live ? 1000 : false
    });
};
