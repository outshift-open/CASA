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
