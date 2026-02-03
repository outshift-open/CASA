import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarFooter
} from '@/components/ui/sidebar';
import {Home, Settings, Shield, Users} from 'lucide-react';

const menuItems = [
    {
        title: 'Dashboard',
        icon: Home,
        url: '#'
    },
    {
        title: 'Applications',
        icon: Users,
        url: '#applications'
    },
    {
        title: 'Authorization',
        icon: Shield,
        url: '#authorization'
    },
    {
        title: 'Settings',
        icon: Settings,
        url: '#settings'
    }
];

export function AppSidebar() {
    return (
        <Sidebar>
            <SidebarHeader className="border-b px-6 py-4">
                <div className="flex items-center gap-2">
                    <Shield className="h-6 w-6 text-primary" />
                    <div>
                        <h2 className="text-lg font-semibold">ZTA Explorer</h2>
                        <p className="text-xs text-muted-foreground">Identity & Authorization</p>
                    </div>
                </div>
            </SidebarHeader>
            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel>Navigation</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {menuItems.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton asChild>
                                        <a href={item.url} className="flex items-center gap-3">
                                            <item.icon className="h-4 w-4" />
                                            <span>{item.title}</span>
                                        </a>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter className="border-t p-4">
                <div className="text-xs text-muted-foreground">
                    <p>v1.0.0</p>
                    <p className="mt-1">© 2026 Outshift by Cisco</p>
                </div>
            </SidebarFooter>
        </Sidebar>
    );
}
