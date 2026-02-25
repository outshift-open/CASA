import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {appService} from '@/services/app.service';
import type {CreateAppRequest, UpdateAppRequest} from '@/types/app.types';

export const useApps = () => {
    return useQuery({
        queryKey: ['apps'],
        queryFn: appService.getApps
    });
};

export const useAppById = (id: string) => {
    return useQuery({
        queryKey: ['apps', id],
        queryFn: () => appService.getAppById(id),
        enabled: !!id
    });
};

export const useCreateApp = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (app: CreateAppRequest) => appService.createApp(app),
        onSuccess: (newApp) => {
            queryClient.invalidateQueries({queryKey: ['apps']});
            // Invalidate MAS apps cache since a new app was added to a MAS
            if (newApp.mas_id) {
                queryClient.invalidateQueries({queryKey: ['mas', newApp.mas_id, 'apps']});
            }
        }
    });
};

export const useUpdateApp = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({id, app}: {id: string; app: UpdateAppRequest}) => appService.updateApp(id, app),
        onSuccess: (updatedApp, {id}) => {
            queryClient.invalidateQueries({queryKey: ['apps']});
            queryClient.invalidateQueries({queryKey: ['apps', id]});
            // Invalidate MAS apps cache since app details might have changed
            if (updatedApp.mas_id) {
                queryClient.invalidateQueries({queryKey: ['mas', updatedApp.mas_id, 'apps']});
            }
        }
    });
};

export const useDeleteApp = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: string) => appService.deleteApp(id),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['apps']});
            // Invalidate all MAS apps caches since we don't know which MAS this app belonged to
            queryClient.invalidateQueries({
                queryKey: ['mas'],
                predicate: (query) => query.queryKey.length === 3 && query.queryKey[2] === 'apps'
            });
        }
    });
};
