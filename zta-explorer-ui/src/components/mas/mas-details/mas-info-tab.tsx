import {useMASApps, useUpdateMAS} from '@/hooks/use-mas';
import {useMASScopes} from '@/hooks/use-scopes';
import {Button} from '@/components/ui/button';
import {Switch} from '@/components/ui/switch';
import {Bot, AppWindow, Server, Tags, Copy, Download, Wrench, ShieldCheck, ShieldOff} from 'lucide-react';
import {toast} from 'sonner';
import {useMemo} from 'react';
import type {MAS} from '@/types/mas.types';
import type {AppType} from '@/types/app.types';

// ToolCheckFlags bitmask values (must match backend IntFlag)
const FLAG_DETERMINISTIC_TOOL_SELECTED = 1 << 0;
const FLAG_DETERMINISTIC_LLM_SELECTED_TOOLS = 1 << 1;
const FLAG_AI_POWERED_TOOL_MATCH = 1 << 2;

const TOOL_CHECKS = [
    {
        flag: FLAG_DETERMINISTIC_TOOL_SELECTED,
        label: 'Deny if tool not selected by LLM',
        description: 'Tool not in LLM-selected tools list'
    },
    {
        flag: FLAG_DETERMINISTIC_LLM_SELECTED_TOOLS,
        label: 'Deny if no LLM calls made',
        description: 'App never made an LLM call'
    },
    {
        flag: FLAG_AI_POWERED_TOOL_MATCH,
        label: 'Deny if intent mismatch',
        description: 'Tool does not match user intent'
    }
];

const APP_TYPE_ICONS: Record<AppType, React.ComponentType<{className?: string}>> = {
    agent: Bot,
    client: AppWindow,
    mcp_server: Server
};

const APP_TYPE_COLORS: Record<AppType, string> = {
    agent: 'text-blue-500',
    client: 'text-green-500',
    mcp_server: 'text-purple-500'
};

const APP_TYPE_LABELS: Record<AppType, string> = {
    agent: 'Agents',
    client: 'Clients',
    mcp_server: 'MCP Servers'
};

function formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)}mo ago`;
    return `${Math.floor(diffInSeconds / 31536000)}y ago`;
}

interface MASInfoTabProps {
    mas: MAS;
}

export function MASInfoTab({mas}: MASInfoTabProps) {
    const {data: apps} = useMASApps(mas.id);
    const {data: scopes} = useMASScopes(mas.id);
    const {mutate: updateMAS, isPending} = useUpdateMAS(mas.id);

    const stats = useMemo(() => {
        if (!apps) return {byType: {agent: 0, client: 0, mcp_server: 0}, totalTools: 0};
        const byType = apps.reduce(
            (acc, app) => {
                acc[app.type] = (acc[app.type] || 0) + 1;
                return acc;
            },
            {agent: 0, client: 0, mcp_server: 0} as Record<AppType, number>
        );
        const totalTools = apps.reduce((sum, app) => sum + (app.tools?.length || 0), 0);
        return {byType, totalTools};
    }, [apps]);

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`${label} copied to clipboard`);
    };

    const exportConfig = () => {
        const config = {
            mas: {id: mas.id, name: mas.name, created_at: mas.created_at},
            apps: apps?.map((app) => ({
                id: app.id,
                name: app.name,
                type: app.type,
                base_url: app.base_url,
                tools: app.tools
            }))
        };
        const blob = new Blob([JSON.stringify(config, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${mas.name}-config.json`;
        link.click();
        URL.revokeObjectURL(url);
        toast.success('Configuration exported');
    };

    const checks = mas.enabled_tool_checks ?? 0;

    const toggleCheck = (flag: number, enabled: boolean) => {
        const newChecks = enabled ? checks | flag : checks & ~flag;
        updateMAS(
            {name: mas.name, enabled_tool_checks: newChecks},
            {
                onSuccess: () => toast.success('Authorization checks updated'),
                onError: () => toast.error('Failed to update authorization checks')
            }
        );
    };

    return (
        <div className="space-y-6">
            {/* Metadata row */}
            <div className="flex items-start justify-between gap-4">
                <div className="grid gap-4 sm:grid-cols-2 flex-1">
                    {/* ID */}
                    <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">MAS ID</p>
                        <div className="flex items-center gap-2">
                            <code className="text-xs font-mono bg-muted px-2 py-1 rounded truncate max-w-[220px]">
                                {mas.id}
                            </code>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6 cursor-pointer flex-shrink-0"
                                onClick={() => copyToClipboard(mas.id, 'MAS ID')}
                            >
                                <Copy className="h-3 w-3" />
                            </Button>
                        </div>
                    </div>

                    {/* Created */}
                    <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Created</p>
                        <div>
                            <p className="text-sm font-medium">{formatDate(mas.created_at)}</p>
                            <p className="text-xs text-muted-foreground">{new Date(mas.created_at).toLocaleString()}</p>
                        </div>
                    </div>

                    {/* Namespace */}
                    {mas.namespace && (
                        <div className="space-y-1">
                            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                Namespace
                            </p>
                            <code className="text-xs font-mono bg-muted px-2 py-1 rounded">{mas.namespace}</code>
                        </div>
                    )}
                </div>

                <Button variant="outline" size="sm" onClick={exportConfig} className="cursor-pointer flex-shrink-0">
                    <Download className="mr-2 h-3 w-3" />
                    Export
                </Button>
            </div>

            <div className="border-t" />

            {/* Stats row */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {(Object.entries(stats.byType) as [AppType, number][]).map(([type, count]) => {
                    const Icon = APP_TYPE_ICONS[type];
                    const colorClass = APP_TYPE_COLORS[type];
                    return (
                        <div key={type} className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
                            <div className="flex items-center justify-between">
                                <p className="text-xs text-muted-foreground">{APP_TYPE_LABELS[type]}</p>
                                <Icon className={`h-4 w-4 ${colorClass}`} />
                            </div>
                            <p className="text-2xl font-bold">{count}</p>
                        </div>
                    );
                })}

                <div className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
                    <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">Tools</p>
                        <Wrench className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <p className="text-2xl font-bold">{stats.totalTools}</p>
                </div>

                <div className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
                    <div className="flex items-center justify-between">
                        <p className="text-xs text-muted-foreground">Scopes</p>
                        <Tags className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <p className="text-2xl font-bold">{scopes?.length ?? 0}</p>
                </div>
            </div>

            <div className="border-t" />

            {/* Authorization checks */}
            <div className="space-y-3">
                <div className="flex items-center justify-between">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Deny Conditions</p>
                    {(() => {
                        const allFlags = TOOL_CHECKS.reduce((acc, {flag}) => acc | flag, 0);
                        const allEnabled = (checks & allFlags) === allFlags;
                        return (
                            <button
                                type="button"
                                disabled={isPending}
                                className="text-xs text-muted-foreground hover:text-foreground transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                                onClick={() =>
                                    updateMAS(
                                        {name: mas.name, enabled_tool_checks: allEnabled ? 0 : allFlags},
                                        {
                                            onSuccess: () =>
                                                toast.success(`All checks ${allEnabled ? 'disabled' : 'enabled'}`),
                                            onError: () => toast.error('Failed to update authorization checks')
                                        }
                                    )
                                }
                            >
                                {allEnabled ? 'Disable all' : 'Enable all'}
                            </button>
                        );
                    })()}
                </div>
                <div className="grid gap-2 sm:grid-cols-3">
                    {TOOL_CHECKS.map(({flag, label, description}) => {
                        const enabled = (checks & flag) !== 0;
                        return (
                            <div
                                key={flag}
                                className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${enabled ? 'bg-card' : 'bg-muted/30'}`}
                            >
                                {enabled ? (
                                    <ShieldCheck className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                ) : (
                                    <ShieldOff className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                                )}
                                <div className="flex-1 space-y-0.5 min-w-0">
                                    <p
                                        className={`text-sm font-medium leading-none ${!enabled ? 'text-muted-foreground' : ''}`}
                                    >
                                        {label}
                                    </p>
                                    <p className="text-xs text-muted-foreground">{description}</p>
                                </div>
                                <Switch
                                    checked={enabled}
                                    onCheckedChange={(val) => toggleCheck(flag, val)}
                                    disabled={isPending}
                                    className="flex-shrink-0 cursor-pointer"
                                />
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
