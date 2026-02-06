import {BrowserRouter, Routes, Route} from 'react-router-dom';
import {SidebarInset, SidebarProvider} from '@/components/ui/sidebar';
import {AppSidebar} from '@/components/app-sidebar';
import {SiteHeader} from '@/components/site-header';
import {DashboardPage} from '@/pages/dashboard-page';
import {ApplicationsPage} from '@/pages/apps/applications-page';
import {AppDetailPage} from '@/pages/apps/app-detail-page';
import {AppEditPage} from '@/pages/apps/app-edit-page';
import {AppCreatePage} from '@/pages/apps/app-create-page';
import {MASPage} from '@/pages/mas/mas-page';
import {MASDetailPage} from '@/pages/mas/mas-detail-page';
import {MASEditPage} from '@/pages/mas/mas-edit-page';
import {MASCreatePage} from '@/pages/mas/mas-create-page';
import {SettingsPage} from '@/pages/settings-page';
import {NotFoundPage} from '@/pages/not-found-page';
import {Toaster} from '@/components/ui/sonner';

function App() {
    return (
        <BrowserRouter>
            <SidebarProvider
                style={
                    {
                        '--sidebar-width': 'calc(var(--spacing) * 60)'
                    } as React.CSSProperties
                }
            >
                <AppSidebar variant="inset" />
                <SidebarInset>
                    <SiteHeader />
                    <div className="@container/main flex flex-1 flex-col gap-2 p-4 md:p-6">
                        <div className="flex flex-col gap-4 md:gap-6">
                            <Routes>
                                <Route path="/" element={<DashboardPage />} />
                                <Route path="/applications" element={<ApplicationsPage />} />
                                <Route path="/apps/create" element={<AppCreatePage />} />
                                <Route path="/apps/:id" element={<AppDetailPage />} />
                                <Route path="/apps/:id/edit" element={<AppEditPage />} />
                                <Route path="/mas" element={<MASPage />} />
                                <Route path="/mas/create" element={<MASCreatePage />} />
                                <Route path="/mas/:id" element={<MASDetailPage />} />
                                <Route path="/mas/:id/edit" element={<MASEditPage />} />
                                <Route path="/settings" element={<SettingsPage />} />
                                <Route path="*" element={<NotFoundPage />} />
                            </Routes>
                        </div>
                    </div>
                </SidebarInset>
            </SidebarProvider>
            <Toaster />
        </BrowserRouter>
    );
}

export default App;
