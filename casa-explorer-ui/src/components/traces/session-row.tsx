/**
 * Copyright 2026 Cisco Systems, Inc. and its affiliates
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

import {useState} from 'react';
import {ChevronDown, ChevronRight, CheckCircle2, XCircle, Download, List, GitBranch} from 'lucide-react';
import {ToggleGroup, ToggleGroupItem} from '@/components/ui/toggle-group';
import {toast} from 'sonner';
import {EventType} from '@/types/trace.types';
import type {Trace} from '@/types/trace.types';
import {EventRow, downloadJson} from '@/components/traces/event-row';
import type {AppNames} from '@/components/traces/event-row';
import {SessionChainView} from '@/components/traces/session-chain-view';

type SessionView = 'list' | 'chain';

export interface SessionData {
    userInputId: string;
    prompt: string | null;
    createdAt: string;
    events: Trace[];
    allowedCount: number;
    deniedCount: number;
    llmCallCount: number;
    agentCallCount: number;
    mcpCallCount: number;
    tokenCount: number;
}

interface SessionRowProps {
    session: SessionData;
    appNames: AppNames;
    focusTraceId?: string | null;
}

export function SessionRow({session, appNames, focusTraceId}: SessionRowProps) {
    const [expanded, setExpanded] = useState(!!focusTraceId);
    const [view, setView] = useState<SessionView>('chain');

    const datetime = session.createdAt
        ? new Date(session.createdAt).toLocaleString([], {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
          })
        : null;

    let llmCallIndex = 0;

    return (
        <div className="border rounded-lg overflow-hidden">
            <button
                type="button"
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-accent/50 transition-colors text-left cursor-pointer"
                onClick={() => setExpanded((v) => !v)}
            >
                {expanded ? (
                    <ChevronDown className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                ) : (
                    <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0 overflow-hidden">
                    <p className="text-sm font-medium truncate">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mr-1.5">
                            Task:
                        </span>
                        {session.prompt ?? <span className="text-muted-foreground italic">No prompt</span>}
                    </p>
                    {datetime && <p className="text-xs text-muted-foreground mt-0.5">{datetime}</p>}
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0 text-xs">
                    <span className="text-muted-foreground tabular-nums">
                        {session.tokenCount} token{session.tokenCount !== 1 ? 's' : ''}
                        {session.agentCallCount > 0 && <> · {session.agentCallCount} agent</>}
                        {session.llmCallCount > 0 && <> · {session.llmCallCount} LLM</>}
                        {session.mcpCallCount > 0 && <> · {session.mcpCallCount} MCP</>}
                    </span>
                    <span className="flex items-center gap-2">
                        {session.allowedCount > 0 && (
                            <span className="flex items-center gap-0.5 text-green-500 font-medium">
                                <CheckCircle2 className="h-3.5 w-3.5" />
                                {session.allowedCount}
                            </span>
                        )}
                        {session.deniedCount > 0 && (
                            <span className="flex items-center gap-0.5 text-destructive font-medium">
                                <XCircle className="h-3.5 w-3.5" />
                                {session.deniedCount}
                            </span>
                        )}
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                downloadJson(session.events, `session-${session.userInputId.slice(0, 8)}.json`);
                                toast.success('Session downloaded');
                            }}
                            className="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-accent transition-colors cursor-pointer"
                            aria-label="Download session"
                        >
                            <Download className="h-3.5 w-3.5" />
                        </button>
                    </span>
                </div>
            </button>

            {expanded && (
                <div className="border-t bg-muted/20">
                    {/* Shared toolbar: summary left, view toggle right */}
                    <div className="flex items-center justify-between px-4 py-2 border-b border-white/5">
                        <div className="flex items-center gap-3 text-[11px]">
                            {session.mcpCallCount > 0 && (
                                <>
                                    <span className="text-muted-foreground/50">Tool calls:</span>
                                    {session.allowedCount > 0 && (
                                        <span className="flex items-center gap-1 text-green-500 font-medium">
                                            <CheckCircle2 className="h-3 w-3" />
                                            {session.allowedCount} allowed
                                        </span>
                                    )}
                                    {session.deniedCount > 0 && (
                                        <span className="flex items-center gap-1 text-destructive font-medium">
                                            <XCircle className="h-3 w-3" />
                                            {session.deniedCount} denied
                                        </span>
                                    )}
                                </>
                            )}
                            <span className="text-muted-foreground/30 tabular-nums">
                                {session.events.length} events
                            </span>
                        </div>
                        <ToggleGroup
                            type="single"
                            variant="outline"
                            spacing={0}
                            value={view}
                            onValueChange={(v) => v && setView(v as SessionView)}
                        >
                            <ToggleGroupItem value="chain" aria-label="Chain view" className="h-7 w-7 p-0">
                                <GitBranch className="h-3.5 w-3.5" />
                            </ToggleGroupItem>
                            <ToggleGroupItem value="list" aria-label="List view" className="h-7 w-7 p-0">
                                <List className="h-3.5 w-3.5" />
                            </ToggleGroupItem>
                        </ToggleGroup>
                    </div>
                    <div className="px-4 pb-3 pt-2">
                        {view === 'chain' ? (
                            <SessionChainView events={session.events} appNames={appNames} />
                        ) : (
                            session.events.map((trace) => {
                                const idx = trace.event_type === EventType.LLMCallStarted ? llmCallIndex++ : undefined;
                                return (
                                    <EventRow
                                        key={trace.id}
                                        trace={trace}
                                        index={idx}
                                        appNames={appNames}
                                        initialExpanded={trace.id === focusTraceId}
                                    />
                                );
                            })
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
