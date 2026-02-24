import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
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

export const useCreateMAS = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({name}: {name: string; app_ids?: string[]}) => {
            // Create MAS - apps are added later when creating apps with mas_id
            const mas = await masService.createMAS({name});
            return mas;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['mas']});
        }
    });
};

export const useUpdateMAS = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({id, name}: {id: string; name: string}) => {
            // Update MAS name only - apps manage their own mas_id
            const mas = await masService.updateMAS(id, {name});
            return mas;
        },
        onSuccess: (_, {id}) => {
            queryClient.invalidateQueries({queryKey: ['mas']});
            queryClient.invalidateQueries({queryKey: ['mas', id]});
            queryClient.invalidateQueries({queryKey: ['mas', id, 'apps']});
        }
    });
};

export const useDeleteMAS = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: string) => masService.deleteMAS(id),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['mas']});
            // Invalidate apps since deleting MAS cascades to delete its apps
            queryClient.invalidateQueries({queryKey: ['apps']});
        }
    });
};
