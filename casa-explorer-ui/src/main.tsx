import {createRoot} from 'react-dom/client';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {ThemeProvider} from '@/components/theme-provider';
import {ErrorBoundary} from '@/components/error-boundary';
import App from './app.tsx';
import './styles/globals.css';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            refetchOnWindowFocus: false,
            refetchOnMount: true
        }
    }
});

createRoot(document.getElementById('root')!).render(
    <>
        <ErrorBoundary>
            <ThemeProvider attribute="class" defaultTheme="ioc" enableSystem={false} themes={['light', 'dark', 'ioc']}>
                <QueryClientProvider client={queryClient}>
                    <App />
                </QueryClientProvider>
            </ThemeProvider>
        </ErrorBoundary>
    </>
);
