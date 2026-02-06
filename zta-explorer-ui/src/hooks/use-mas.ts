import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {masService} from '@/services/mas.service';

export const useMAS = () => {
    return useQuery({
        queryKey: ['mas'],
        queryFn: masService.getMAS
    });
};

export const useCreateMAS = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({name, app_ids}: {name: string; app_ids: string[]}) => {
            // Step 1: Create MAS
            const mas = await masService.createMAS({name});

            // Step 2: Bind apps if any
            if (app_ids.length > 0) {
                await masService.bindApps(mas.id, {app_ids});
            }

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
        mutationFn: async ({id, name, app_ids}: {id: string; name: string; app_ids: string[]}) => {
            // Update MAS name
            const mas = await masService.updateMAS(id, {name});

            // Update bound apps
            await masService.bindApps(id, {app_ids});

            return mas;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['mas']});
        }
    });
};

export const useDeleteMAS = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: string) => masService.deleteMAS(id),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['mas']});
        }
    });
};
