import {useNavigate} from 'react-router-dom';
import {useCreateMAS} from '@/hooks/use-mas';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {toast} from 'sonner';
import {masSchema, type MASFormData} from '@/lib/validations/mas.schema';

export function MASCreatePage() {
    const navigate = useNavigate();
    const createMAS = useCreateMAS();

    const {
        register,
        handleSubmit,
        formState: {errors}
    } = useForm<MASFormData>({
        resolver: zodResolver(masSchema),
        defaultValues: {
            name: ''
        }
    });

    const onSubmit = async (data: MASFormData) => {
        try {
            const newMAS = await createMAS.mutateAsync({
                name: data.name
            });
            toast.success('MAS created successfully');
            navigate(`/mas/${newMAS.id}`);
        } catch (error) {
            console.error('Failed to create MAS:', error);
            toast.error('Failed to create MAS');
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold">Create Multi-Agent System</h1>
                <p className="text-muted-foreground">
                    Create a new MAS. You can add applications to it when creating or editing apps.
                </p>
            </div>
            <Card>
                <CardHeader>
                    <CardTitle>MAS Details</CardTitle>
                    <CardDescription>Provide a name for your Multi-Agent System</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        <div className="grid gap-4">
                            <div className="grid gap-2">
                                <Label htmlFor="name" className="text-sm font-medium">
                                    Name <span className="text-destructive">*</span>
                                </Label>
                                <Input
                                    id="name"
                                    placeholder="Enter MAS name"
                                    {...register('name')}
                                    disabled={createMAS.isPending}
                                    autoFocus
                                />
                                {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
                            </div>
                        </div>

                        <div className="flex justify-end gap-2">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => navigate('/mas')}
                                disabled={createMAS.isPending}
                            >
                                Cancel
                            </Button>
                            <Button type="submit" disabled={createMAS.isPending}>
                                {createMAS.isPending ? 'Creating...' : 'Create MAS'}
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
