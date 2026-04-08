import {useQuery} from '@tanstack/react-query';
import {masService} from '@/services/mas.service';

export const useMAS = () => {
    return useQuery({
        queryKey: ['mas'],
        queryFn: masService.getMAS
    });
};

export const useMASById = (id: string) => {
    return useQuery({
        queryKey: ['mas', id],
        queryFn: () => masService.getMASById(id),
        enabled: !!id
    });
};

export const useMASApps = (masId: string) => {
    return useQuery({
        queryKey: ['mas', masId, 'apps'],
        queryFn: () => masService.getMASApps(masId),
        enabled: !!masId,
        refetchOnMount: 'always'
    });
};
