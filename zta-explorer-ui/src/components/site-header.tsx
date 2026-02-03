import {useLocation} from 'react-router-dom';
import {SidebarTrigger} from '@/components/ui/sidebar';
import {ChevronRight} from 'lucide-react';
import {ThemeToggle} from '@/components/theme-toggle';

const routeTitles: Record<string, string> = {
    '/': 'Dashboard',
    '/applications': 'Applications',
    '/settings': 'Settings',
    '/help': 'Get Help',
    '/search': 'Search'
};

export function SiteHeader() {
    const location = useLocation();
    const title = routeTitles[location.pathname] || 'Dashboard';

    return (
        <header className="flex h-14 shrink-0 items-center gap-2 border-b bg-background px-4 rounded-t-xl">
            <SidebarTrigger />
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
            <h1 className="text-base font-semibold">{title}</h1>
            <div className="ml-auto">
                <ThemeToggle />
            </div>
        </header>
    );
}
