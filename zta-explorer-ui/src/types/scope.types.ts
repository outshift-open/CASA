import type {MAS} from './mas.types';

export interface Scope {
    id: string;
    name: string;
    mas_id: string;
    mas?: MAS;
}

export interface ScopeCreateRequest {
    name: string;
    mas_id: string;
}

export interface ScopeUpdateRequest {
    name: string;
}
