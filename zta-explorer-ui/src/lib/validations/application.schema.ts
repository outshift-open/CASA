import {z} from 'zod';

export const applicationSchema = z.object({
    name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
    type: z.enum(['agent', 'client', 'mcp_server']),
    base_url: z.string().url('Must be a valid URL'),
    tools: z.string().optional()
});

export type ApplicationFormData = z.infer<typeof applicationSchema>;
