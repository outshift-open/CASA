/**
 * Copyright 2026 Copyright 2026 Cisco Systems, Inc. and its affiliates
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {ReactNode} from 'react';
import {AlertCircle, RefreshCw} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {Card, CardContent} from '@/components/ui/card';
import {Skeleton} from '@/components/ui/skeleton';

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
    errorMessage,
    emptyMessage = 'No data available',
    onRetry,
    children
}: ApiStateHandlerProps) {
    if (isLoading) {
        return (
            <div className="space-y-3">
                {Array.from({length: 5}).map((_, i) => (
                    <Skeleton key={i} className="w-full h-10" />
                ))}
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
