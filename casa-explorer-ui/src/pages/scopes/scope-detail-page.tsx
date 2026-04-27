/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {useParams, useNavigate} from 'react-router-dom';
import {useScopeById} from '@/hooks/use-scopes';
import {useMASById} from '@/hooks/use-mas';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Skeleton} from '@/components/ui/skeleton';
import {Tabs, TabsList, TabsTrigger} from '@/components/ui/tabs';
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle} from '@/components/ui/dialog';
import {ApiStateHandler} from '@/components/api-state-handler';
import {Network, Copy, Wrench, ExternalLink, Info, Search} from 'lucide-react';
import {toast} from 'sonner';
import {useState, useMemo} from 'react';
import type {Tool} from '@/types/app.types';

export function ScopeDetailPage() {
    const {id} = useParams<{id: string}>();
    const navigate = useNavigate();
    const {data: scope, isLoading, error, refetch} = useScopeById(id || '');
    const {data: mas} = useMASById(scope?.mas_id || '');
    const [activeTab, setActiveTab] = useState('info');
    const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
    const [toolSearch, setToolSearch] = useState('');

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`${label} copied to clipboard`);
    };

    // Get tools directly from the scope (backend now includes this relationship)
    const toolsUsingScope = useMemo(() => {
        return scope?.tools || [];
    }, [scope]);

    const hasTools = toolsUsingScope.length > 0;

    return (
        <>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Scope Details</h1>
                        <p className="text-muted-foreground">View and manage scope information</p>
                    </div>
                </div>

                <ApiStateHandler
                    isLoading={isLoading}
                    isError={!!error || !scope}
                    error={error as Error}
                    loadingMessage="Loading scope..."
                    errorMessage="Failed to load scope. Please try again."
                    onRetry={() => refetch()}
                >
                    {scope && (
                        <div className="grid gap-6">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                                    <div className="space-y-2">
                                        <CardTitle>{scope.name}</CardTitle>
                                        <CardDescription>Scope information and tools</CardDescription>
                                    </div>
                                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-auto">
                                        <TabsList>
                                            <TabsTrigger value="info">
                                                <Info className="mr-2 h-4 w-4" />
                                                Info
                                            </TabsTrigger>
                                            <TabsTrigger value="tools">
                                                <Wrench className="mr-2 h-4 w-4" />
                                                Tools
                                            </TabsTrigger>
                                        </TabsList>
                                    </Tabs>
                                </CardHeader>
                                <CardContent>
                                    {activeTab === 'info' && (
                                        <Card>
                                            <CardHeader>
                                                <div className="flex items-start justify-between">
                                                    <div className="space-y-1">
                                                        <CardTitle>Basic Information</CardTitle>
                                                        <CardDescription>Core details about this scope</CardDescription>
                                                    </div>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="grid gap-6 md:grid-cols-2">
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Name
                                                            </p>
                                                            <p className="text-base font-semibold">{scope.name}</p>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <div className="flex items-center justify-between">
                                                                <p className="text-sm font-medium text-muted-foreground">
                                                                    Scope ID
                                                                </p>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="sm"
                                                                    onClick={() =>
                                                                        copyToClipboard(scope.id, 'Scope ID')
                                                                    }
                                                                    className="cursor-pointer h-6 px-2"
                                                                >
                                                                    <Copy className="h-3 w-3" />
                                                                </Button>
                                                            </div>
                                                            <p className="text-xs font-mono bg-muted px-2 py-1 rounded">
                                                                {scope.id}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <p className="text-sm font-medium text-muted-foreground">
                                                                Multi-Agent System
                                                            </p>
                                                            {scope.mas || mas ? (
                                                                <div
                                                                    className="flex items-center gap-2 cursor-pointer text-base group"
                                                                    onClick={() => navigate(`/mas/${scope.mas_id}`)}
                                                                >
                                                                    <Network className="h-4 w-4 text-muted-foreground" />
                                                                    <div className="flex flex-col">
                                                                        <span className="font-semibold underline decoration-dotted group-hover:decoration-solid">
                                                                            {scope.mas?.name ||
                                                                                mas?.name ||
                                                                                'Unknown MAS'}
                                                                        </span>
                                                                        <span className="font-mono text-xs text-muted-foreground">
                                                                            {scope.mas?.id || mas?.id || scope.mas_id}
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <Skeleton className="h-5 w-32" />
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    )}

                                    {activeTab === 'tools' && (
                                        <div className="space-y-3">
                                            {!hasTools ? (
                                                <div className="flex flex-col items-center justify-center py-8 gap-3">
                                                    <Wrench className="h-10 w-10 text-muted-foreground opacity-40" />
                                                    <p className="text-sm font-medium text-muted-foreground">
                                                        No tools are using this scope
                                                    </p>
                                                </div>
                                            ) : (
                                                <>
                                                    <div className="relative w-1/2">
                                                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                                        <Input
                                                            placeholder="Search tools..."
                                                            value={toolSearch}
                                                            onChange={(e) => setToolSearch(e.target.value)}
                                                            className="pl-9"
                                                        />
                                                    </div>
                                                    <div className="space-y-3">
                                                        {toolsUsingScope
                                                            .filter(
                                                                (t) =>
                                                                    !toolSearch ||
                                                                    t.name
                                                                        .toLowerCase()
                                                                        .includes(toolSearch.toLowerCase()) ||
                                                                    (t.description ?? '')
                                                                        .toLowerCase()
                                                                        .includes(toolSearch.toLowerCase())
                                                            )
                                                            .map((tool) => (
                                                                <div
                                                                    key={tool.id}
                                                                    className="group p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer"
                                                                    onClick={() => setSelectedTool(tool)}
                                                                >
                                                                    <div className="flex items-start justify-between gap-4">
                                                                        <div className="flex items-start gap-3 flex-1 min-w-0">
                                                                            <div className="mt-0.5 p-2 rounded-md bg-primary/10">
                                                                                <Wrench className="h-4 w-4 text-primary" />
                                                                            </div>
                                                                            <div className="flex-1 min-w-0">
                                                                                <p className="font-semibold text-foreground">
                                                                                    {tool.name}
                                                                                </p>
                                                                                <p className="text-sm text-muted-foreground mt-1">
                                                                                    {tool.description}
                                                                                </p>
                                                                                <p className="text-xs text-muted-foreground mt-2">
                                                                                    Click to view schemas
                                                                                </p>
                                                                            </div>
                                                                        </div>
                                                                        {tool.app_id && (
                                                                            <Button
                                                                                variant="ghost"
                                                                                size="sm"
                                                                                onClick={(e) => {
                                                                                    e.stopPropagation();
                                                                                    navigate(`/apps/${tool.app_id}`);
                                                                                }}
                                                                                className="cursor-pointer h-8 w-8 p-0 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                                                                                title="View app"
                                                                            >
                                                                                <ExternalLink className="h-4 w-4" />
                                                                            </Button>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            ))}
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </ApiStateHandler>
            </div>

            <Dialog open={!!selectedTool} onOpenChange={(open) => !open && setSelectedTool(null)}>
                <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <Wrench className="h-5 w-5" />
                            {selectedTool?.name}
                        </DialogTitle>
                        <DialogDescription>{selectedTool?.description}</DialogDescription>
                    </DialogHeader>

                    <div className="space-y-6 mt-4">
                        {/* Input Schema */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold text-foreground">Input Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        if (selectedTool?.input_schema) {
                                            navigator.clipboard.writeText(selectedTool.input_schema);
                                            toast.success('Input schema copied to clipboard');
                                        }
                                    }}
                                    className="cursor-pointer h-8 px-2"
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>
                                    {selectedTool?.input_schema
                                        ? JSON.stringify(JSON.parse(selectedTool.input_schema), null, 2)
                                        : '{}'}
                                </code>
                            </pre>
                        </div>

                        {/* Output Schema */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold text-foreground">Output Schema</h3>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        if (selectedTool?.output_schema) {
                                            navigator.clipboard.writeText(selectedTool.output_schema);
                                            toast.success('Output schema copied to clipboard');
                                        }
                                    }}
                                    className="cursor-pointer h-8 px-2"
                                >
                                    <Copy className="h-3 w-3" />
                                </Button>
                            </div>
                            <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                                <code>
                                    {selectedTool?.output_schema
                                        ? JSON.stringify(JSON.parse(selectedTool.output_schema), null, 2)
                                        : '{}'}
                                </code>
                            </pre>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
}
