import {useQuery} from '@tanstack/react-query';
import {scopeService} from '@/services/scope.service';

export function useScopes() {
    return useQuery({
        queryKey: ['scopes'],
        queryFn: scopeService.getScopes
    });
}

export function useMASScopes(masId: string) {
    return useQuery({
        queryKey: ['scopes', 'mas', masId],
        queryFn: () => scopeService.getMASScopes(masId),
        enabled: !!masId
    });
}

export function useScopeById(id: string) {
    return useQuery({
        queryKey: ['scopes', id],
        queryFn: () => scopeService.getScopeById(id),
        enabled: !!id
    });
}
