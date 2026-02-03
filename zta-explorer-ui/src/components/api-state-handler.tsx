import {ReactNode} from 'react';
import {AlertCircle, Loader2, RefreshCw} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {Card, CardContent} from '@/components/ui/card';

interface ApiStateHandlerProps {
    isLoading?: boolean;
    isError?: boolean;
    error?: Error | null;
    isEmpty?: boolean;
    loadingMessage?: string;
    errorMessage?: string;
    emptyMessage?: string;
    onRetry?: () => void;
    children: ReactNode;
    fullHeight?: boolean;
}

export function ApiStateHandler({
    isLoading = false,
    isError = false,
    error = null,
    isEmpty = false,
    loadingMessage = 'Loading...',
    errorMessage,
    emptyMessage = 'No data available',
    onRetry,
    children,
    fullHeight = true
}: ApiStateHandlerProps) {
    const loadingClass = fullHeight
        ? 'flex items-center justify-center min-h-[400px]'
        : 'flex items-center justify-center py-8';

    if (isLoading) {
        return (
            <div className={loadingClass}>
                <div className="flex flex-col items-center gap-3">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">{loadingMessage}</p>
                </div>
            </div>
        );
    }

    if (isError) {
        const displayMessage = errorMessage || error?.message || 'An error occurred';

        return (
            <div className="flex items-center justify-center py-8">
                <Card className="w-full border-destructive/50">
                    <CardContent className="p-6">
                        <div className="flex flex-col items-center gap-4 text-center">
                            <div className="rounded-full bg-destructive/10 p-3">
                                <AlertCircle className="h-6 w-6 text-destructive" />
                            </div>
                            <div className="space-y-2">
                                <h3 className="font-semibold text-lg">Error</h3>
                                <p className="text-sm text-muted-foreground">{displayMessage}</p>
                            </div>
                            {onRetry && (
                                <Button variant="outline" onClick={onRetry} className="gap-2">
                                    <RefreshCw className="h-4 w-4" />
                                    Try Again
                                </Button>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (isEmpty) {
        return (
            <div className="flex items-center justify-center py-8">
                <div className="text-center">
                    <p className="text-sm text-muted-foreground">{emptyMessage}</p>
                </div>
            </div>
        );
    }

    return <>{children}</>;
}
