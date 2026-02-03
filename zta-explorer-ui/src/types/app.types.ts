export type AppType = 'agent' | 'client' | 'mcp_server';

export interface App {
    id?: string;
    type: AppType;
    name: string;
    base_url: string;
    tools: string[];
}

export interface AppListResponse {
    items: App[];
    total: number;
}

export interface CreateAppRequest {
    type: AppType;
    name: string;
    base_url: string;
    tools: string[];
}

export interface UpdateAppRequest {
    type: AppType;
    name: string;
    base_url: string;
    tools: string[];
}
