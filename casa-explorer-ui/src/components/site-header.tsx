import {useLocation, Link} from 'react-router-dom';
import {ChevronRight, Home, BookOpen, Github} from 'lucide-react';
import {ThemeToggle} from '@/components/theme-toggle';
import {useMAS} from '@/hooks/use-mas';
import {useTraces} from '@/hooks/use-traces';
import {Button} from '@/components/ui/button';

const routeTitles: Record<string, string> = {
    '/': 'Dashboard',
    '/mas': 'Multi-Agent Systems',
    '/auth-requests': 'Auth Requests',
    '/settings': 'Settings'
};

const routeRedirects: Record<string, string> = {
    '/mas': '/mas'
};

export function SiteHeader() {
    const location = useLocation();
    const {data: masData} = useMAS();

    const pathSegments = location.pathname.split('/').filter(Boolean);
    const isAuthRequestDetail = pathSegments[0] === 'auth-requests' && pathSegments.length === 2;
    const authRequestId = isAuthRequestDetail ? pathSegments[1] : undefined;
    const {data: tracesData} = useTraces(undefined, 1, 100, !!authRequestId);
    const authRequestPrompt = authRequestId
        ? tracesData?.items?.[authRequestId]?.find((t) => t.event_type === 'TokenIssuedEvent')?.event.prompt
        : undefined;

    const breadcrumbs: Array<{label: string; path: string; isLast: boolean}> = [];

    let currentPath = '';
    pathSegments.forEach((segment, index) => {
        currentPath += `/${segment}`;
        const isLast = index === pathSegments.length - 1;

        let label = routeTitles[currentPath] || segment;

        if (segment === 'create') {
            label = 'Create';
        } else if (segment === 'edit') {
            label = 'Edit';
        } else if (pathSegments[index - 1] === 'mas' && segment !== 'create') {
            const mas = masData?.find((m) => m.id === segment);
            label = mas?.name || segment;
        } else if (pathSegments[index - 1] === 'auth-requests') {
            label = authRequestPrompt || segment;
        }

        breadcrumbs.push({
            label,
            path: routeRedirects[currentPath] || currentPath,
            isLast
        });
    });

    if (breadcrumbs.length === 0) {
        breadcrumbs.push({label: 'Dashboard', path: '/', isLast: true});
    }

    return (
        <header className="flex h-14 shrink-0 items-center gap-1 border-b bg-background px-4 rounded-t-xl">
            <Button variant="ghost" size="icon" asChild>
                <Link to="/">
                    <Home className="h-4 w-4" />
                </Link>
            </Button>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
            <div className="flex items-center gap-1">
                {breadcrumbs.map((crumb, index) => (
                    <div key={crumb.path} className="flex items-center gap-1">
                        {index > 0 && <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                        {crumb.isLast ? (
                            <span className="text-base font-semibold">{crumb.label}</span>
                        ) : (
                            <Link
                                to={crumb.path}
                                className="text-base text-muted-foreground hover:text-foreground transition-colors"
                            >
                                {crumb.label}
                            </Link>
                        )}
                    </div>
                ))}
            </div>
            <div className="ml-auto flex items-center gap-1">
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                    title="Documentation"
                >
                    <BookOpen className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                    title="GitHub"
                >
                    <Github className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                    onClick={() => window.dispatchEvent(new KeyboardEvent('keydown', {key: '?', bubbles: true}))}
                    title="Keyboard shortcuts"
                >
                    <kbd className="text-xs font-mono font-semibold">?</kbd>
                </Button>
                <ThemeToggle />
            </div>
        </header>
    );
}
