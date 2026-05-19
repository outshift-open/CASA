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

import React, {useEffect, useCallback, useRef, useMemo} from 'react';
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
    useNodesState
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {MASGraphMASNode} from './mas-graph-mas-node';
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
    masNode: MASGraphMASNode,
    appNode: MASGraphNode
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const edgeTypes: Record<string, React.ComponentType<any>> = {
    flowEdge: FlowEdgeComponent
};

const NODE_W = 200;
const NODE_H = 96;
const MAS_NODE_W = 220;
const MAS_NODE_H = 110;

const elk = new ELK();

function buildElkGraph(filteredApps: App[], flowEdges: MASFlowEdge[]) {
    const appIds = new Set(filteredApps.filter((a) => a.id).map((a) => a.id as string));
    const relevantFlows = flowEdges.filter((fe) => appIds.has(fe.caller_app_id) && appIds.has(fe.callee_app_id));

    const hasIncomingFlow = new Set<string>();
    relevantFlows.forEach((fe) => hasIncomingFlow.add(fe.callee_app_id));

    const flowAppIds = new Set<string>();
    relevantFlows.forEach((fe) => {
        flowAppIds.add(fe.caller_app_id);
        flowAppIds.add(fe.callee_app_id);
    });

    // Apps with no flow at all → connect directly to MAS hub
    const isolatedApps = filteredApps.filter((a) => a.id && !flowAppIds.has(a.id as string));
    // Flow-connected apps with no incoming flow → they are roots, connect to MAS hub
    const flowRoots = filteredApps.filter(
        (a) => a.id && flowAppIds.has(a.id as string) && !hasIncomingFlow.has(a.id as string)
    );
    const masTargets = [...flowRoots, ...isolatedApps];

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
        children: [
            // layerConstraint FIRST pins MAS hub to layer 0, CENTER aligns it to the middle of that layer
            {
                id: 'mas-center',
                width: MAS_NODE_W,
                height: MAS_NODE_H,
                layoutOptions: {
                    'elk.layered.layering.layerConstraint': 'FIRST',
                    'elk.alignment': 'CENTER'
                }
            },
            ...filteredApps.filter((a) => a.id).map((app) => ({id: `app-${app.id}`, width: NODE_W, height: NODE_H}))
        ],
        edges: [
            ...masTargets
                .filter((a) => a.id)
                .map((app) => ({id: `topo-${app.id}`, sources: ['mas-center'], targets: [`app-${app.id}`]})),
            ...relevantFlows.map((fe) => ({
                id: `flow-${fe.caller_app_id}-${fe.callee_app_id}`,
                sources: [`app-${fe.caller_app_id}`],
                targets: [`app-${fe.callee_app_id}`]
            }))
        ]
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
    const {data: flowEdges = []} = useMASFlow(mas.id);
    const [layoutedNodes, setLayoutedNodes, onNodesChange] = useNodesState<Node>([]);

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

                const masPos = posMap.get('mas-center') ?? {x: 0, y: 0};
                const masNode: Node = {
                    id: 'mas-center',
                    type: 'masNode',
                    position: masPos,
                    data: {name: mas.name, appCount: filteredApps.length}
                };

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

                setLayoutedNodes(resolveCollisions([masNode, ...appNodes], {margin: 32, maxIterations: 50}));
            })
            .catch(console.error);
    }, [filteredApps, flowEdges, mas.name, searchTerm, setLayoutedNodes]);

    const onNodeDragStop = useCallback(() => {
        setLayoutedNodes((nds) => resolveCollisions(nds, {maxIterations: Infinity, overlapThreshold: 0.5, margin: 15}));
    }, [setLayoutedNodes]);

    const edges = useMemo(() => {
        const appIds = new Set(filteredApps.filter((a) => a.id).map((a) => a.id as string));

        const topologyEdges: Edge[] = filteredApps
            .filter((a) => a.id)
            .map((app) => ({
                id: `edge-mas-${app.id}`,
                source: 'mas-center',
                sourceHandle: 'bottom',
                target: `app-${app.id}`,
                targetHandle: 'top',
                type: 'bezier',
                animated: false,
                style: {stroke: 'rgba(255,255,255,0.07)', strokeWidth: 1, strokeDasharray: '4 6'}
            }));

        const observedEdges: Edge[] = flowEdges
            .filter((fe) => appIds.has(fe.caller_app_id) && appIds.has(fe.callee_app_id))
            .map((fe) => {
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

                return {
                    id: `flow-${fe.caller_app_id}-${fe.callee_app_id}`,
                    source: `app-${fe.caller_app_id}`,
                    sourceHandle: 'bottom',
                    target: `app-${fe.callee_app_id}`,
                    targetHandle: 'top',
                    type: 'flowEdge',
                    animated: true,
                    data: {label: labelText},
                    style: {stroke: strokeColor, strokeWidth: width, filter: `drop-shadow(0 0 6px ${glowColor})`}
                };
            });

        return [...topologyEdges, ...observedEdges];
    }, [filteredApps, flowEdges, maxCallCount]);

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
                className="flex items-center gap-4 text-xs flex-wrap"
                style={{
                    background: 'rgba(4,8,18,0.70)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    borderRadius: 10,
                    padding: '10px 16px',
                    backdropFilter: 'blur(8px)'
                }}
            >
                <span className="text-[9px] font-bold uppercase tracking-widest text-white/30">Nodes</span>
                <div className="flex items-center gap-1.5">
                    <div
                        className="w-6 h-6 rounded-md flex items-center justify-center"
                        style={{background: 'rgba(129,140,248,0.12)', border: '1px solid rgba(129,140,248,0.3)'}}
                    >
                        <Bot className="h-3.5 w-3.5" style={{color: '#818cf8'}} strokeWidth={1.5} />
                    </div>
                    <span className="text-white/55">Agent</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div
                        className="w-6 h-6 rounded-md flex items-center justify-center"
                        style={{background: 'rgba(52,211,153,0.12)', border: '1px solid rgba(52,211,153,0.3)'}}
                    >
                        <AppWindow className="h-3.5 w-3.5" style={{color: '#34d399'}} strokeWidth={1.5} />
                    </div>
                    <span className="text-white/55">Client</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div
                        className="w-6 h-6 rounded-md flex items-center justify-center"
                        style={{background: 'rgba(34,211,238,0.12)', border: '1px solid rgba(34,211,238,0.3)'}}
                    >
                        <Server className="h-3.5 w-3.5" style={{color: '#22d3ee'}} strokeWidth={1.5} />
                    </div>
                    <span className="text-white/55">MCP Server</span>
                </div>

                <div className="w-px h-4 bg-white/8 mx-1" />

                <span className="text-[9px] font-bold uppercase tracking-widest text-white/30">Flows</span>
                <div className="flex items-center gap-1.5">
                    <svg width="22" height="10">
                        <line
                            x1="0"
                            y1="5"
                            x2="22"
                            y2="5"
                            stroke="rgba(255,255,255,0.18)"
                            strokeWidth="1.5"
                            strokeDasharray="4 3"
                        />
                    </svg>
                    <span className="text-white/40">membership</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <svg width="22" height="10">
                        <line x1="0" y1="5" x2="22" y2="5" stroke="#34d399" strokeWidth="2.5" />
                    </svg>
                    <span style={{color: '#34d399'}}>all allowed</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <svg width="22" height="10">
                        <line x1="0" y1="5" x2="22" y2="5" stroke="#fb923c" strokeWidth="2.5" />
                    </svg>
                    <span style={{color: '#fb923c'}}>some blocked</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <svg width="22" height="10">
                        <line x1="0" y1="5" x2="22" y2="5" stroke="#f87171" strokeWidth="2.5" />
                    </svg>
                    <span style={{color: '#f87171'}}>mostly blocked</span>
                </div>

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
                className="w-full rounded-xl overflow-hidden"
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
                    fitView
                    fitViewOptions={{padding: 0.15}}
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
                            if (node.type === 'masNode') return '#00BCEB';
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
