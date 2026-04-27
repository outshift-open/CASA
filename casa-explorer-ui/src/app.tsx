import {BrowserRouter, Routes, Route} from 'react-router-dom';
import {SidebarInset, SidebarProvider} from '@/components/ui/sidebar';
import {AppSidebar} from '@/components/app-sidebar';
import {SiteHeader} from '@/components/site-header';
import {DashboardPage} from '@/pages/dashboard-page';
import {MASPage} from '@/pages/mas/mas-page';
import {MASDetailPage} from '@/pages/mas/mas-detail-page';
import {AuthRequestsPage} from '@/pages/auth-requests/auth-requests-page';
import {AuthRequestDetailPage} from '@/pages/auth-requests/auth-request-detail-page';
import {SettingsPage} from '@/pages/settings-page';
import {NotFoundPage} from '@/pages/not-found-page';
import {Toaster} from '@/components/ui/sonner';
import {KeyboardShortcutsDialog} from '@/components/keyboard-shortcuts-dialog';

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
                                <Route path="/mas" element={<MASPage />} />
                                <Route path="/mas/:id" element={<MASDetailPage />} />
                                <Route path="/auth-requests" element={<AuthRequestsPage />} />
                                <Route path="/auth-requests/:userInputId" element={<AuthRequestDetailPage />} />
                                <Route path="/settings" element={<SettingsPage />} />
                                <Route path="*" element={<NotFoundPage />} />
                            </Routes>
                        </div>
                    </div>
                </SidebarInset>
            </SidebarProvider>
            <Toaster />
            <KeyboardShortcutsDialog />
        </BrowserRouter>
    );
}

export default App;
