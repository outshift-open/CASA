/**
 * Copyright 2026 Copyright 2026 Cisco Systems, Inc. and its affiliates
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

import {Button} from '@/components/ui/button';
import {Copy, Download, Tags, AppWindow, Activity, ShieldAlert} from 'lucide-react';
import {toast} from 'sonner';
import type {MAS} from '@/types/mas.types';
import {DateHover} from '@/components/ui/date-hover';

const FLAG_DETERMINISTIC_TOOL_SELECTED = 1 << 0;
const FLAG_DETERMINISTIC_LLM_SELECTED_TOOLS = 1 << 1;
const FLAG_AI_POWERED_TOOL_MATCH = 1 << 2;
const TOTAL_CHECKS = 3;

interface MASInfoTabProps {
    mas: MAS;
    traceTotal: number;
    onTabChange: (tab: string) => void;
}

export function MASInfoTab({mas, traceTotal, onTabChange}: MASInfoTabProps) {
    const apps = mas.apps ?? [];

    const enabledChecks = mas.enabled_tool_checks ?? 0;
    const enabledCount = [
        FLAG_DETERMINISTIC_TOOL_SELECTED,
        FLAG_DETERMINISTIC_LLM_SELECTED_TOOLS,
        FLAG_AI_POWERED_TOOL_MATCH
    ].filter((f) => (enabledChecks & f) !== 0).length;

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`${label} copied to clipboard`);
    };

    const exportConfig = () => {
        const config = {
            mas: {id: mas.id, name: mas.name, created_at: mas.created_at},
            apps: apps.map((app) => ({
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

    return (
        <div className="space-y-6">
            {/* Metadata row */}
            <div className="flex items-start justify-between gap-4">
                <div className="grid gap-4 sm:grid-cols-2 flex-1">
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

                    <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Created</p>
                        <div>
                            <DateHover date={mas.created_at} className="text-sm font-medium" />
                            <p className="text-xs text-muted-foreground">
                                {new Date(mas.created_at).toLocaleString([], {hour12: false})}
                            </p>
                        </div>
                    </div>

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

            {/* Summary cards */}
            <div className="grid gap-4 sm:grid-cols-2">
                {/* Auth scopes */}
                <div className="rounded-lg border bg-muted/30 p-5 space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                            <Tags className="h-4 w-4" />
                            Auth Scopes
                        </div>
                        <span className="text-[10px] font-medium uppercase tracking-wide px-2 py-0.5 rounded-full border border-muted-foreground/30 text-muted-foreground">
                            Coming soon
                        </span>
                    </div>
                    <p className="text-xs text-muted-foreground">Auth scopes grant access to specific MCP tools.</p>
                </div>

                {/* Deny conditions */}
                <div className="rounded-lg border bg-card p-5 space-y-3">
                    <div className="flex items-center gap-2 text-sm font-medium">
                        <ShieldAlert className="h-4 w-4 text-muted-foreground" />
                        Deny Conditions
                    </div>
                    <div>
                        <p className="text-3xl font-bold">
                            {enabledCount}
                            <span className="text-xl font-normal text-muted-foreground"> / {TOTAL_CHECKS}</span>
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                            Guardrails evaluated before MCP tool execution.
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={() => onTabChange('deny_conditions')}
                        className="text-sm text-primary hover:underline cursor-pointer"
                    >
                        Configure Deny Conditions
                    </button>
                </div>

                {/* Agentic services */}
                <div className="rounded-lg border bg-card p-5 space-y-3">
                    <div className="flex items-center gap-2 text-sm font-medium">
                        <AppWindow className="h-4 w-4 text-muted-foreground" />
                        Agentic Services
                    </div>
                    <div>
                        <p className="text-3xl font-bold">{apps.length}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                            Registered agents, clients, and MCP servers for this MAS.
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={() => onTabChange('apps')}
                        className="text-sm text-primary hover:underline cursor-pointer"
                    >
                        View Agentic Services
                    </button>
                </div>

                {/* Trace activity */}
                <div className="rounded-lg border bg-card p-5 space-y-3">
                    <div className="flex items-center gap-2 text-sm font-medium">
                        <Activity className="h-4 w-4 text-muted-foreground" />
                        Trace Activity
                    </div>
                    <div>
                        <p className="text-3xl font-bold">{traceTotal}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                            Trace sessions with authorization and MCP events for this MAS.
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={() => onTabChange('traces')}
                        className="text-sm text-primary hover:underline cursor-pointer"
                    >
                        View Traces
                    </button>
                </div>
            </div>
        </div>
    );
}
