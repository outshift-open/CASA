import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {appService} from '@/services/app.service';
import type {CreateAppRequest, UpdateAppRequest} from '@/types/app.types';

export const useApps = () => {
    return useQuery({
        queryKey: ['apps'],
        queryFn: appService.getApps
    });
};

export const useCreateApp = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (app: CreateAppRequest) => appService.createApp(app),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['apps']});
        }
    });
};

export const useUpdateApp = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({id, app}: {id: string; app: UpdateAppRequest}) => appService.updateApp(id, app),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['apps']});
        }
    });
};

export const useDeleteApp = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: string) => appService.deleteApp(id),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['apps']});
        }
    });
};
