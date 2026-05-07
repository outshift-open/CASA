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

import {useUpdateMAS} from '@/hooks/use-mas';
import {Switch} from '@/components/ui/switch';

import {ShieldCheck, ShieldOff} from 'lucide-react';
import {toast} from 'sonner';
import {ToolCheckFlags} from '@/types/mas.types';
import type {MAS} from '@/types/mas.types';

const TOOL_CHECKS = [
    {
        flag: ToolCheckFlags.DeterministicToolSelected,
        label: 'Deny If Tool Not Selected By LLM',
        description: 'Tool not in LLM-selected tools list'
    },
    {
        flag: ToolCheckFlags.DeterministicLLMSelectedTools,
        label: 'Deny If No LLM Calls Made',
        description: 'App never made an LLM call'
    },
    {
        flag: ToolCheckFlags.AIPoweredToolMatch,
        label: 'Deny If Intent Mismatch',
        description: 'Tool does not match user intent'
    }
];

interface MASDenyConditionsTabProps {
    mas: MAS;
}

export function MASDenyConditionsTab({mas}: MASDenyConditionsTabProps) {
    const {mutate: updateMAS, isPending} = useUpdateMAS(mas.id);

    const checks = mas.enabled_tool_checks ?? 0;
    const allFlags = TOOL_CHECKS.reduce((acc, {flag}) => acc | flag, 0);
    const allEnabled = (checks & allFlags) === allFlags;

    const toggleCheck = (flag: number, enabled: boolean) => {
        const newChecks = enabled ? checks | flag : checks & ~flag;
        updateMAS(
            {name: mas.name, enabled_tool_checks: newChecks},
            {
                onSuccess: () => toast.success('Deny conditions updated'),
                onError: () => toast.error('Failed to update deny conditions')
            }
        );
    };

    const toggleAll = () => {
        updateMAS(
            {name: mas.name, enabled_tool_checks: allEnabled ? 0 : allFlags},
            {
                onSuccess: () => toast.success(`All deny conditions ${allEnabled ? 'disabled' : 'enabled'}`),
                onError: () => toast.error('Failed to update deny conditions')
            }
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex items-start justify-between gap-4">
                <p className="text-sm text-muted-foreground">
                    These guardrails control when auth requests are denied before execution. They apply to all agentic
                    services on this multi-agent system.
                </p>
                <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-xs text-muted-foreground">{allEnabled ? 'Disable all' : 'Enable all'}</span>
                    <Switch
                        checked={allEnabled}
                        onCheckedChange={toggleAll}
                        disabled={isPending}
                        className="cursor-pointer"
                    />
                </div>
            </div>

            <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                    Deny Conditions
                </p>
                <div className="grid gap-3 sm:grid-cols-3">
                    {TOOL_CHECKS.map(({flag, label, description}) => {
                        const enabled = (checks & flag) !== 0;
                        return (
                            <div
                                key={flag}
                                className={`flex items-start gap-3 p-4 rounded-lg border transition-colors ${enabled ? 'bg-card' : 'bg-muted/30'}`}
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
