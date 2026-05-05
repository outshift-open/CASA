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

import type {AppType} from './app.types';

export interface AppSummary {
    id: string;
    type: AppType;
    name: string;
}

export interface MASTraceStat {
    mas_id: string;
    traces: number;
    allowed: number;
    denied: number;
}

export interface MAS {
    id: string;
    name: string;
    apps: AppSummary[];
    created_at: string;
    enabled_tool_checks?: number;
    namespace?: string;
    k8s_name?: string;
    authorization_server_id?: string;
    traces?: MASTraceStat;
}

export interface MASListResponse {
    items: MAS[];
    total: number;
    page: number;
    page_size: number;
}
