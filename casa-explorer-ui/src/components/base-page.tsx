/**
 * Copyright 2026 Copyright 2026 Cisco Systems, Inc. and its affiliates
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

import {type ReactNode} from 'react';
import {useLocation, Link} from 'react-router-dom';
import {ChevronRight, Home} from 'lucide-react';
import {useMAS} from '@/hooks/use-mas';
import {useTraces} from '@/hooks/use-traces';

const routeTitles: Record<string, string> = {
    '/': 'Dashboard',
    '/mas': 'Multi-Agent Systems',
    '/auth-requests': 'Auth Requests',
    '/settings': 'Settings'
};

const routeRedirects: Record<string, string> = {
    '/mas': '/mas'
};

function Breadcrumbs() {
    const location = useLocation();
    const {data: masData} = useMAS();

    const pathSegments = location.pathname.split('/').filter(Boolean);
    const isAuthRequestDetail = pathSegments[0] === 'auth-requests' && pathSegments.length === 2;
    const authRequestId = isAuthRequestDetail ? pathSegments[1] : undefined;
    const {data: tracesData} = useTraces(undefined, 1, 100, !!authRequestId);
    const authRequestPrompt = authRequestId
        ? tracesData?.items?.[authRequestId]?.find((t) => t.event_type === 'TokenIssuedEvent')?.event.prompt
        : undefined;

    const breadcrumbs: Array<{label: string; path: string; isLast: boolean}> = [];

    let currentPath = '';
    pathSegments.forEach((segment, index) => {
        currentPath += `/${segment}`;
        const isLast = index === pathSegments.length - 1;

        let label = routeTitles[currentPath] || segment;

        if (segment === 'create') {
            label = 'Create';
        } else if (segment === 'edit') {
            label = 'Edit';
        } else if (pathSegments[index - 1] === 'mas' && segment !== 'create') {
            const mas = masData?.find((m) => m.id === segment);
            label = mas?.name || segment;
        } else if (pathSegments[index - 1] === 'auth-requests') {
            label = authRequestPrompt || segment;
        }

        breadcrumbs.push({label, path: routeRedirects[currentPath] || currentPath, isLast});
    });

    if (breadcrumbs.length === 0) {
        breadcrumbs.push({label: 'Dashboard', path: '/', isLast: true});
    }

    if (breadcrumbs.length <= 1) return null;

    return (
        <nav className="flex items-center gap-1 text-sm mb-2">
            <Link to="/" className="text-muted-foreground hover:text-foreground transition-colors">
                <Home className="h-3.5 w-3.5" />
            </Link>
            {breadcrumbs.map((crumb) => (
                <div key={crumb.path} className="flex items-center gap-1">
                    <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50" />
                    {crumb.isLast ? (
                        <span className="text-foreground font-medium">{crumb.label}</span>
                    ) : (
                        <Link to={crumb.path} className="text-muted-foreground hover:text-foreground transition-colors">
                            {crumb.label}
                        </Link>
                    )}
                </div>
            ))}
        </nav>
    );
}

export function BasePage({children}: {children: ReactNode}) {
    return (
        <div className="flex flex-col gap-4 md:gap-6">
            <Breadcrumbs />
            {children}
        </div>
    );
}
