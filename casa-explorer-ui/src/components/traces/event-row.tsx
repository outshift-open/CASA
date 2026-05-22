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

import {Fragment, useState, useRef, useEffect} from 'react';
import {
    ChevronDown,
    ChevronRight,
    Zap,
    ArrowRightLeft,
    Brain,
    BrainCircuit,
    CheckCircle2,
    XCircle,
    Download,
    BotMessageSquare
} from 'lucide-react';
import {Badge} from '@/components/ui/badge';
import {CheckTypeBadge} from '@/components/ui/check-type-badge';
import {AuthStatusBadge} from '@/components/ui/auth-status-badge';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {APP_TYPE_LABELS, APP_TYPE_CLASSES} from '@/components/ui/app-type-badge';
import {getAppColorClass} from '@/lib/app-colors';
import {toast} from 'sonner';
import {EventType} from '@/types/trace.types';
import type {Trace, BlockingReason} from '@/types/trace.types';
import type {AppType} from '@/types/app.types';

// ─── Types ───────────────────────────────────────────────────────────────────

export type AppInfo = {name: string; type: AppType};
export type AppNames = Record<string, AppInfo>;

// ─── Constants ───────────────────────────────────────────────────────────────

export const BLOCKING_REASON_LABELS: Record<BlockingReason, string> = {
    no_llm_calls_made_by_app: 'No LLM Calls Made',
    tool_not_selected_by_llm: 'Not Selected By LLM',
    tool_intent_mismatch: 'Intent Mismatch',
    tool_parameters_mismatch: 'Params Mismatch',
    modified_mcp_tool_defs: 'Modified Tool Defs',
    insufficient_scope: 'Insufficient Scope'
};

export const BLOCKING_REASON_DESCRIPTIONS: Partial<Record<BlockingReason, string>> = {
    no_llm_calls_made_by_app: 'The app made no LLM calls before requesting tool access',
    tool_not_selected_by_llm: 'Requested MCP Server Tool was not selected by the LLM',
    tool_intent_mismatch: "MCP Server Tool choice doesn't match the intention of original input",
    tool_parameters_mismatch: 'Requested MCP Server Tool Parameters are different from those selected by the LLM',
    modified_mcp_tool_defs: 'The LLM received modified MCP Server Tool Definitions',
    insufficient_scope: 'Token does not have the required scope for this tool'
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extractToolName(s: string): string {
    const m = s.match(/name='([^']+)'/);
    return m ? m[1] : s;
}

export function parseToolsList(raw: string[] | string | null | undefined): string[] {
    if (!raw) return [];
    const items = Array.isArray(raw)
        ? raw
        : (() => {
              try {
                  const parsed = JSON.parse(raw);
                  return Array.isArray(parsed) ? parsed : [raw];
              } catch {
                  return [raw];
              }
          })();
    return items.map(extractToolName);
}

export function downloadJson(data: unknown, filename: string) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 100);
}

function shortId(id: string | undefined): string {
    if (!id) return '—';
    return id.length > 8 ? `${id.slice(0, 8)}…` : id;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

export function ToolChips({tools}: {tools: string[]}) {
    if (tools.length === 0) return null;
    return (
        <>
            {tools.map((t) => (
                <code
                    key={t}
                    className="mx-0.5 px-1.5 py-0.5 rounded-full bg-white/8 border border-white/10 text-[10px] font-mono text-foreground/80"
                >
                    {t}
                </code>
            ))}
        </>
    );
}

export function AppIdChip({id, appNames}: {id: string | undefined; appNames: AppNames}) {
    if (!id) return <span className="text-muted-foreground">—</span>;
    const info = appNames[id];
    const nameColorClass = info?.type ? `${getAppColorClass(id, info.type)} font-semibold` : 'text-foreground/80';
    return (
        <span className="inline-flex items-center gap-1">
            {info?.type && (
                <span
                    className={`px-1 py-0.5 rounded text-[9px] font-medium uppercase tracking-wide ${APP_TYPE_CLASSES[info.type]}`}
                >
                    {APP_TYPE_LABELS[info.type]}
                </span>
            )}
            <code className={`text-[11px] font-mono ${nameColorClass}`} title={id}>
                {info?.name ?? shortId(id)}
            </code>
        </span>
    );
}

export function EventTimestamp({createdAt}: {createdAt: string}) {
    if (!createdAt) return null;
    const time = new Date(createdAt).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    return (
        <span className="ml-auto pl-3 text-[11px] text-muted-foreground/60 flex-shrink-0 tabular-nums min-w-[64px] text-right">
            {time}
        </span>
    );
}

const ALWAYS_HIDDEN = new Set(['id', 'user_input_id', 'mas_id', 'created_at']);
const JWT_FIELDS = new Set(['token', 'subject_token', 'act_token']);
const JSON_FIELDS = new Set(['prompt']);
const FIELD_LABELS: Record<string, string> = {prompt: 'task'};

function decodeJwtPayload(jwt: string): Record<string, unknown> | null {
    try {
        const parts = jwt.split('.');
        if (parts.length !== 3) return null;
        const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(payload));
    } catch {
        return null;
    }
}

function tryParseJson(val: string): unknown | null {
    try {
        return JSON.parse(val);
    } catch {
        return null;
    }
}

function formatValue(key: string, val: unknown): string {
    if (JWT_FIELDS.has(key) && typeof val === 'string') {
        const decoded = decodeJwtPayload(val);
        return decoded ? JSON.stringify(decoded, null, 2) : val;
    }
    if (JSON_FIELDS.has(key) && typeof val === 'string') {
        const parsed = tryParseJson(val);
        return parsed !== null ? JSON.stringify(parsed, null, 2) : val;
    }
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'object') return JSON.stringify(val, null, 2);
    return String(val);
}

export function EventAttributes({event}: {event: Trace['event']}) {
    const entries = Object.entries(event).filter(
        ([key, val]) => !ALWAYS_HIDDEN.has(key) && val !== null && val !== undefined
    );
    if (entries.length === 0) return null;
    return (
        <div className="ml-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
            {entries.map(([key, val]) => {
                const isJwt = JWT_FIELDS.has(key) && typeof val === 'string';
                const isTools = key === 'tools';
                const toolsList = isTools ? parseToolsList(val as string[] | string | null) : null;
                const display = formatValue(key, val);
                return (
                    <Fragment key={key}>
                        <span className="text-[10px] text-muted-foreground/70 font-mono pt-0.5 whitespace-nowrap">
                            {FIELD_LABELS[key] ?? key}
                        </span>
                        {isTools && toolsList && toolsList.length > 0 ? (
                            <span className="text-[10px] font-mono text-foreground/80">{toolsList.join(', ')}</span>
                        ) : isJwt || JSON_FIELDS.has(key) ? (
                            <pre className="text-[10px] font-mono text-foreground/80 whitespace-pre-wrap break-all leading-relaxed">
                                {display}
                            </pre>
                        ) : (
                            <span className="text-[10px] font-mono text-foreground/80 break-all">{display}</span>
                        )}
                    </Fragment>
                );
            })}
        </div>
    );
}

// ─── EventRow ────────────────────────────────────────────────────────────────

interface EventRowProps {
    trace: Trace;
    appNames: AppNames;
    initialExpanded?: boolean;
}

export function EventRow({trace, appNames, initialExpanded}: EventRowProps) {
    const {event_type, event, created_at} = trace;
    const [expanded, setExpanded] = useState(initialExpanded ?? false);
    const rowRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (initialExpanded && rowRef.current) {
            const el = rowRef.current;
            let container: HTMLElement | null = el.parentElement;
            while (container) {
                const {overflowY} = getComputedStyle(container);
                if (overflowY === 'auto' || overflowY === 'scroll') break;
                container = container.parentElement;
            }
            if (!container) return;
            const relativeTop =
                el.getBoundingClientRect().top - container.getBoundingClientRect().top + container.scrollTop;
            container.scrollTo({top: relativeTop - 80, behavior: 'smooth'});
        }
    }, [initialExpanded]);

    // Visual weight tiers:
    //   MCP tool calls  → full brightness, thicker border (security decisions)
    //   Agent calls     → medium prominence
    //   LLM calls       → dimmed (implementation detail, not a security event)
    //   Token events    → ghosted (plumbing)
    let borderStyle: React.CSSProperties = {borderColor: 'rgba(255,255,255,0.08)'};
    let borderWidth = 'border-l-2';
    let expandedBgClass = 'bg-white/[0.02]';
    let rowBgClass = '';
    let hoverBgClass = 'hover:bg-white/[0.03]';
    let rowOpacity = '';
    let icon: React.ReactNode = null;
    let summary: React.ReactNode = null;

    if (event_type === EventType.TokenIssued) {
        // Ghosted — purely infrastructure
        borderStyle = {borderColor: 'rgba(255,255,255,0.08)'};
        rowOpacity = 'opacity-80';
        hoverBgClass = 'hover:opacity-80 hover:bg-white/[0.02]';
        icon = <Zap className="h-3 w-3 text-white/35 mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[12px] text-white/30 flex items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-white/40 flex-shrink-0">Token issued</span>
                {event.app_id && (
                    <>
                        <span className="flex-shrink-0">for</span>
                        <AppIdChip id={event.app_id} appNames={appNames} />
                    </>
                )}
            </div>
        );
    } else if (event_type === EventType.TokenExchanged) {
        const tools = parseToolsList(event.tools);
        // Ghosted — infrastructure
        borderStyle = {borderColor: 'rgba(255,255,255,0.08)'};
        rowOpacity = 'opacity-80';
        hoverBgClass = 'hover:opacity-80 hover:bg-white/[0.02]';
        icon = <ArrowRightLeft className="h-3 w-3 text-white/35 mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[12px] text-white/30 flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-white/40">Token exchanged</span>
                {event.subject_app_id && (
                    <>
                        <span>by</span>
                        <AppIdChip id={event.subject_app_id} appNames={appNames} />
                    </>
                )}
                {event.act_app_id && (
                    <>
                        <span className="text-white/20">→</span>
                        <span>for</span>
                        <AppIdChip id={event.act_app_id} appNames={appNames} />
                    </>
                )}
                {tools.length > 0 && (
                    <>
                        <span className="ml-1">— requested tool</span>
                        <ToolChips tools={tools} />
                    </>
                )}
            </div>
        );
    } else if (event_type === EventType.LLMCallStarted) {
        // Dimmed — implementation detail
        borderStyle = {borderColor: 'rgba(96,165,250,0.25)'};
        expandedBgClass = 'bg-blue-500/5';
        rowBgClass = 'bg-blue-500/5';
        rowOpacity = 'opacity-85';
        hoverBgClass = 'hover:opacity-85 hover:bg-blue-500/10';
        icon = <Brain className="h-3 w-3 text-blue-400/70 mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[12px] text-muted-foreground/60 flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-foreground/60">LLM Call</span>
                {event.app_id && (
                    <>
                        <span className="text-muted-foreground/40">from</span>
                        <AppIdChip id={event.app_id} appNames={appNames} />
                    </>
                )}
            </div>
        );
    } else if (event_type === EventType.LLMCallEnded) {
        const selectedTools = parseToolsList(event.tools);
        // Dimmed — implementation detail
        borderStyle = {borderColor: 'rgba(96,165,250,0.25)'};
        expandedBgClass = 'bg-blue-500/5';
        rowBgClass = 'bg-blue-500/5';
        rowOpacity = 'opacity-85';
        hoverBgClass = 'hover:opacity-85 hover:bg-blue-500/10';
        icon = <BrainCircuit className="h-3 w-3 text-blue-400/70 mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[12px] text-muted-foreground/60 flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-foreground/60">LLM responded</span>
                {event.app_id && (
                    <>
                        <span className="text-muted-foreground/40">from</span>
                        <AppIdChip id={event.app_id} appNames={appNames} />
                    </>
                )}
                {selectedTools.length > 0 && (
                    <>
                        <span className="ml-1 text-muted-foreground/40">— selected</span>
                        <ToolChips tools={selectedTools} />
                    </>
                )}
            </div>
        );
    } else if (event_type === EventType.AgentCallStarted) {
        // Medium prominence
        borderStyle = {borderColor: 'rgba(167,139,250,0.45)'};
        borderWidth = 'border-l-2';
        expandedBgClass = 'bg-violet-500/8';
        rowBgClass = 'bg-violet-500/8';
        hoverBgClass = 'hover:bg-violet-500/15';
        icon = <BotMessageSquare className="h-3.5 w-3.5 text-violet-400/80 mt-0.5 flex-shrink-0" />;
        summary = (
            <div className="text-[13px] text-muted-foreground flex flex-wrap items-center gap-x-1 flex-1 min-w-0">
                <span className="font-medium text-violet-200/80">Agent call</span>
                {event.caller_app_id && (
                    <>
                        <span>by</span>
                        <AppIdChip id={event.caller_app_id} appNames={appNames} />
                    </>
                )}
                {event.callee_app_id && (
                    <>
                        <span className="text-muted-foreground/40">→</span>
                        <AppIdChip id={event.callee_app_id} appNames={appNames} />
                    </>
                )}
            </div>
        );
    } else if (event_type === EventType.MCPCallStarted) {
        const blocked = event.blocked;
        const reason = event.blocking_reason ? BLOCKING_REASON_LABELS[event.blocking_reason] : null;
        const reasonDescription = event.blocking_reason ? BLOCKING_REASON_DESCRIPTIONS[event.blocking_reason] : null;
        // Prominent but not blinding — security decisions stand out without overwhelming
        borderWidth = 'border-l-[3px]';
        borderStyle = blocked ? {borderColor: 'rgba(248,113,113,0.45)'} : {borderColor: 'rgba(34,197,94,0.35)'};
        expandedBgClass = blocked ? 'bg-red-500/5' : 'bg-green-500/5';
        rowBgClass = blocked ? 'bg-red-500/[0.04]' : 'bg-green-500/[0.04]';
        hoverBgClass = blocked ? 'hover:bg-red-500/8' : 'hover:bg-green-500/8';
        icon = blocked ? (
            <XCircle className="h-3.5 w-3.5 text-red-400/80 mt-0.5 flex-shrink-0" />
        ) : (
            <CheckCircle2 className="h-3.5 w-3.5 text-green-400/80 mt-0.5 flex-shrink-0" />
        );
        summary = (
            <div className="text-[13px] flex flex-wrap items-center gap-x-2 gap-y-1 flex-1 min-w-0">
                <span className={`font-medium ${blocked ? 'text-red-400/90' : 'text-green-400/90'}`}>Tool Call</span>
                <code
                    className={`px-1.5 py-0.5 rounded font-mono text-[11px] ${
                        blocked
                            ? 'bg-red-500/10 text-red-300/80 border border-red-500/20'
                            : 'bg-green-500/10 text-green-300/80 border border-green-500/20'
                    }`}
                >
                    {event.tool ?? '—'}
                </code>
                {(event.caller_app_id || event.callee_app_id) && (
                    <span className="text-muted-foreground/60 flex items-center gap-1">
                        <span>from</span>
                        <AppIdChip id={event.caller_app_id} appNames={appNames} />
                        <span className="text-muted-foreground/40">→</span>
                        <AppIdChip id={event.callee_app_id} appNames={appNames} />
                    </span>
                )}
                {blocked ? (
                    <>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Badge
                                    variant="outline"
                                    className="text-[10px] h-4 px-1.5 cursor-default border-red-500/50 text-red-400"
                                >
                                    Denied{reason ? ` · ${reason}` : ''}
                                </Badge>
                            </TooltipTrigger>
                            {reasonDescription && (
                                <TooltipContent>
                                    <p className="text-center">{reasonDescription}</p>
                                </TooltipContent>
                            )}
                        </Tooltip>
                        <CheckTypeBadge type={event.blocking_type} size="sm" />
                    </>
                ) : (
                    <AuthStatusBadge blocked={false} size="sm" />
                )}
            </div>
        );
    }

    if (!icon) return null;

    return (
        <div ref={rowRef} className={`${borderWidth} ml-2 transition-opacity`} style={borderStyle}>
            <button
                type="button"
                className={`w-full flex items-start gap-2 py-1.5 pl-4 transition-all text-left cursor-pointer ${hoverBgClass} ${rowBgClass} ${rowOpacity}`}
                onClick={() => setExpanded((v) => !v)}
            >
                {expanded ? (
                    <ChevronDown className="h-3.5 w-3.5 text-muted-foreground/70 mt-0.5 flex-shrink-0" />
                ) : (
                    <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/70 mt-0.5 flex-shrink-0" />
                )}
                {icon}
                {summary}
                <EventTimestamp createdAt={created_at} />
            </button>
            {expanded && (
                <div className={`pl-4 pb-2 ${expandedBgClass}`}>
                    {event_type === EventType.AgentCallStarted && event.prompt && (
                        <div
                            className="ml-6 mr-4 mt-1.5 mb-1 rounded-lg overflow-hidden"
                            style={{background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.18)'}}
                        >
                            <div
                                className="px-3 py-1 text-[9px] font-bold uppercase tracking-widest text-violet-400/60"
                                style={{borderBottom: '1px solid rgba(167,139,250,0.12)'}}
                            >
                                Message to agent
                            </div>
                            <p className="px-3 py-2 text-[11px] text-white/60 font-mono leading-relaxed whitespace-pre-wrap break-words">
                                {event.prompt}
                            </p>
                        </div>
                    )}
                    <EventAttributes event={event} />
                    <button
                        type="button"
                        onClick={(e) => {
                            e.stopPropagation();
                            downloadJson(trace, `event-${trace.id.slice(0, 8)}.json`);
                            toast.success('Event downloaded');
                        }}
                        className="mt-2 ml-6 flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                    >
                        <Download className="h-3 w-3" />
                        Download event
                    </button>
                </div>
            )}
        </div>
    );
}
