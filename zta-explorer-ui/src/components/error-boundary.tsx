import React, {Component, ErrorInfo, ReactNode} from 'react';
import {AlertTriangle, RefreshCw} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from '@/components/ui/card';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
            errorInfo: null
        };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
        this.setState({
            error,
            errorInfo
        });
    }

    private handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        });
        window.location.href = '/';
    };

    private handleReload = () => {
        window.location.reload();
    };

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="flex min-h-screen items-center justify-center bg-background p-4">
                    <Card className="w-full max-w-2xl">
                        <CardHeader>
                            <div className="flex items-center gap-3">
                                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
                                    <AlertTriangle className="h-6 w-6 text-destructive" />
                                </div>
                                <div>
                                    <CardTitle className="text-2xl">Something went wrong</CardTitle>
                                    <CardDescription>An unexpected error occurred in the application</CardDescription>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            {this.state.error && (
                                <div className="space-y-4">
                                    <div>
                                        <p className="mb-2 text-sm font-medium">Error Message:</p>
                                        <div className="rounded-md bg-muted p-3">
                                            <code className="text-sm text-destructive">{this.state.error.message}</code>
                                        </div>
                                    </div>
                                    {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                                        <details className="cursor-pointer">
                                            <summary className="text-sm font-medium">
                                                Stack Trace (Development Only)
                                            </summary>
                                            <div className="mt-2 max-h-64 overflow-auto rounded-md bg-muted p-3">
                                                <pre className="text-xs">{this.state.errorInfo.componentStack}</pre>
                                            </div>
                                        </details>
                                    )}
                                </div>
                            )}
                        </CardContent>
                        <CardFooter className="flex gap-3">
                            <Button onClick={this.handleReset} variant="default">
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Go to Dashboard
                            </Button>
                            <Button onClick={this.handleReload} variant="outline">
                                Reload Page
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}
