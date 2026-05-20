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

import React, {useEffect, useCallback, useRef, useMemo, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import ELK from 'elkjs/lib/elk.bundled.js';
import {
    ReactFlow,
    Node,
    Edge,
    Controls,
    Background,
    BackgroundVariant,
    ConnectionMode,
    NodeTypes,
    MiniMap,
    Panel,
    ReactFlowProvider,
    useNodesState,
    useReactFlow
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {MASGraphNode} from './mas-graph-node';
import {MASFlowEdge as FlowEdgeComponent} from './mas-graph-flow-edge';
import {resolveCollisions} from './resolve-collisions';
import {Button} from '@/components/ui/button';
import {Bot, AppWindow, Server, Download, Network} from 'lucide-react';
import {toPng} from 'html-to-image';
import {useMASFlow} from '@/hooks/use-mas';
import type {MAS} from '@/types/mas.types';
import type {App, AppType} from '@/types/app.types';
import type {MASFlowEdge} from '@/types/mas.types';

interface MASGraphViewProps {
    mas: MAS;
    apps: App[];
    onAppClick?: (app: App) => void;
    searchTerm?: string;
    selectedTypes?: Set<AppType>;
}

const nodeTypes: NodeTypes = {
    appNode: MASGraphNode
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const edgeTypes: Record<string, React.ComponentType<any>> = {
    flowEdge: FlowEdgeComponent
};

const NODE_W = 200;
const NODE_H = 96;

const elk = new ELK();

function buildElkGraph(filteredApps: App[], flowEdges: MASFlowEdge[]) {
    const appIds = new Set(filteredApps.filter((a) => a.id).map((a) => a.id as string));
    const relevantFlows = flowEdges.filter((fe) => appIds.has(fe.caller_app_id) && appIds.has(fe.callee_app_id));

    return {
        id: 'root',
        layoutOptions: {
            'elk.algorithm': 'layered',
            'elk.direction': 'DOWN',
            'elk.alignment': 'CENTER',
            'elk.layered.spacing.nodeNodeBetweenLayers': '160',
            'elk.spacing.nodeNode': '100',
            'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
            'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF',
            'elk.edgeRouting': 'SPLINES',
            'elk.padding': '[top=80, left=80, bottom=80, right=80]',
            'elk.separateConnectedComponents': 'false',
            'elk.layered.spacing.edgeNodeBetweenLayers': '60',
            'elk.layered.spacing.edgeEdgeBetweenLayers': '30'
        },
        children: filteredApps.filter((a) => a.id).map((app) => ({id: `app-${app.id}`, width: NODE_W, height: NODE_H})),
        edges: Array.from(
            new Map(relevantFlows.map((fe) => [`${fe.caller_app_id}-${fe.callee_app_id}`, fe])).values()
        ).map((fe) => ({
            id: `flow-${fe.caller_app_id}-${fe.callee_app_id}`,
            sources: [`app-${fe.caller_app_id}`],
            targets: [`app-${fe.callee_app_id}`]
        }))
    };
}

function MASGraphViewInner({
    mas,
    apps,
    onAppClick,
    searchTerm = '',
    selectedTypes = new Set(['agent', 'client', 'mcp_server'])
}: MASGraphViewProps) {
    const navigate = useNavigate();
    const graphRef = useRef<HTMLDivElement>(null);
    const {data: flowEdges = [], isLoading: isFlowLoading} = useMASFlow(mas.id);
    const [layoutedNodes, setLayoutedNodes, onNodesChange] = useNodesState<Node>([]);
    const {fitView} = useReactFlow();
    const [visibleEdgeTypes, setVisibleEdgeTypes] = useState(new Set(['agent', 'token', 'mcp']));

    const toggleEdgeType = useCallback((type: string) => {
        setVisibleEdgeTypes((prev) => {
            const next = new Set(prev);
            if (next.has(type)) next.delete(type);
            else next.add(type);
            return next;
        });
    }, []);

    const filteredApps = useMemo(() => {
        return apps.filter((app) => {
            const matchesSearch = searchTerm === '' || app.name.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesType = selectedTypes.has(app.type);
            return matchesSearch && matchesType;
        });
    }, [apps, searchTerm, selectedTypes]);

    const maxCallCount = useMemo(() => Math.max(1, ...flowEdges.map((e) => e.call_count)), [flowEdges]);

    useEffect(() => {
        if (filteredApps.length === 0) {
            setLayoutedNodes([]);
            return;
        }

        elk.layout(buildElkGraph(filteredApps, flowEdges))
            .then((laid) => {
                const posMap = new Map<string, {x: number; y: number}>();
                laid.children?.forEach((n) => posMap.set(n.id, {x: n.x ?? 0, y: n.y ?? 0}));

                const appNodes: Node[] = filteredApps
                    .filter((a) => a.id)
                    .map((app) => ({
                        id: `app-${app.id}`,
                        type: 'appNode',
                        position: posMap.get(`app-${app.id}`) ?? {x: 0, y: 0},
                        data: {
                            name: app.name,
                            type: app.type,
                            toolCount: app.tools?.length || 0,
                            tools: app.tools || [],
                            appId: app.id,
                            isHighlighted:
                                searchTerm !== '' && app.name.toLowerCase().includes(searchTerm.toLowerCase())
                        },
                        className:
                            searchTerm !== '' && app.name.toLowerCase().includes(searchTerm.toLowerCase())
                                ? 'highlighted'
                                : ''
                    }));

                setLayoutedNodes(resolveCollisions(appNodes, {margin: 32, maxIterations: 50}));
                requestAnimationFrame(() => fitView({padding: 0.15, duration: 300}));
            })
            .catch(console.error);
    }, [filteredApps, flowEdges, searchTerm, setLayoutedNodes, fitView]);

    const onNodeDragStop = useCallback(() => {
        setLayoutedNodes((nds) => resolveCollisions(nds, {maxIterations: Infinity, overlapThreshold: 0.5, margin: 15}));
    }, [setLayoutedNodes]);

    const edges = useMemo(() => {
        const appIds = new Set(filteredApps.filter((a) => a.id).map((a) => a.id as string));

        const validEdges = flowEdges.filter((fe) => appIds.has(fe.caller_app_id) && appIds.has(fe.callee_app_id));

        const NODE_WIDTH = 200;

        // Position lookup — used to pick left/right handle for agent edges
        const nodePos = new Map<string, {x: number; y: number}>();
        for (const n of layoutedNodes) {
            nodePos.set((n.id as string).replace('app-', ''), n.position);
        }

        // Separate agent edges — they use left/right handles based on relative position
        const nonAgentEdges = validEdges.filter(
            (fe) => fe.edge_type !== 'agent' && visibleEdgeTypes.has(fe.edge_type ?? 'mcp')
        );
        const agentEdges = validEdges.filter((fe) => fe.edge_type === 'agent' && visibleEdgeTypes.has('agent'));

        // For non-agent edges on the same pair (e.g. token + mcp to same nodes), nudge them apart
        const typesByNonAgentPair = new Map<string, string[]>();
        for (const fe of nonAgentEdges) {
            const key = `${fe.caller_app_id}:${fe.callee_app_id}`;
            if (!typesByNonAgentPair.has(key)) typesByNonAgentPair.set(key, []);
            typesByNonAgentPair.get(key)!.push(fe.edge_type ?? 'mcp');
        }

        const pairsWithAgentEdge = new Set(agentEdges.map((fe) => `${fe.caller_app_id}:${fe.callee_app_id}`));

        const nonAgentObserved: Edge[] = nonAgentEdges.map((fe) => {
            const blockRate = fe.call_count > 0 ? fe.blocked_count / fe.call_count : 0;
            const width = 2 + Math.round((fe.call_count / maxCallCount) * 2);
            const strokeColor = blockRate > 0.5 ? '#f87171' : blockRate > 0 ? '#fb923c' : '#34d399';
            const glowColor =
                blockRate > 0.5
                    ? 'rgba(248,113,113,0.5)'
                    : blockRate > 0
                      ? 'rgba(251,146,60,0.5)'
                      : 'rgba(52,211,153,0.5)';
            const labelText = `${fe.call_count} call${fe.call_count !== 1 ? 's' : ''}${fe.blocked_count > 0 ? ` · ${fe.blocked_count} blocked` : ''}`;

            const pairKey = `${fe.caller_app_id}:${fe.callee_app_id}`;
            const siblings = typesByNonAgentPair.get(pairKey) ?? [fe.edge_type ?? 'mcp'];
            const idx = siblings.indexOf(fe.edge_type ?? 'mcp');
            const nudge = siblings.length > 1 ? (idx - (siblings.length - 1) / 2) * 18 : 0;

            // Stagger label positions along the edge so multiple labels don't overlap
            const baseT = pairsWithAgentEdge.has(pairKey) ? 0.75 : 0.5;
            const labelT = siblings.length > 1 ? baseT + (idx - (siblings.length - 1) / 2) * 0.15 : baseT;

            return {
                id: `flow-${fe.edge_type ?? 'mcp'}-${fe.caller_app_id}-${fe.callee_app_id}`,
                source: `app-${fe.caller_app_id}`,
                sourceHandle: 'bottom',
                target: `app-${fe.callee_app_id}`,
                targetHandle: 'top',
                type: 'flowEdge',
                animated: true,
                data: {
                    label: labelText,
                    curvature: 0.25,
                    sourceXOffset: nudge,
                    targetXOffset: nudge,
                    labelT
                },
                style: {stroke: strokeColor, strokeWidth: width, filter: `drop-shadow(0 0 6px ${glowColor})`}
            };
        });

        const agentObserved: Edge[] = agentEdges.map((fe) => {
            const width = 2 + Math.round((fe.call_count / maxCallCount) * 2);
            const labelText = `${fe.call_count} call${fe.call_count !== 1 ? 's' : ''}`;

            const srcPos = nodePos.get(fe.caller_app_id);
            const tgtPos = nodePos.get(fe.callee_app_id);

            const srcCenterX = (srcPos?.x ?? 0) + NODE_WIDTH / 2;
            const tgtCenterX = (tgtPos?.x ?? 0) + NODE_WIDTH / 2;
            const goRight = tgtCenterX >= srcCenterX;
            const sourceHandle = goRight ? 'right' : 'left';
            const targetHandle = goRight ? 'right-target' : 'left-target';

            return {
                id: `flow-agent-${fe.caller_app_id}-${fe.callee_app_id}`,
                source: `app-${fe.caller_app_id}`,
                sourceHandle,
                target: `app-${fe.callee_app_id}`,
                targetHandle,
                type: 'flowEdge',
                animated: true,
                data: {label: labelText, curvature: 0.35, labelT: 0.5},
                style: {stroke: '#a78bfa', strokeWidth: width, filter: 'drop-shadow(0 0 6px rgba(167,139,250,0.5))'}
            };
        });

        const observedEdges = [...nonAgentObserved, ...agentObserved];

        return observedEdges;
    }, [filteredApps, flowEdges, maxCallCount, visibleEdgeTypes, layoutedNodes]);

    const onNodeClick = useCallback(
        (_event: React.MouseEvent, node: Node) => {
            if (node.type !== 'appNode' || !node.data.appId) return;
            const app = apps.find((a) => a.id === node.data.appId);
            if (!app) return;
            if (onAppClick) onAppClick(app);
            else navigate(`/apps/${app.id}`);
        },
        [apps, onAppClick, navigate]
    );

    const exportToPng = useCallback(() => {
        if (!graphRef.current) return;
        toPng(graphRef.current, {
            backgroundColor: '#04080f',
            width: graphRef.current.offsetWidth,
            height: graphRef.current.offsetHeight
        })
            .then((dataUrl) => {
                const link = document.createElement('a');
                link.download = `${mas.name}-graph.png`;
                link.href = dataUrl;
                link.click();
            })
            .catch(console.error);
    }, [mas.name]);

    if (apps.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-16 gap-4 text-muted-foreground">
                <div
                    className="w-16 h-16 rounded-2xl flex items-center justify-center"
                    style={{background: 'rgba(0,188,235,0.06)', border: '1px solid rgba(0,188,235,0.15)'}}
                >
                    <Network className="h-7 w-7" style={{color: 'rgba(0,188,235,0.4)'}} strokeWidth={1.5} />
                </div>
                <div className="text-center">
                    <p className="text-sm font-medium text-white/60">No agentic services to display</p>
                    <p className="text-xs mt-1 text-white/35">Add agentic services to this MAS to see the graph</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {/* Legend */}
            <div
                className="flex items-center gap-2 text-xs"
                style={{
                    background: 'rgba(4,8,18,0.70)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    borderRadius: 10,
                    padding: '7px 14px',
                    backdropFilter: 'blur(8px)',
                    minWidth: 0
                }}
            >
                {/* Nodes group */}
                <span className="text-[9px] font-bold uppercase tracking-widest text-white/25 shrink-0">Nodes</span>
                <div className="flex items-center gap-1">
                    <div
                        className="w-5 h-5 rounded flex items-center justify-center shrink-0"
                        style={{background: 'rgba(129,140,248,0.12)', border: '1px solid rgba(129,140,248,0.3)'}}
                    >
                        <Bot className="h-3 w-3" style={{color: '#818cf8'}} strokeWidth={1.5} />
                    </div>
                    <span className="text-white/50 text-[11px]">Agent</span>
                </div>
                <div className="flex items-center gap-1">
                    <div
                        className="w-5 h-5 rounded flex items-center justify-center shrink-0"
                        style={{background: 'rgba(96,165,250,0.12)', border: '1px solid rgba(96,165,250,0.3)'}}
                    >
                        <AppWindow className="h-3 w-3" style={{color: '#60a5fa'}} strokeWidth={1.5} />
                    </div>
                    <span className="text-white/50 text-[11px]">Client</span>
                </div>
                <div className="flex items-center gap-1">
                    <div
                        className="w-5 h-5 rounded flex items-center justify-center shrink-0"
                        style={{background: 'rgba(34,211,238,0.12)', border: '1px solid rgba(34,211,238,0.3)'}}
                    >
                        <Server className="h-3 w-3" style={{color: '#22d3ee'}} strokeWidth={1.5} />
                    </div>
                    <span className="text-white/50 text-[11px]">MCP</span>
                </div>

                <div className="w-px h-3.5 bg-white/10 mx-1 shrink-0" />

                {/* Flows legend */}
                <span className="text-[9px] font-bold uppercase tracking-widest text-white/25 shrink-0">Flows</span>
                {[
                    {stroke: '#a78bfa', dash: undefined, label: 'agent→agent'},
                    {stroke: '#34d399', dash: undefined, label: 'allowed'},
                    {stroke: '#fb923c', dash: undefined, label: 'partial block'},
                    {stroke: '#f87171', dash: undefined, label: 'mostly blocked'}
                ].map(({stroke, dash, label}) => (
                    <div key={label} className="flex items-center gap-1 shrink-0">
                        <svg width="16" height="8" className="shrink-0">
                            <line x1="0" y1="4" x2="16" y2="4" stroke={stroke} strokeWidth="2" strokeDasharray={dash} />
                        </svg>
                        <span className="text-white/40 text-[11px]">{label}</span>
                    </div>
                ))}

                <div className="w-px h-3.5 bg-white/10 mx-1 shrink-0" />

                {/* Flow type filters */}
                <span className="text-[9px] font-bold uppercase tracking-widest text-white/25 shrink-0">Show</span>
                {(
                    [
                        {type: 'agent', label: 'Agent→Agent'},
                        {type: 'token', label: 'Token'},
                        {type: 'mcp', label: 'MCP'}
                    ] as const
                ).map(({type, label}) => {
                    const active = visibleEdgeTypes.has(type);
                    return (
                        <button
                            key={type}
                            type="button"
                            onClick={() => toggleEdgeType(type)}
                            className="shrink-0 cursor-pointer transition-all rounded-md px-2.5 py-1"
                            style={{
                                border: `1px solid ${active ? 'rgba(255,255,255,0.18)' : 'rgba(255,255,255,0.06)'}`,
                                background: active ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.02)',
                                color: active ? 'rgba(255,255,255,0.75)' : 'rgba(255,255,255,0.22)'
                            }}
                            title={active ? `Hide ${label} flows` : `Show ${label} flows`}
                        >
                            <span className="text-[11px] font-medium">{label}</span>
                        </button>
                    );
                })}

                <Button
                    variant="outline"
                    size="sm"
                    onClick={exportToPng}
                    className="cursor-pointer ml-auto text-white/50 border-white/10 hover:border-white/20 hover:text-white/80"
                >
                    <Download className="mr-1.5 h-3 w-3" />
                    Export PNG
                </Button>
            </div>

            {/* Graph */}
            <div
                ref={graphRef}
                className="relative w-full rounded-xl overflow-hidden"
                style={{
                    height: 820,
                    background:
                        'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(0,30,70,0.35) 0%, rgba(4,8,18,0.95) 70%)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    boxShadow: 'inset 0 0 80px rgba(0,0,0,0.4)'
                }}
            >
                <ReactFlow
                    nodes={layoutedNodes}
                    edges={edges}
                    nodeTypes={nodeTypes}
                    edgeTypes={edgeTypes}
                    onNodesChange={onNodesChange}
                    onNodeClick={onNodeClick}
                    onNodeDragStop={onNodeDragStop}
                    minZoom={0.2}
                    maxZoom={2.5}
                    connectionMode={ConnectionMode.Loose}
                    defaultEdgeOptions={{type: 'bezier', animated: false}}
                >
                    <Background variant={BackgroundVariant.Dots} gap={28} size={1} color="rgba(255,255,255,0.06)" />
                    <Controls
                        className="!bottom-4 !left-4"
                        style={{
                            background: 'rgba(4,8,18,0.9)',
                            border: '1px solid rgba(255,255,255,0.08)',
                            borderRadius: 10,
                            overflow: 'hidden'
                        }}
                    />
                    <MiniMap
                        nodeColor={(node) => {
                            const type = node.data?.type as AppType | undefined;
                            if (type === 'agent') return '#818cf8';
                            if (type === 'client') return '#34d399';
                            if (type === 'mcp_server') return '#22d3ee';
                            return '#4b5563';
                        }}
                        maskColor="rgba(0,0,0,0.55)"
                        style={{
                            background: 'rgba(4,8,18,0.90)',
                            border: '1px solid rgba(255,255,255,0.08)',
                            borderRadius: 10
                        }}
                    />
                    <Panel
                        position="top-right"
                        style={{
                            background: 'rgba(4,8,18,0.80)',
                            backdropFilter: 'blur(8px)',
                            border: '1px solid rgba(255,255,255,0.07)',
                            borderRadius: 8,
                            padding: '6px 12px',
                            marginTop: 8,
                            marginRight: 8
                        }}
                    >
                        <div className="text-[11px] text-white/40">
                            Showing <span className="text-white/70 font-medium">{filteredApps.length}</span> of{' '}
                            <span className="text-white/70 font-medium">{apps.length}</span> services
                        </div>
                    </Panel>
                </ReactFlow>
                {(isFlowLoading || (filteredApps.length > 0 && layoutedNodes.length === 0)) && (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div className="flex flex-col items-center gap-3">
                            <div
                                className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
                                style={{borderColor: 'rgba(0,188,235,0.6)', borderTopColor: 'transparent'}}
                            />
                            <span className="text-xs text-white/30 tracking-widest uppercase">Computing layout</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export function MASGraphView(props: MASGraphViewProps) {
    return (
        <ReactFlowProvider>
            <MASGraphViewInner {...props} />
        </ReactFlowProvider>
    );
}

export type {MASGraphViewProps};
