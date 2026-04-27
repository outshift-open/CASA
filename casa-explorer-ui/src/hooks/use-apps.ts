import {useQuery} from '@tanstack/react-query';
import {appService} from '@/services/app.service';

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
