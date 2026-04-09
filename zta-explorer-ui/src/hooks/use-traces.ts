import {useQuery} from '@tanstack/react-query';
import {traceService} from '@/services/trace.service';

export const useTraces = (masId?: string, page = 1, pageSize = 100) => {
    return useQuery({
        queryKey: ['traces', masId, page, pageSize],
        queryFn: () => traceService.getTraces(page, pageSize, masId)
    });
};
