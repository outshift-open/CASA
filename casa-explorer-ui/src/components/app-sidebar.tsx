/**
 * Copyright 2026 Cisco Systems, Inc. and its affiliates
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

import * as React from 'react';
import {useLocation} from 'react-router-dom';
import {LayoutDashboard, ChevronLeft, ChevronRight, Network, Tags, Activity} from 'lucide-react';
import {NavLink} from 'react-router-dom';
import {PATHS} from '@/router/paths';

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
    {title: 'Dashboard', url: PATHS.dashboard, icon: LayoutDashboard},
    {title: 'Multi-Agent Systems', url: PATHS.mas.list, icon: Network},
    {title: 'Auth Requests', url: PATHS.authRequests.list, icon: Activity}
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
                                tooltip="Auth Scopes (coming soon)"
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
