export type AppType = 'agent' | 'client' | 'mcp_server';

export interface MAS {
    id: string;
    name: string;
    created_at: string;
}

export interface Tool {
    id?: string;
    name: string;
    description: string;
    input_schema: string;
    output_schema: string;
    app_id?: string;
    scopes?: string[];
}

export interface ToolRequest {
    name: string;
    description: string;
    input_schema: string;
    output_schema: string;
    scopes?: string[];
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

export interface CreateAppRequest {
    type: AppType;
    name: string;
    base_url: string;
    mas_id: string;
    tools: ToolRequest[];
}

// Note: Backend does not support updating mas_id or type after creation
// as apps are tied to MAS authorization server and client credentials
export interface UpdateAppRequest {
    name: string;
    base_url: string;
    tools: ToolRequest[];
}
