import {z} from 'zod';

export const scopeCreateSchema = z.object({
    name: z
        .string()
        .min(1, 'Scope name is required')
        .min(2, 'Scope name must be at least 2 characters')
        .max(100, 'Scope name must be less than 100 characters')
        .regex(/^[a-zA-Z0-9_-]+$/, 'Scope name can only contain letters, numbers, hyphens, and underscores'),
    mas_id: z.string().uuid('Invalid MAS ID')
});

export const scopeUpdateSchema = z.object({
    name: z
        .string()
        .min(1, 'Scope name is required')
        .min(2, 'Scope name must be at least 2 characters')
        .max(100, 'Scope name must be less than 100 characters')
        .regex(/^[a-zA-Z0-9_-]+$/, 'Scope name can only contain letters, numbers, hyphens, and underscores')
});

export type ScopeCreateFormData = z.infer<typeof scopeCreateSchema>;
export type ScopeUpdateFormData = z.infer<typeof scopeUpdateSchema>;
