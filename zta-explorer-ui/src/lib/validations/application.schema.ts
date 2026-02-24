import {z} from 'zod';

// Schema for creating new applications (requires MAS selection)
export const applicationCreateSchema = z.object({
    name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
    type: z.enum(['agent', 'client', 'mcp_server']),
    base_url: z.string().url('Must be a valid URL'),
    mas_id: z.string().min(1, 'MAS is required'),
    tools: z.string().optional()
});

// Schema for editing applications (MAS and Type cannot be changed after creation)
export const applicationEditSchema = z.object({
    name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
    base_url: z.string().url('Must be a valid URL'),
    tools: z.string().optional()
});

export type ApplicationCreateFormData = z.infer<typeof applicationCreateSchema>;
export type ApplicationEditFormData = z.infer<typeof applicationEditSchema>;

// Backward compatibility
export const applicationSchema = applicationCreateSchema;
export type ApplicationFormData = ApplicationCreateFormData;
