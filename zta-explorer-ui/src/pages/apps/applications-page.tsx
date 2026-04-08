import {useApps} from '@/hooks/use-apps';
import {toast} from 'sonner';
import {ApiStateHandler} from '@/components/api-state-handler';
import {ApplicationsTable} from '@/components/apps';

export function ApplicationsPage() {
    const {data, isLoading, error, refetch} = useApps();

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Applications refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh apps:', error);
            toast.error('Failed to refresh applications');
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Applications</h1>
                    <p className="text-muted-foreground">Agents, clients, and MCP servers</p>
                </div>
            </div>

            <div>
                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error}
                    error={error as Error}
                    loadingMessage="Loading applications..."
                    errorMessage="Failed to load applications. Please try again."
                    onRetry={() => refetch()}
                >
                    <ApplicationsTable
                        data={data?.items || []}
                        total={data?.total || 0}
                        isLoading={isLoading}
                        onRefresh={handleRefresh}
                    />
                </ApiStateHandler>
            </div>
        </div>
    );
}
