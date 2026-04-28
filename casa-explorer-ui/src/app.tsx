import {BrowserRouter, Routes, Route} from 'react-router-dom';
import {BasePage} from '@/components/base-page';
import {SidebarProvider} from '@/components/ui/sidebar';
import {AppSidebar} from '@/components/app-sidebar';
import {SiteHeader} from '@/components/site-header';
import {DashboardPage} from '@/pages/dashboard-page';
import {MASPage} from '@/pages/mas/mas-page';
import {MASDetailPage} from '@/pages/mas/mas-detail-page';
import {AuthRequestsPage} from '@/pages/auth-requests/auth-requests-page';
import {AuthRequestDetailPage} from '@/pages/auth-requests/auth-request-detail-page';
import {NotFoundPage} from '@/pages/not-found-page';
import {Toaster} from '@/components/ui/sonner';
import {KeyboardShortcutsDialog} from '@/components/keyboard-shortcuts-dialog';

function App() {
    return (
        <BrowserRouter>
            <div className="flex flex-col h-screen overflow-hidden">
                <SiteHeader />
                <div className="flex flex-1 overflow-hidden">
                    <SidebarProvider style={{'--sidebar-width': 'calc(var(--spacing) * 60)'} as React.CSSProperties}>
                        <AppSidebar variant="inset" />
                        <main className="flex-1 overflow-y-auto">
                            <div className="@container/main flex flex-1 flex-col gap-2 p-4 md:p-6">
                                <BasePage>
                                    <Routes>
                                        <Route path="/" element={<DashboardPage />} />
                                        <Route path="/mas" element={<MASPage />} />
                                        <Route path="/mas/:id" element={<MASDetailPage />} />
                                        <Route path="/auth-requests" element={<AuthRequestsPage />} />
                                        <Route path="/auth-requests/:userInputId" element={<AuthRequestDetailPage />} />
                                        <Route path="*" element={<NotFoundPage />} />
                                    </Routes>
                                </BasePage>
                            </div>
                        </main>
                    </SidebarProvider>
                </div>
            </div>
            <Toaster />
            <KeyboardShortcutsDialog />
        </BrowserRouter>
    );
}

export default App;
