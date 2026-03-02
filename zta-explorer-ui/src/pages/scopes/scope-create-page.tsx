import {useNavigate, useSearchParams} from 'react-router-dom';
import {useCreateScope} from '@/hooks/use-scopes';
import {useMAS} from '@/hooks/use-mas';
import {useForm, Controller} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover';
import {Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList} from '@/components/ui/command';
import {Alert, AlertDescription, AlertTitle} from '@/components/ui/alert';
import {Badge} from '@/components/ui/badge';
import {toast} from 'sonner';
import {scopeCreateSchema, type ScopeCreateFormData} from '@/lib/validations/scope.schema';
import {AlertCircle, Plus, Check, ChevronsUpDown, Network} from 'lucide-react';
import {cn} from '@/lib/utils';
import {useState, useEffect} from 'react';

export function ScopeCreatePage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const prefilledMasId = searchParams.get('mas_id');
    const createScope = useCreateScope();
    const {data: masData, isLoading: masLoading, error: masError, refetch: refetchMAS} = useMAS();
    const [masComboboxOpen, setMasComboboxOpen] = useState(false);

    const {
        register,
        handleSubmit,
        control,
        setValue,
        formState: {errors}
    } = useForm<ScopeCreateFormData>({
        resolver: zodResolver(scopeCreateSchema),
        defaultValues: {
            name: '',
            mas_id: prefilledMasId || ''
        }
    });

    // Update mas_id when masData loads and we have a prefilled value
    useEffect(() => {
        if (prefilledMasId && masData) {
            const masExists = masData.some((mas) => mas.id === prefilledMasId);
            if (masExists) {
                setValue('mas_id', prefilledMasId);
            }
        }
    }, [prefilledMasId, masData, setValue]);

    const onSubmit = async (data: ScopeCreateFormData) => {
        try {
            const newScope = await createScope.mutateAsync(data);
            toast.success('Scope created successfully');
            navigate(`/scopes/${newScope.id}`);
        } catch (error) {
            console.error('Failed to create scope:', error);
            toast.error('Failed to create scope');
        }
    };

    const hasMAS = masData && masData.length > 0;
    const prefilledMAS = prefilledMasId && masData ? masData.find((mas) => mas.id === prefilledMasId) : null;

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold">Create Scope</h1>
                <p className="text-muted-foreground">Add a new authorization scope to a Multi-Agent System</p>
                {prefilledMAS && (
                    <div className="mt-2 flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                            <Network className="mr-1 h-3 w-3" />
                            For MAS: {prefilledMAS.name}
                        </Badge>
                    </div>
                )}
            </div>

            {masLoading && (
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-center py-8">
                            <div className="flex flex-col items-center gap-2">
                                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                                <p className="text-sm text-muted-foreground">Loading Multi-Agent Systems...</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {!masLoading && masError && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error Loading MAS</AlertTitle>
                    <AlertDescription className="mt-2 flex flex-col gap-3">
                        <p>Failed to load Multi-Agent Systems. Please try again.</p>
                        <div>
                            <Button onClick={() => refetchMAS()} size="sm" variant="outline">
                                Retry
                            </Button>
                        </div>
                    </AlertDescription>
                </Alert>
            )}

            {!masLoading && !masError && !hasMAS && (
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex flex-col items-center justify-center py-12 text-center">
                            <div className="rounded-full bg-destructive/10 p-3 mb-4">
                                <AlertCircle className="h-8 w-8 text-destructive" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No Multi-Agent Systems Found</h3>
                            <p className="text-muted-foreground mb-6 max-w-md">
                                You need to create at least one Multi-Agent System (MAS) before you can create a scope.
                                Scopes must be associated with a MAS.
                            </p>
                            <Button onClick={() => navigate('/mas/create')}>
                                <Plus className="mr-2 h-4 w-4" />
                                Create Your First MAS
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {!masLoading && !masError && hasMAS && (
                <Card>
                    <CardHeader>
                        <CardTitle>Scope Details</CardTitle>
                        <CardDescription>
                            Fill in the details to create a new scope. The scope will be automatically synchronized with
                            Keycloak.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                            <div className="grid gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="name" className="text-sm font-medium">
                                        Scope Name <span className="text-destructive">*</span>
                                    </Label>
                                    <Input
                                        id="name"
                                        placeholder="e.g., call-tools, read-data"
                                        {...register('name')}
                                        disabled={createScope.isPending}
                                        autoFocus
                                    />
                                    {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
                                    <p className="text-xs text-muted-foreground">
                                        Use letters, numbers, hyphens, and underscores only
                                    </p>
                                </div>

                                <div className="grid gap-2">
                                    <Label htmlFor="mas_id" className="text-sm font-medium">
                                        Multi-Agent System <span className="text-destructive">*</span>
                                    </Label>
                                    <Controller
                                        name="mas_id"
                                        control={control}
                                        render={({field}) => (
                                            <Popover open={masComboboxOpen} onOpenChange={setMasComboboxOpen}>
                                                <PopoverTrigger asChild>
                                                    <Button
                                                        variant="outline"
                                                        role="combobox"
                                                        aria-expanded={masComboboxOpen}
                                                        className="w-full justify-between"
                                                        disabled={createScope.isPending || masLoading}
                                                    >
                                                        {field.value
                                                            ? masData?.find((mas) => mas.id === field.value)?.name
                                                            : masLoading
                                                              ? 'Loading...'
                                                              : 'Select MAS...'}
                                                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                                    </Button>
                                                </PopoverTrigger>
                                                <PopoverContent
                                                    className="p-0"
                                                    align="start"
                                                    style={{width: 'var(--radix-popover-trigger-width)'}}
                                                >
                                                    <Command className="w-full">
                                                        <CommandInput placeholder="Search MAS..." />
                                                        <CommandList>
                                                            <CommandEmpty>No MAS found.</CommandEmpty>
                                                            <CommandGroup>
                                                                {masData?.map((mas) => (
                                                                    <CommandItem
                                                                        key={mas.id}
                                                                        value={mas.name}
                                                                        onSelect={() => {
                                                                            field.onChange(mas.id);
                                                                            setMasComboboxOpen(false);
                                                                        }}
                                                                    >
                                                                        <Check
                                                                            className={cn(
                                                                                'mr-2 h-4 w-4',
                                                                                field.value === mas.id
                                                                                    ? 'opacity-100'
                                                                                    : 'opacity-0'
                                                                            )}
                                                                        />
                                                                        {mas.name}
                                                                    </CommandItem>
                                                                ))}
                                                            </CommandGroup>
                                                        </CommandList>
                                                    </Command>
                                                </PopoverContent>
                                            </Popover>
                                        )}
                                    />
                                    {errors.mas_id && (
                                        <p className="text-sm text-destructive">{errors.mas_id.message}</p>
                                    )}
                                </div>
                            </div>

                            <div className="flex justify-end gap-2">
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => navigate('/scopes')}
                                    disabled={createScope.isPending}
                                >
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={createScope.isPending}>
                                    {createScope.isPending ? 'Creating...' : 'Create Scope'}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
