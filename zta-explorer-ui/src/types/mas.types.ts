import type {App} from './app.types';

export interface MAS {
    id: string;
    name: string;
    apps: App[];
    created_at: string;
}

export interface MASListResponse {
    items: MAS[];
    total: number;
}

export interface CreateMASRequest {
    name: string;
}

export interface UpdateMASRequest {
    name: string;
}

export interface BindAppsRequest {
    app_ids: string[];
}
