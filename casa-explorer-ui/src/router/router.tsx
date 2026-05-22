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

import {lazy, Suspense} from 'react';
import {createBrowserRouter} from 'react-router-dom';
import {AppLayout} from '@/components/app-layout';
import {PATHS} from './paths';

const DashboardPage = lazy(() => import('@/pages/dashboard-page').then((m) => ({default: m.DashboardPage})));
const MASPage = lazy(() => import('@/pages/mas/mas-page').then((m) => ({default: m.MASPage})));
const MASDetailPage = lazy(() => import('@/pages/mas/mas-detail-page').then((m) => ({default: m.MASDetailPage})));
const AuthRequestsPage = lazy(() =>
    import('@/pages/auth-requests/auth-requests-page').then((m) => ({default: m.AuthRequestsPage}))
);
const AuthRequestDetailPage = lazy(() =>
    import('@/pages/auth-requests/auth-request-detail-page').then((m) => ({default: m.AuthRequestDetailPage}))
);
const NotFoundPage = lazy(() => import('@/pages/not-found-page').then((m) => ({default: m.NotFoundPage})));

const S = ({children}: {children: React.ReactNode}) => <Suspense fallback={null}>{children}</Suspense>;

export const router = createBrowserRouter([
    {
        path: PATHS.dashboard,
        element: <AppLayout />,
        children: [
            {
                index: true,
                element: (
                    <S>
                        <DashboardPage />
                    </S>
                )
            },
            {
                path: PATHS.mas.list,
                element: (
                    <S>
                        <MASPage />
                    </S>
                )
            },
            {
                path: PATHS.mas.detailPattern,
                element: (
                    <S>
                        <MASDetailPage />
                    </S>
                )
            },
            {
                path: PATHS.authRequests.list,
                element: (
                    <S>
                        <AuthRequestsPage />
                    </S>
                )
            },
            {
                path: PATHS.authRequests.detailPattern,
                element: (
                    <S>
                        <AuthRequestDetailPage />
                    </S>
                )
            },
            {
                path: '*',
                element: (
                    <S>
                        <NotFoundPage />
                    </S>
                )
            }
        ]
    }
]);
