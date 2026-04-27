/**
 * Copyright 2026 Google LLC
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

import {useLocation, Link} from 'react-router-dom';
import {ChevronRight, Home} from 'lucide-react';
import {ThemeToggle} from '@/components/theme-toggle';
import {useApps} from '@/hooks/use-apps';
import {useMAS} from '@/hooks/use-mas';
import {useScopes} from '@/hooks/use-scopes';
import {Button} from '@/components/ui/button';

const routeTitles: Record<string, string> = {
    '/': 'Dashboard',
    '/agentic-services': 'Agentic Services',
    '/mas': 'Multi-Agent Systems',
    '/scopes': 'Scopes',
    '/settings': 'Settings',
    '/help': 'Get Help',
    '/search': 'Search'
};

// Map breadcrumb paths to actual routes
const routeRedirects: Record<string, string> = {
    '/agentic-services': '/agentic-services',
    '/mas': '/mas',
    '/scopes': '/scopes'
};

export function SiteHeader() {
    const location = useLocation();
    const {data: appsData} = useApps();
    const {data: masData} = useMAS();
    const {data: scopesData} = useScopes();

    // Parse the current path into breadcrumb segments
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: Array<{label: string; path: string; isLast: boolean}> = [];

    // Build breadcrumbs from path segments (never add Dashboard automatically)
    let currentPath = '';
    pathSegments.forEach((segment, index) => {
        currentPath += `/${segment}`;
        const isLast = index === pathSegments.length - 1;

        // Determine the label for this segment
        let label = routeTitles[currentPath] || segment;

        // Handle special cases for IDs and actions
        if (segment === 'create') {
            label = 'Create';
        } else if (segment === 'edit') {
            label = 'Edit';
        } else if (pathSegments[index - 1] === 'agentic-services' && segment !== 'create') {
            // It's a service ID - try to find the service name
            const app = appsData?.items?.find((a) => a.id === segment);
            label = app?.name || segment;
        } else if (pathSegments[index - 1] === 'mas' && segment !== 'create') {
            // It's a MAS ID - try to find the MAS name
            const mas = masData?.find((m) => m.id === segment);
            label = mas?.name || segment;
        } else if (pathSegments[index - 1] === 'scopes' && segment !== 'create') {
            // It's a scope ID - try to find the scope name
            const scope = Array.isArray(scopesData) ? scopesData.find((s) => s.id === segment) : null;
            label = scope?.name || segment;
        }

        breadcrumbs.push({
            label,
            path: routeRedirects[currentPath] || currentPath,
            isLast
        });
    });

    // If we're on the root and no breadcrumbs, show Dashboard
    if (breadcrumbs.length === 0) {
        breadcrumbs.push({
            label: 'Dashboard',
            path: '/',
            isLast: true
        });
    }

    return (
        <header className="flex h-14 shrink-0 items-center gap-1 border-b bg-background px-4 rounded-t-xl">
            <Button variant="ghost" size="icon" asChild>
                <Link to="/">
                    <Home className="h-4 w-4" />
                </Link>
            </Button>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
            <div className="flex items-center gap-1">
                {breadcrumbs.map((crumb, index) => (
                    <div key={crumb.path} className="flex items-center gap-1">
                        {index > 0 && <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                        {crumb.isLast ? (
                            <span className="text-base font-semibold">{crumb.label}</span>
                        ) : (
                            <Link
                                to={crumb.path}
                                className="text-base text-muted-foreground hover:text-foreground transition-colors"
                            >
                                {crumb.label}
                            </Link>
                        )}
                    </div>
                ))}
            </div>
            <div className="ml-auto flex items-center gap-1">
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                    onClick={() => window.dispatchEvent(new KeyboardEvent('keydown', {key: '?', bubbles: true}))}
                    title="Keyboard shortcuts"
                >
                    <kbd className="text-xs font-mono font-semibold">?</kbd>
                </Button>
                <ThemeToggle />
            </div>
        </header>
    );
}
