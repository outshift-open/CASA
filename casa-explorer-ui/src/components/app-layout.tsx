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

import type React from 'react';
import {Outlet} from 'react-router-dom';
import {SidebarProvider} from '@/components/ui/sidebar';
import {AppSidebar} from '@/components/app-sidebar';
import {SiteHeader} from '@/components/site-header';
import {BasePage} from '@/components/base-page';
import {Toaster} from '@/components/ui/sonner';
import {KeyboardShortcutsDialog} from '@/components/keyboard-shortcuts-dialog';

export function AppLayout() {
    return (
        <div className="flex flex-col h-screen overflow-hidden">
            <SiteHeader />
            <div className="flex flex-1 overflow-hidden">
                <SidebarProvider style={{'--sidebar-width': 'calc(var(--spacing) * 60)'} as React.CSSProperties}>
                    <AppSidebar variant="inset" />
                    <main className="flex-1 overflow-y-auto">
                        <div className="@container/main flex flex-1 flex-col gap-2 p-4 md:p-6">
                            <BasePage>
                                <Outlet />
                            </BasePage>
                        </div>
                    </main>
                </SidebarProvider>
            </div>
            <Toaster />
            <KeyboardShortcutsDialog />
        </div>
    );
}
