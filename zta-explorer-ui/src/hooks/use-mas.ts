import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
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

export const useUpdateMAS = (masId: string) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (payload: {name: string; enabled_tool_checks?: number}) => masService.updateMAS(masId, payload),
        onSuccess: (updated) => {
            queryClient.setQueryData(['mas', masId], updated);
            queryClient.invalidateQueries({queryKey: ['mas']});
        }
    });
};
