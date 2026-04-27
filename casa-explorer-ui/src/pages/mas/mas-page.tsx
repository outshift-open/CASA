import {useMAS} from '@/hooks/use-mas';
import {toast} from 'sonner';
import {ApiStateHandler} from '@/components/api-state-handler';
import {MASTable} from '@/components/mas';

export function MASPage() {
    const {data, isLoading, error, refetch} = useMAS();

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('MAS refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh MAS:', error);
            toast.error('Failed to refresh MAS');
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Multi-Agent Systems</h1>
                    <p className="text-muted-foreground">Multi-Agent Systems</p>
                </div>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading MAS..."
                    errorMessage="Failed to load MAS. Please try again."
                    onRetry={() => refetch()}
                >
                    <MASTable
                        data={data || []}
                        total={data?.length || 0}
                        isLoading={isLoading}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>
        </div>
    );
}
