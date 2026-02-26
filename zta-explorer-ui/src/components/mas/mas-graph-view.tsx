import {useMemo, useCallback} from 'react';
import {useNavigate} from 'react-router-dom';
import ReactFlow, {Node, Edge, Controls, Background, BackgroundVariant, ConnectionMode, NodeTypes} from 'reactflow';
import 'reactflow/dist/style.css';
import {MASGraphMASNode} from './mas-graph-mas-node';
import {MASGraphNode} from './mas-graph-node';
import type {MAS} from '@/types/mas.types';
import type {App} from '@/types/app.types';

interface MASGraphViewProps {
    mas: MAS;
    apps: App[];
}

const nodeTypes: NodeTypes = {
    masNode: MASGraphMASNode,
    appNode: MASGraphNode
};

export function MASGraphView({mas, apps}: MASGraphViewProps) {
    const navigate = useNavigate();

    const {nodes, edges} = useMemo(() => {
        // MAS node at the top center
        const masNode: Node = {
            id: 'mas-center',
            type: 'masNode',
            position: {x: 400, y: 50},
            data: {
                name: mas.name,
                appCount: apps.length
            },
            draggable: false
        };

        // Calculate pyramid layout
        const appNodes: Node[] = apps.map((app, index) => {
            const totalApps = apps.length;

            // Determine number of items per row for pyramid layout
            // Row 1: up to 3 items, Row 2: up to 4 items, Row 3+: remaining items
            let row = 0;
            let posInRow = 0;
            let itemsInRow = 0;

            if (totalApps <= 3) {
                // Single row
                row = 1;
                itemsInRow = totalApps;
                posInRow = index;
            } else if (totalApps <= 7) {
                // Two rows: 3 on top, rest on bottom
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
                // Three or more rows: 3, 4, then rest
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

            // Calculate position
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
                    onClick: () => navigate(`/apps/${app.id}`)
                }
            };
        });

        const appEdges: Edge[] = apps.map((app) => ({
            id: `edge-mas-${app.id}`,
            source: 'mas-center',
            sourceHandle: 'bottom',
            target: `app-${app.id}`,
            targetHandle: 'top',
            type: 'smoothstep',
            animated: false,
            style: {
                stroke: 'oklch(0.648 0.2 131.684)',
                strokeWidth: 2
            }
        }));

        return {
            nodes: [masNode, ...appNodes],
            edges: appEdges
        };
    }, [mas, apps, navigate]);

    const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
        if (node.data.onClick) {
            node.data.onClick();
        }
    }, []);

    if (apps.length === 0) {
        return (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
                <p>No applications to display in graph view</p>
            </div>
        );
    }

    return (
        <div className="w-full h-[600px] border rounded-lg bg-background">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                onNodeClick={onNodeClick}
                fitView
                minZoom={0.5}
                maxZoom={1.5}
                connectionMode={ConnectionMode.Loose}
                defaultEdgeOptions={{
                    type: 'smoothstep',
                    animated: false
                }}
            >
                <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
                <Controls />
            </ReactFlow>
        </div>
    );
}
