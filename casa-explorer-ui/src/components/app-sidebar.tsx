import * as React from 'react';
import {useLocation} from 'react-router-dom';
import {LayoutDashboard, ChevronLeft, ChevronRight, Network, Tags, Activity} from 'lucide-react';
import {NavLink} from 'react-router-dom';

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    SidebarGroup,
    useSidebar
} from '@/components/ui/sidebar';
import {Button} from '@/components/ui/button';

const mainNavItems = [
    {
        title: 'Dashboard',
        url: '/',
        icon: LayoutDashboard
    },
    {
        title: 'Multi-Agent Systems',
        url: '/mas',
        icon: Network
    },
    {
        title: 'Auth Requests',
        url: '/auth-requests',
        icon: Activity
    }
];

const bottomNavItems: {title: string; url: string; icon: React.ElementType}[] = [];

export function AppSidebar({...props}: React.ComponentProps<typeof Sidebar>) {
    const {toggleSidebar, state} = useSidebar();
    const location = useLocation();

    const isActiveRoute = (url: string) => {
        if (url === '/') {
            return location.pathname === '/';
        }
        if (url === '/agentic-services') {
            return location.pathname === '/agentic-services' || location.pathname.startsWith('/agentic-services/');
        }
        if (url === '/mas') {
            return location.pathname === '/mas' || location.pathname.startsWith('/mas/');
        }
        return location.pathname === url || location.pathname.startsWith(url + '/');
    };

    return (
        <Sidebar collapsible="icon" {...props}>
            <SidebarContent className="pt-2">
                <SidebarGroup>
                    <SidebarMenu>
                        {mainNavItems.map((item) => (
                            <SidebarMenuItem key={item.title}>
                                <SidebarMenuButton tooltip={item.title} asChild isActive={isActiveRoute(item.url)}>
                                    <NavLink to={item.url} end={item.url === '/'}>
                                        {item.icon && <item.icon />}
                                        <span>{item.title}</span>
                                    </NavLink>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        ))}
                        <SidebarMenuItem>
                            <SidebarMenuButton
                                tooltip="Auth scopes (coming soon)"
                                disabled
                                className="opacity-40 cursor-not-allowed"
                            >
                                <Tags />
                                <span>Auth Scopes</span>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter>
                <SidebarMenu>
                    {bottomNavItems.map((item) => (
                        <SidebarMenuItem key={item.title}>
                            <SidebarMenuButton tooltip={item.title} asChild isActive={isActiveRoute(item.url)}>
                                <NavLink to={item.url}>
                                    {item.icon && <item.icon />}
                                    <span>{item.title}</span>
                                </NavLink>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    ))}
                </SidebarMenu>
            </SidebarFooter>
            <Button
                onClick={toggleSidebar}
                variant="ghost"
                size="icon"
                className="absolute top-1/2 -right-[7px] z-20 h-8 w-8 -translate-y-1/2 cursor-pointer rounded-full border border-sidebar-border bg-[#07111F] shadow-md hover:bg-accent"
            >
                {state === 'collapsed' ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
        </Sidebar>
    );
}
