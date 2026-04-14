import {useState} from 'react';
import {useMASScopes} from '@/hooks/use-scopes';
import {Card, CardContent} from '@/components/ui/card';
import {Input} from '@/components/ui/input';
import {Skeleton} from '@/components/ui/skeleton';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {Tags, Search, List, LayoutGrid} from 'lucide-react';
import {useNavigate} from 'react-router-dom';
import type {MAS} from '@/types/mas.types';

interface MASScopesTabProps {
    mas: MAS;
}

export function MASScopesTab({mas}: MASScopesTabProps) {
    const navigate = useNavigate();
    const {data: scopes, isLoading: scopesLoading, error: scopesError} = useMASScopes(mas.id);
    const [search, setSearch] = useState('');
    const [view, setView] = useState<'table' | 'grid'>('table');

    const filteredScopes = search
        ? (scopes ?? []).filter(
              (s) =>
                  s.name.toLowerCase().includes(search.toLowerCase()) ||
                  s.id.toLowerCase().includes(search.toLowerCase())
          )
        : (scopes ?? []);

    const hasData = scopes && scopes.length > 0;

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-lg font-semibold">Scopes</p>
                    <p className="text-sm text-muted-foreground">
                        {scopes?.length || 0} scope{scopes?.length !== 1 ? 's' : ''} configured
                    </p>
                </div>
            </div>

            {hasData && (
                <div className="flex items-center justify-between gap-2">
                    <div className="relative w-1/2">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Search scopes..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-9"
                        />
                    </div>
                    <ToggleGroup
                        type="single"
                        value={view}
                        onValueChange={(v) => v && setView(v as 'table' | 'grid')}
                        variant="outline"
                    >
                        <ToggleGroupItem value="table" aria-label="Table view">
                            <List className="h-4 w-4" />
                        </ToggleGroupItem>
                        <ToggleGroupItem value="grid" aria-label="Grid view">
                            <LayoutGrid className="h-4 w-4" />
                        </ToggleGroupItem>
                    </ToggleGroup>
                </div>
            )}

            {scopesLoading ? (
                <div className="space-y-3">
                    {Array.from({length: 3}).map((_, i) => (
                        <Skeleton key={i} className="w-full h-10" />
                    ))}
                </div>
            ) : scopesError ? (
                <Card>
                    <CardContent className="pt-6">
                        <p className="text-sm text-destructive text-center py-8">Error loading scopes</p>
                    </CardContent>
                </Card>
            ) : hasData ? (
                view === 'grid' ? (
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {filteredScopes.map((scope) => (
                            <Card
                                key={scope.id}
                                className="cursor-pointer hover:bg-accent/50 transition-colors p-0"
                                onClick={() => navigate(`/scopes/${scope.id}`)}
                            >
                                <div className="flex items-center gap-3 p-3">
                                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10">
                                        <Tags className="h-4 w-4 text-primary" />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <p className="text-sm font-semibold truncate">{scope.name}</p>
                                        <p className="text-xs text-muted-foreground font-mono truncate">{scope.id}</p>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                ) : (
                    <Card className="py-0">
                        <CardContent className="p-0">
                            <div className="divide-y">
                                {filteredScopes.map((scope) => (
                                    <div
                                        key={scope.id}
                                        className="flex items-center gap-3 px-4 py-4 hover:bg-muted/50 transition-colors cursor-pointer"
                                        onClick={() => navigate(`/scopes/${scope.id}`)}
                                    >
                                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 flex-shrink-0">
                                            <Tags className="h-5 w-5 text-primary" />
                                        </div>
                                        <div>
                                            <p className="font-semibold">{scope.name}</p>
                                            <p className="text-xs text-muted-foreground font-mono">{scope.id}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )
            ) : (
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                            <Tags className="h-10 w-10 opacity-40" />
                            <div className="text-center">
                                <p className="text-sm font-medium">No scopes</p>
                                <p className="text-xs mt-1">This MAS doesn't have any scopes configured</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
