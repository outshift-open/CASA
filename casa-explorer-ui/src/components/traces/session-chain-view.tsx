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
import {
    CheckCircle2,
    XCircle,
    ChevronDown,
    ChevronRight,
    ArrowRightLeft,
    Brain,
    BrainCircuit,
    Zap,
    BotMessageSquare,
    Download
} from 'lucide-react';
import {Badge} from '@/components/ui/badge';
import {Tooltip, TooltipContent, TooltipTrigger} from '@/components/ui/tooltip';
import {CheckTypeBadge} from '@/components/ui/check-type-badge';
import {AuthStatusBadge} from '@/components/ui/auth-status-badge';
import {APP_TYPE_LABELS, APP_TYPE_CLASSES} from '@/components/ui/app-type-badge';
import {getAppColor, getAppColorClass} from '@/lib/app-colors';
import {toast} from 'sonner';
import {EventType} from '@/types/trace.types';
import type {Trace} from '@/types/trace.types';
import type {AppNames} from '@/components/traces/event-row';
import {
    BLOCKING_REASON_LABELS,
    BLOCKING_REASON_DESCRIPTIONS,
    parseToolsList,
    EventAttributes,
    EventTimestamp,
    downloadJson
} from '@/components/traces/event-row';

// ─── Chain building ───────────────────────────────────────────────────────────

interface ChainStep {
    kind: 'token' | 'agent' | 'llm' | 'mcp';
    trace: Trace;
    children: ChainStep[];
}

function buildChain(events: Trace[]): ChainStep[] {
    const roots: ChainStep[] = [];
    // Stack tracks ancestry: each TokenExchanged/AgentCall pushes a new scope
    const stack: ChainStep[] = [];

    const currentParent = () => stack[stack.length - 1] ?? null;

    const appendChild = (step: ChainStep) => {
        const parent = currentParent();
        if (parent) {
            parent.children.push(step);
        } else {
            roots.push(step);
        }
    };

    for (const trace of events) {
        const {event_type} = trace;

        if (event_type === EventType.TokenIssued) {
            const step: ChainStep = {kind: 'token', trace, children: []};
            // Token issued is always a new root-level scope; clear the stack
            stack.length = 0;
            roots.push(step);
            stack.push(step);
        } else if (event_type === EventType.TokenExchanged) {
            const step: ChainStep = {kind: 'token', trace, children: []};
            // Pop back to the nearest agent scope (becomes a child of it), or
            // all the way to root if no agent is on the stack (becomes a root sibling)
            while (stack.length > 0 && stack[stack.length - 1].kind !== 'agent') {
                stack.pop();
            }
            appendChild(step);
            stack.push(step);
        } else if (event_type === EventType.AgentCallStarted) {
            const step: ChainStep = {kind: 'agent', trace, children: []};
            appendChild(step);
            stack.push(step);
        } else if (event_type === EventType.LLMCallStarted || event_type === EventType.LLMCallEnded) {
            const step: ChainStep = {kind: 'llm', trace, children: []};
            appendChild(step);
        } else if (event_type === EventType.MCPCallStarted) {
            const step: ChainStep = {kind: 'mcp', trace, children: []};
            appendChild(step);
        }
    }

    return roots;
}

// ─── Node renderers ───────────────────────────────────────────────────────────

function AppChip({id, appNames}: {id: string | undefined; appNames: AppNames}) {
    if (!id) return null;
    const info = appNames[id];
    const color = info ? getAppColor(id, info.type) : '#94a3b8';
    const colorClass = info ? getAppColorClass(id, info.type) : 'text-slate-400';
    return (
        <span className="inline-flex items-center gap-1">
            {info?.type && (
                <span
                    className={`px-1 py-0.5 rounded text-[9px] font-medium uppercase tracking-wide ${APP_TYPE_CLASSES[info.type]}`}
                >
                    {APP_TYPE_LABELS[info.type]}
                </span>
            )}
            <span className={`text-[11px] font-mono font-semibold ${colorClass}`} title={id} style={{color}}>
                {info?.name ?? id.slice(0, 8) + '…'}
            </span>
        </span>
    );
}

function ExpandableMessage({label, text}: {label: string; text: string}) {
    const [open, setOpen] = useState(false);
    const isLong = text.length > 120;
    const display = !isLong || open ? text : text.slice(0, 120) + '…';
    return (
        <div
            className="mt-2 rounded-lg overflow-hidden"
            style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.07)'
            }}
        >
            <div
                className="px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest text-white/30"
                style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}
            >
                {label}
            </div>
            <div className="px-3 py-2 text-[11px] text-white/60 font-mono leading-relaxed whitespace-pre-wrap break-words">
                {display}
            </div>
            {isLong && (
                <button
                    type="button"
                    onClick={() => setOpen((v) => !v)}
                    className="w-full px-3 py-1 text-[10px] text-white/30 hover:text-white/60 transition-colors cursor-pointer text-left"
                    style={{borderTop: '1px solid rgba(255,255,255,0.06)'}}
                >
                    {open ? '↑ Show less' : '↓ Show more'}
                </button>
            )}
        </div>
    );
}

function DownloadButton({trace}: {trace: Trace}) {
    return (
        <button
            type="button"
            onClick={(e) => {
                e.stopPropagation();
                downloadJson(trace, `event-${trace.id.slice(0, 8)}.json`);
                toast.success('Event downloaded');
            }}
            className="mt-2 ml-6 flex items-center gap-1 text-[10px] text-white/30 hover:text-white/60 transition-colors cursor-pointer"
        >
            <Download className="h-3 w-3" />
            Download event
        </button>
    );
}

function TokenNode({step, appNames}: {step: ChainStep; appNames: AppNames}) {
    const {event_type, event} = step.trace;
    const isIssued = event_type === EventType.TokenIssued;
    const tools = parseToolsList(event.tools);
    const [expanded, setExpanded] = useState(false);

    return (
        <div
            className="rounded-lg overflow-hidden opacity-80"
            style={{background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)'}}
        >
            <button
                type="button"
                className="w-full flex items-center gap-2 py-1.5 px-3 text-left cursor-pointer hover:bg-white/[0.02] transition-colors"
                onClick={() => setExpanded((v) => !v)}
            >
                <div className="mt-0.5 flex-shrink-0">
                    {isIssued ? (
                        <Zap className="h-3 w-3 text-white/35" />
                    ) : (
                        <ArrowRightLeft className="h-3 w-3 text-white/35" />
                    )}
                </div>
                <div className="flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-[11px] text-white/30 min-w-0 flex-1">
                    <span className="font-medium text-white/40">{isIssued ? 'Token issued' : 'Token exchanged'}</span>
                    {isIssued && event.app_id && (
                        <>
                            <span>for</span>
                            <AppChip id={event.app_id} appNames={appNames} />
                        </>
                    )}
                    {!isIssued && event.subject_app_id && (
                        <>
                            <span>by</span>
                            <AppChip id={event.subject_app_id} appNames={appNames} />
                        </>
                    )}
                    {!isIssued && event.act_app_id && (
                        <>
                            <span className="text-white/20">→</span>
                            <span>for</span>
                            <AppChip id={event.act_app_id} appNames={appNames} />
                        </>
                    )}
                    {!isIssued && tools.length > 0 && (
                        <>
                            <span className="ml-1 text-white/25">— requested tool</span>
                            <code className="mx-0.5 px-1.5 py-0.5 rounded-full bg-white/8 border border-white/10 text-[10px] font-mono text-white/50">
                                {tools.join(', ')}
                            </code>
                        </>
                    )}
                </div>
                <EventTimestamp createdAt={step.trace.created_at} />
                {expanded ? (
                    <ChevronDown className="h-3 w-3 text-white/20 flex-shrink-0" />
                ) : (
                    <ChevronRight className="h-3 w-3 text-white/20 flex-shrink-0" />
                )}
            </button>
            {expanded && (
                <div className="pb-2" style={{borderTop: '1px solid rgba(255,255,255,0.06)'}}>
                    <EventAttributes event={event} />
                    <DownloadButton trace={step.trace} />
                </div>
            )}
        </div>
    );
}

function AgentNode({step, appNames}: {step: ChainStep; appNames: AppNames}) {
    const {event} = step.trace;
    const [expanded, setExpanded] = useState(false);
    const hasPrompt = !!event.prompt;

    return (
        <div
            className="rounded-lg overflow-hidden"
            style={{background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.45)'}}
        >
            <button
                type="button"
                className="w-full flex items-center gap-2 px-3 py-2 text-left cursor-pointer hover:bg-violet-500/15 transition-colors"
                onClick={() => hasPrompt && setExpanded((v) => !v)}
            >
                <BotMessageSquare className="h-3.5 w-3.5 text-violet-400/80 flex-shrink-0" />
                <div className="flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-[13px] flex-1 min-w-0">
                    <span className="font-medium text-violet-200/80">Agent call</span>
                    {event.caller_app_id && (
                        <>
                            <span className="text-white/40">by</span>
                            <AppChip id={event.caller_app_id} appNames={appNames} />
                        </>
                    )}
                    {event.callee_app_id && (
                        <>
                            <span className="text-white/30">→</span>
                            <AppChip id={event.callee_app_id} appNames={appNames} />
                        </>
                    )}
                </div>
                <EventTimestamp createdAt={step.trace.created_at} />
                {expanded ? (
                    <ChevronDown className="h-3.5 w-3.5 text-violet-400/60 flex-shrink-0" />
                ) : (
                    <ChevronRight className="h-3.5 w-3.5 text-violet-400/60 flex-shrink-0" />
                )}
            </button>
            {expanded && (
                <div className="pb-2" style={{borderTop: '1px solid rgba(167,139,250,0.18)'}}>
                    {event.prompt && (
                        <div
                            className="mx-3 mt-2 rounded-lg overflow-hidden"
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
                    <DownloadButton trace={step.trace} />
                </div>
            )}
        </div>
    );
}

function LLMNode({step, appNames, index}: {step: ChainStep; appNames: AppNames; index?: number}) {
    const {event_type, event} = step.trace;
    const isEnded = event_type === EventType.LLMCallEnded;
    const [expanded, setExpanded] = useState(false);
    const selectedTools = parseToolsList(event.tools);

    return (
        <div
            className="rounded-lg overflow-hidden opacity-85 hover:opacity-100 transition-opacity"
            style={{background: 'rgba(96,165,250,0.05)', border: '1px solid rgba(96,165,250,0.25)'}}
        >
            <button
                type="button"
                className="w-full flex items-center gap-2 px-3 py-1.5 text-left cursor-pointer hover:bg-blue-500/10 transition-colors"
                onClick={() => setExpanded((v) => !v)}
            >
                {isEnded ? (
                    <BrainCircuit className="h-3 w-3 text-blue-400/70 flex-shrink-0" />
                ) : (
                    <Brain className="h-3 w-3 text-blue-400/70 flex-shrink-0" />
                )}
                <div className="flex flex-wrap items-center gap-x-1.5 text-[12px] text-white/60 flex-1 min-w-0">
                    <span className="font-medium text-white/60">
                        {isEnded ? 'LLM responded' : `LLM Call${index !== undefined ? ` #${index + 1}` : ''}`}
                    </span>
                    {event.app_id && (
                        <>
                            <span className="text-white/40">from</span>
                            <AppChip id={event.app_id} appNames={appNames} />
                        </>
                    )}
                    {isEnded && selectedTools.length > 0 && (
                        <>
                            <span className="ml-1 text-white/40">— selected</span>
                            <code className="mx-0.5 px-1.5 py-0.5 rounded-full bg-white/8 border border-white/10 text-[10px] font-mono text-blue-300/70">
                                {selectedTools.join(', ')}
                            </code>
                        </>
                    )}
                </div>
                <EventTimestamp createdAt={step.trace.created_at} />
                {expanded ? (
                    <ChevronDown className="h-3 w-3 text-white/20 flex-shrink-0" />
                ) : (
                    <ChevronRight className="h-3 w-3 text-white/20 flex-shrink-0" />
                )}
            </button>
            {expanded && (
                <div className="pb-2" style={{borderTop: '1px solid rgba(96,165,250,0.15)'}}>
                    {isEnded && event.response && <ExpandableMessage label="LLM response" text={event.response} />}
                    <EventAttributes event={event} />
                    <DownloadButton trace={step.trace} />
                </div>
            )}
        </div>
    );
}

function MCPNode({step, appNames}: {step: ChainStep; appNames: AppNames}) {
    const {event} = step.trace;
    const blocked = !!event.blocked;
    const [expanded, setExpanded] = useState(false);
    const reason = event.blocking_reason ? BLOCKING_REASON_LABELS[event.blocking_reason] : null;
    const reasonDesc = event.blocking_reason ? BLOCKING_REASON_DESCRIPTIONS[event.blocking_reason] : null;

    const borderColor = blocked ? 'rgba(248,113,113,0.45)' : 'rgba(34,197,94,0.35)';
    const bgColor = blocked ? 'rgba(248,113,113,0.04)' : 'rgba(74,222,128,0.04)';
    const hoverBg = blocked ? 'hover:bg-red-500/8' : 'hover:bg-green-500/8';

    return (
        <div className="rounded-lg overflow-hidden" style={{background: bgColor, border: `1px solid ${borderColor}`}}>
            <button
                type="button"
                className={`w-full flex items-center gap-2 px-3 py-2 text-left cursor-pointer transition-colors ${hoverBg}`}
                onClick={() => setExpanded((v) => !v)}
            >
                {blocked ? (
                    <XCircle className="h-3.5 w-3.5 text-red-400/80 flex-shrink-0" />
                ) : (
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-400/80 flex-shrink-0" />
                )}
                <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[13px] flex-1 min-w-0">
                    <span className={`font-medium ${blocked ? 'text-red-400/90' : 'text-green-400/90'}`}>
                        Tool Call
                    </span>
                    <code
                        className={`px-1.5 py-0.5 rounded font-mono text-[11px] ${
                            blocked
                                ? 'bg-red-500/10 text-red-300/80 border border-red-500/20'
                                : 'bg-green-500/10 text-green-300/80 border border-green-500/20'
                        }`}
                    >
                        {event.tool ?? '—'}
                    </code>
                    {event.caller_app_id && (
                        <span className="text-white/60 flex items-center gap-1 text-[11px]">
                            <span>from</span>
                            <AppChip id={event.caller_app_id} appNames={appNames} />
                            <span className="text-white/30">→</span>
                            <AppChip id={event.callee_app_id} appNames={appNames} />
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
                                {reasonDesc && (
                                    <TooltipContent>
                                        <p className="text-center max-w-[200px]">{reasonDesc}</p>
                                    </TooltipContent>
                                )}
                            </Tooltip>
                            {event.blocking_type && <CheckTypeBadge type={event.blocking_type} size="sm" />}
                        </>
                    ) : (
                        <AuthStatusBadge blocked={false} size="sm" />
                    )}
                </div>
                <EventTimestamp createdAt={step.trace.created_at} />
                {expanded ? (
                    <ChevronDown className="h-3.5 w-3.5 flex-shrink-0 text-white/30" />
                ) : (
                    <ChevronRight className="h-3.5 w-3.5 flex-shrink-0 text-white/30" />
                )}
            </button>
            {expanded && (
                <div className="pb-2" style={{borderTop: `1px solid ${borderColor}`}}>
                    {blocked && reasonDesc && (
                        <div
                            className="mx-3 mt-2 rounded-lg px-3 py-2 text-[11px] leading-relaxed"
                            style={{
                                background: 'rgba(248,113,113,0.08)',
                                border: '1px solid rgba(248,113,113,0.2)',
                                color: '#fca5a5'
                            }}
                        >
                            <span className="font-semibold text-red-300">Why denied: </span>
                            {reasonDesc}
                        </div>
                    )}
                    {!blocked && (
                        <div
                            className="mx-3 mt-2 rounded-lg px-3 py-2 text-[11px]"
                            style={{
                                background: 'rgba(74,222,128,0.06)',
                                border: '1px solid rgba(74,222,128,0.15)',
                                color: '#86efac'
                            }}
                        >
                            Tool call passed all authorization checks
                        </div>
                    )}
                    <EventAttributes event={event} />
                    <DownloadButton trace={step.trace} />
                </div>
            )}
        </div>
    );
}

// ─── Connector line ───────────────────────────────────────────────────────────

// ─── Recursive step renderer ──────────────────────────────────────────────────

function ChainStepNode({
    step,
    appNames,
    isLast,
    llmIndex
}: {
    step: ChainStep;
    appNames: AppNames;
    isLast: boolean;
    llmIndex?: number;
}) {
    const connectorColor =
        step.kind === 'agent'
            ? 'rgba(167,139,250,0.5)'
            : step.kind === 'mcp'
              ? step.trace.event.blocked
                  ? 'rgba(248,113,113,0.45)'
                  : 'rgba(74,222,128,0.45)'
              : 'rgba(255,255,255,0.18)';

    let llmCounter = 0;

    return (
        <div className="relative">
            {step.kind === 'token' && <TokenNode step={step} appNames={appNames} />}
            {step.kind === 'agent' && <AgentNode step={step} appNames={appNames} />}
            {step.kind === 'llm' && <LLMNode step={step} appNames={appNames} index={llmIndex} />}
            {step.kind === 'mcp' && <MCPNode step={step} appNames={appNames} />}

            {step.children.length > 0 && (
                <div className="mt-1.5 space-y-1.5">
                    {step.children.map((child, i) => {
                        const idx = child.kind === 'llm' ? llmCounter++ : undefined;
                        const isLastChild = i === step.children.length - 1;
                        const dashed = child.kind === 'llm';
                        const tx = 8; // trunk x
                        const nodeY = 16; // vertical midpoint of node row
                        const curveR = 8; // corner radius
                        // Path: down the trunk to (tx, nodeY-curveR), then quarter-circle right to (tx+curveR, nodeY), then straight to rail edge
                        const railW = 24;
                        const branchPath = `M ${tx} ${nodeY - curveR} Q ${tx} ${nodeY} ${tx + curveR} ${nodeY} L ${railW} ${nodeY}`;
                        return (
                            <div key={child.trace.id} className="relative" style={{paddingLeft: `${railW}px`}}>
                                <svg
                                    className="absolute left-0 top-0 h-full pointer-events-none"
                                    width={railW}
                                    style={{overflow: 'visible'}}
                                >
                                    {/* Vertical trunk — starts above this div to bridge the mt-1.5 gap from parent */}
                                    <line
                                        x1={tx}
                                        y1="-6"
                                        x2={tx}
                                        y2={isLastChild ? nodeY - curveR : '100%'}
                                        stroke={connectorColor}
                                        strokeWidth="1.5"
                                        strokeLinecap="round"
                                        strokeDasharray={dashed ? '4 3' : undefined}
                                    />
                                    {/* Quarter-circle branch into node */}
                                    <path
                                        d={branchPath}
                                        fill="none"
                                        stroke={connectorColor}
                                        strokeWidth="1.5"
                                        strokeLinecap="round"
                                        strokeDasharray={dashed ? '4 3' : undefined}
                                    />
                                    {/* Dot where branch meets the card */}
                                    <circle cx={railW} cy={nodeY} r="2.5" fill={connectorColor} />
                                </svg>
                                <ChainStepNode step={child} appNames={appNames} isLast={isLastChild} llmIndex={idx} />
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

// ─── Public component ─────────────────────────────────────────────────────────

interface SessionChainViewProps {
    events: Trace[];
    appNames: AppNames;
}

export function SessionChainView({events, appNames}: SessionChainViewProps) {
    const chain = buildChain(events);

    if (chain.length === 0) {
        return <div className="text-[12px] text-white/30 py-4 text-center">No events to display</div>;
    }

    return (
        <div className="space-y-1.5">
            {/* Chain */}
            <div className="space-y-1.5">
                {chain.map((step, i) => (
                    <ChainStepNode
                        key={step.trace.id}
                        step={step}
                        appNames={appNames}
                        isLast={i === chain.length - 1}
                    />
                ))}
            </div>
        </div>
    );
}
