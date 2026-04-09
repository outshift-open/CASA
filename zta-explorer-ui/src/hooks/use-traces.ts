import {useQuery} from '@tanstack/react-query';
import {traceService} from '@/services/trace.service';

export const useTraces = () => {
    return useQuery({
        queryKey: ['traces'],
        queryFn: () => traceService.getTraces()
    });
};
