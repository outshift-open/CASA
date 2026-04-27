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

export type AppType = 'agent' | 'client' | 'mcp_server';

export interface MAS {
    id: string;
    name: string;
    created_at: string;
}

export interface ScopeMinimal {
    id: string;
    name: string;
}

export interface Tool {
    id?: string;
    name: string;
    description: string;
    input_schema: string;
    output_schema: string;
    app_id?: string;
    scopes?: ScopeMinimal[];
}

export interface App {
    id?: string;
    type: AppType;
    name: string;
    base_url: string;
    tools: Tool[];
    mas_id?: string;
    mas?: MAS;
    created_at?: string;
}

export interface AppListResponse {
    items: App[];
    total: number;
}
