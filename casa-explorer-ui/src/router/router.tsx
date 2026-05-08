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

import {createBrowserRouter} from 'react-router-dom';
import {AppLayout} from '@/components/app-layout';
import {DashboardPage} from '@/pages/dashboard-page';
import {MASPage} from '@/pages/mas/mas-page';
import {MASDetailPage} from '@/pages/mas/mas-detail-page';
import {AuthRequestsPage} from '@/pages/auth-requests/auth-requests-page';
import {AuthRequestDetailPage} from '@/pages/auth-requests/auth-request-detail-page';
import {NotFoundPage} from '@/pages/not-found-page';
import {PATHS} from './paths';

export const router = createBrowserRouter([
    {
        path: PATHS.dashboard,
        element: <AppLayout />,
        children: [
            {index: true, element: <DashboardPage />},
            {path: PATHS.mas.list, element: <MASPage />},
            {path: PATHS.mas.detailPattern, element: <MASDetailPage />},
            {path: PATHS.authRequests.list, element: <AuthRequestsPage />},
            {path: PATHS.authRequests.detailPattern, element: <AuthRequestDetailPage />},
            {path: '*', element: <NotFoundPage />}
        ]
    }
]);
