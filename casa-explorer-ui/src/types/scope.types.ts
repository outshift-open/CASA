import type {MAS} from './mas.types';
import type {Tool} from './app.types';

export interface Scope {
    id: string;
    name: string;
    mas_id: string;
    mas?: MAS;
    tools?: Tool[];
}
