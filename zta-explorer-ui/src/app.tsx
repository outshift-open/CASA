import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom';
import {SidebarInset, SidebarProvider} from '@/components/ui/sidebar';
import {AppSidebar} from '@/components/app-sidebar';
import {SiteHeader} from '@/components/site-header';
import {DashboardPage} from '@/pages/dashboard-page';
import {ApplicationsPage} from '@/pages/applications-page';
import {SettingsPage} from '@/pages/settings-page';
import {HelpPage} from '@/pages/help-page';
import {SearchPage} from '@/pages/search-page';
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
                                <Route path="/settings" element={<SettingsPage />} />
                                <Route path="/help" element={<HelpPage />} />
                                <Route path="/search" element={<SearchPage />} />
                                <Route path="*" element={<Navigate to="/" replace />} />
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
