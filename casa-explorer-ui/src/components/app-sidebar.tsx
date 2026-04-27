import * as React from 'react';
import {useLocation} from 'react-router-dom';
import {
    Settings,
    LayoutDashboard,
    MoreVertical,
    User,
    Bell,
    LogOut,
    ChevronLeft,
    ChevronRight,
    Network,
    Tags,
    Activity
} from 'lucide-react';
import {NavLink} from 'react-router-dom';

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    SidebarGroup,
    SidebarSeparator,
    useSidebar
} from '@/components/ui/sidebar';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {Avatar, AvatarFallback} from '@/components/ui/avatar';
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

const bottomNavItems = [
    {
        title: 'Settings',
        url: '/settings',
        icon: Settings
    }
];

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
            <SidebarHeader>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton size="lg" asChild>
                            <NavLink to="/">
                                <div className="flex aspect-square size-8 items-center justify-center">
                                    <img src="/logo.svg" alt="CASA" className="size-8" />
                                </div>
                                <div className="grid flex-1 text-left text-sm leading-tight ml-2">
                                    <span className="truncate font-semibold">CASA Explorer</span>
                                </div>
                            </NavLink>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>
            <SidebarContent>
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
                <SidebarSeparator className="mx-0" />
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton
                                    size="lg"
                                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground cursor-pointer"
                                >
                                    <Avatar className="h-8 w-8 rounded-lg">
                                        <AvatarFallback className="rounded-lg bg-gradient-to-br from-[#006B8A] to-[#00BCEB] text-white font-bold">
                                            AS
                                        </AvatarFallback>
                                    </Avatar>
                                    <div className="grid flex-1 text-left text-sm leading-tight">
                                        <span className="truncate font-semibold">Admin</span>
                                        <span className="truncate text-xs text-muted-foreground">admin@casa.local</span>
                                    </div>
                                    <MoreVertical className="ml-auto size-4" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
                                side="right"
                                align="end"
                                sideOffset={4}
                            >
                                <DropdownMenuLabel className="p-0 font-normal">
                                    <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                                        <Avatar className="h-8 w-8 rounded-lg">
                                            <AvatarFallback className="rounded-lg bg-gradient-to-br from-[#006B8A] to-[#00BCEB] text-white font-bold">
                                                AS
                                            </AvatarFallback>
                                        </Avatar>
                                        <div className="grid flex-1 text-left text-sm leading-tight">
                                            <span className="truncate font-semibold">Admin</span>
                                            <span className="truncate text-xs text-muted-foreground">
                                                admin@casa.local
                                            </span>
                                        </div>
                                    </div>
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem disabled className="cursor-pointer">
                                    <User className="mr-2 h-4 w-4" />
                                    Account
                                </DropdownMenuItem>
                                <DropdownMenuItem disabled className="cursor-pointer">
                                    <Bell className="mr-2 h-4 w-4" />
                                    Notifications
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem disabled className="cursor-pointer">
                                    <LogOut className="mr-2 h-4 w-4" />
                                    Log out
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
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
