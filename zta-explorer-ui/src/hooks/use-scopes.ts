import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
import {scopeService} from '@/services/scope.service';
import type {ScopeCreateRequest, ScopeUpdateRequest} from '@/types/scope.types';

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

export function useCreateScope() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (request: ScopeCreateRequest) => scopeService.createScope(request),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({queryKey: ['scopes']});
            queryClient.invalidateQueries({queryKey: ['scopes', 'mas', variables.mas_id]});
        }
    });
}

export function useUpdateScope() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({id, request}: {id: string; request: ScopeUpdateRequest}) => scopeService.updateScope(id, request),
        onSuccess: (data) => {
            queryClient.invalidateQueries({queryKey: ['scopes']});
            queryClient.invalidateQueries({queryKey: ['scopes', data.id]});
            queryClient.invalidateQueries({queryKey: ['scopes', 'mas', data.mas_id]});
        }
    });
}

export function useDeleteScope() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: string) => scopeService.deleteScope(id),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['scopes']});
        }
    });
}
