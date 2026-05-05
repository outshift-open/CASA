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

import {useMemo, useCallback, useRef} from 'react';
import {useNavigate} from 'react-router-dom';
import ReactFlow, {
    Node,
    Edge,
    Controls,
    Background,
    BackgroundVariant,
    ConnectionMode,
    NodeTypes,
    MiniMap,
    Panel,
    ReactFlowProvider
} from 'reactflow';
import 'reactflow/dist/style.css';
import {MASGraphMASNode} from './mas-graph-mas-node';
import {MASGraphNode} from './mas-graph-node';
import {Button} from '@/components/ui/button';
import {AppTypeBadge} from '@/components/ui/app-type-badge';
import {Bot, AppWindow, Server, Download, Network} from 'lucide-react';
import {toPng} from 'html-to-image';
import type {MAS} from '@/types/mas.types';
import type {App, AppType} from '@/types/app.types';

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

const APP_TYPE_ORDER: Record<AppType, number> = {
    agent: 1,
    client: 2,
    mcp_server: 3
};

function MASGraphViewInner({
    mas,
    apps,
    onAppClick,
    searchTerm = '',
    selectedTypes = new Set(['agent', 'client', 'mcp_server'])
}: MASGraphViewProps) {
    const navigate = useNavigate();
    const graphRef = useRef<HTMLDivElement>(null);

    // Filter apps based on search and selected types
    const filteredApps = useMemo(() => {
        return apps.filter((app) => {
            const matchesSearch = searchTerm === '' || app.name.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesType = selectedTypes.has(app.type);
            return matchesSearch && matchesType;
        });
    }, [apps, searchTerm, selectedTypes]);

    const {nodes, edges} = useMemo(() => {
        // MAS node at the top center
        const masNode: Node = {
            id: 'mas-center',
            type: 'masNode',
            position: {x: 400, y: 50},
            data: {
                name: mas.name,
                appCount: filteredApps.length
            },
            draggable: false
        };

        // Group apps by type
        const sortedApps = [...filteredApps].sort((a, b) => {
            const typeOrder = APP_TYPE_ORDER[a.type] - APP_TYPE_ORDER[b.type];
            if (typeOrder !== 0) return typeOrder;
            return a.name.localeCompare(b.name);
        });

        // Calculate pyramid layout with grouped types
        const appNodes: Node[] = sortedApps.map((app, index) => {
            const totalApps = sortedApps.length;
            let row = 0;
            let posInRow = 0;
            let itemsInRow = 0;

            if (totalApps <= 3) {
                row = 1;
                itemsInRow = totalApps;
                posInRow = index;
            } else if (totalApps <= 7) {
                if (index < 3) {
                    row = 1;
                    itemsInRow = 3;
                    posInRow = index;
                } else {
                    row = 2;
                    itemsInRow = totalApps - 3;
                    posInRow = index - 3;
                }
            } else {
                if (index < 3) {
                    row = 1;
                    itemsInRow = 3;
                    posInRow = index;
                } else if (index < 7) {
                    row = 2;
                    itemsInRow = 4;
                    posInRow = index - 3;
                } else {
                    row = 3;
                    itemsInRow = totalApps - 7;
                    posInRow = index - 7;
                }
            }

            const horizontalSpacing = 250;
            const verticalSpacing = 180;
            const rowWidth = (itemsInRow - 1) * horizontalSpacing;
            const startX = 400 - rowWidth / 2;

            const x = startX + posInRow * horizontalSpacing;
            const y = 50 + row * verticalSpacing;

            return {
                id: `app-${app.id}`,
                type: 'appNode',
                position: {x, y},
                data: {
                    name: app.name,
                    type: app.type,
                    toolCount: app.tools?.length || 0,
                    tools: app.tools || [],
                    onClick: () => (onAppClick ? onAppClick(app) : navigate(`/apps/${app.id}`)),
                    isHighlighted: searchTerm !== '' && app.name.toLowerCase().includes(searchTerm.toLowerCase())
                },
                className:
                    searchTerm !== '' && app.name.toLowerCase().includes(searchTerm.toLowerCase()) ? 'highlighted' : ''
            };
        });

        // Create edges with different colors per type and animation
        const appEdges: Edge[] = sortedApps.map((app) => {
            const edgeColor = app.type === 'agent' ? '#3b82f6' : app.type === 'client' ? '#22c55e' : '#a855f7';

            return {
                id: `edge-mas-${app.id}`,
                source: 'mas-center',
                sourceHandle: 'bottom',
                target: `app-${app.id}`,
                targetHandle: 'top',
                type: 'smoothstep',
                animated: true,
                style: {
                    stroke: edgeColor,
                    strokeWidth: 2
                }
            };
        });

        return {
            nodes: [masNode, ...appNodes],
            edges: appEdges
        };
    }, [mas, filteredApps, navigate, searchTerm, onAppClick]);

    const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
        if (node.data.onClick) {
            node.data.onClick();
        }
    }, []);

    const exportToPng = useCallback(() => {
        if (graphRef.current) {
            toPng(graphRef.current, {
                backgroundColor: '#ffffff',
                width: graphRef.current.offsetWidth,
                height: graphRef.current.offsetHeight
            })
                .then((dataUrl: string) => {
                    const link = document.createElement('a');
                    link.download = `${mas.name}-graph.png`;
                    link.href = dataUrl;
                    link.click();
                })
                .catch((error: unknown) => {
                    console.error('Error exporting graph:', error);
                });
        }
    }, [mas.name]);

    if (apps.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted-foreground">
                <Network className="h-10 w-10 opacity-40" />
                <div className="text-center">
                    <p className="text-sm font-medium">No agentic services to display</p>
                    <p className="text-xs mt-1">Add agentic services to this MAS to see the graph</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Legend + Export */}
            <div className="flex items-center gap-4 text-xs text-muted-foreground border rounded-lg p-3 bg-[rgba(255,255,255,0.04)] border-[rgba(255,255,255,0.07)]">
                <span className="font-medium">Legend:</span>
                <div className="flex items-center gap-1">
                    <Bot className="h-3 w-3 text-purple-400" />
                    <AppTypeBadge type="agent" />
                </div>
                <div className="flex items-center gap-1">
                    <AppWindow className="h-3 w-3 text-blue-400" />
                    <AppTypeBadge type="client" />
                </div>
                <div className="flex items-center gap-1">
                    <Server className="h-3 w-3 text-cyan-400" />
                    <AppTypeBadge type="mcp_server" />
                </div>
                <Button variant="outline" size="sm" onClick={exportToPng} className="cursor-pointer ml-auto">
                    <Download className="mr-1 h-3 w-3" />
                    Export PNG
                </Button>
            </div>

            {/* Graph */}
            <div
                ref={graphRef}
                className="w-full h-[600px] border rounded-lg bg-[rgba(5,12,24,0.60)] backdrop-blur-sm border-[rgba(255,255,255,0.07)]"
            >
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    nodeTypes={nodeTypes}
                    onNodeClick={onNodeClick}
                    fitView
                    minZoom={0.3}
                    maxZoom={2}
                    connectionMode={ConnectionMode.Loose}
                    defaultEdgeOptions={{
                        type: 'smoothstep',
                        animated: true
                    }}
                >
                    <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
                    <Controls />
                    <MiniMap
                        nodeColor={(node) => {
                            if (node.type === 'masNode') return '#3b82f6';
                            const type = node.data?.type as AppType | undefined;
                            if (type === 'agent') return '#3b82f6';
                            if (type === 'client') return '#22c55e';
                            if (type === 'mcp_server') return '#a855f7';
                            return '#94a3b8';
                        }}
                        maskColor="rgba(0, 0, 0, 0.1)"
                    />
                    <Panel
                        position="bottom-left"
                        className="bg-[rgba(8,12,22,0.85)] backdrop-blur-sm p-2 rounded-lg text-xs border border-[rgba(255,255,255,0.07)]"
                    >
                        <div className="text-muted-foreground">
                            Showing {filteredApps.length} of {apps.length} agentic services
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
