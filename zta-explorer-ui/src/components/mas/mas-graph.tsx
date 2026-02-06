import {useNavigate} from 'react-router-dom';
import {App} from '@/types/app.types';
import {Network, Bot, User, Database} from 'lucide-react';

interface MASGraphProps {
    masName: string;
    masId: string;
    apps: App[];
}

export function MASGraph({masName, masId: _masId, apps}: MASGraphProps) {
    const navigate = useNavigate();

    // Graph dimensions
    const width = 1000;
    const height = 700;
    const padding = 80;

    // Separate apps by type
    const agents = apps.filter((app) => app.type === 'agent');
    const clients = apps.filter((app) => app.type === 'client');
    const mcpServers = apps.filter((app) => app.type === 'mcp_server');

    // Calculate layout - three columns
    const columnWidth = (width - padding * 2) / 3;
    const startX = padding;

    const getColumnPositions = (items: App[], columnIndex: number) => {
        const x = startX + columnWidth * columnIndex + columnWidth / 2;
        const spacing = Math.min(120, (height - padding * 2) / Math.max(items.length, 1));
        const totalHeight = spacing * (items.length - 1);
        const startY = (height - totalHeight) / 2;

        return items.map((_, index) => ({
            x,
            y: startY + spacing * index
        }));
    };

    const clientPositions = getColumnPositions(clients, 0);
    const agentPositions = getColumnPositions(agents, 1);
    const mcpPositions = getColumnPositions(mcpServers, 2);

    const getAppIcon = (type: string) => {
        switch (type) {
            case 'agent':
                return Bot;
            case 'client':
                return User;
            case 'mcp_server':
                return Database;
            default:
                return Network;
        }
    };

    const getAppColor = (type: string) => {
        switch (type) {
            case 'agent':
                return {
                    bg: 'hsl(var(--primary))',
                    border: 'hsl(var(--primary))',
                    text: 'hsl(var(--primary-foreground))'
                };
            case 'client':
                return {bg: '#3b82f6', border: '#2563eb', text: 'white'};
            case 'mcp_server':
                return {bg: '#8b5cf6', border: '#7c3aed', text: 'white'};
            default:
                return {bg: 'hsl(var(--muted))', border: 'hsl(var(--border))', text: 'hsl(var(--foreground))'};
        }
    };

    const renderNode = (app: App, position: {x: number; y: number}, index: number) => {
        const colors = getAppColor(app.type);
        const Icon = getAppIcon(app.type);
        const nodeWidth = 140;
        const nodeHeight = 80;

        return (
            <g
                key={app.id || index}
                className="cursor-pointer transition-all hover:opacity-90"
                onClick={() => app.id && navigate(`/apps/${app.id}`)}
            >
                {/* Node rectangle with gradient */}
                <defs>
                    <linearGradient id={`grad-${app.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style={{stopColor: colors.bg, stopOpacity: 1}} />
                        <stop offset="100%" style={{stopColor: colors.border, stopOpacity: 1}} />
                    </linearGradient>
                </defs>
                <rect
                    x={position.x - nodeWidth / 2}
                    y={position.y - nodeHeight / 2}
                    width={nodeWidth}
                    height={nodeHeight}
                    rx="8"
                    fill={`url(#grad-${app.id})`}
                    stroke={colors.border}
                    strokeWidth="2"
                    filter="url(#shadow)"
                />

                {/* Icon */}
                <g transform={`translate(${position.x - 12}, ${position.y - 28})`}>
                    <Icon size={24} color={colors.text} strokeWidth={2} />
                </g>

                {/* App name */}
                <text
                    x={position.x}
                    y={position.y + 8}
                    textAnchor="middle"
                    fill={colors.text}
                    fontSize="13"
                    fontWeight="600"
                    className="pointer-events-none select-none"
                >
                    {app.name.length > 14 ? app.name.substring(0, 14) + '...' : app.name}
                </text>

                {/* Type label */}
                <text
                    x={position.x}
                    y={position.y + 24}
                    textAnchor="middle"
                    fill={colors.text}
                    fontSize="10"
                    opacity="0.8"
                    className="pointer-events-none select-none"
                >
                    {app.type === 'mcp_server' ? 'MCP Server' : app.type.charAt(0).toUpperCase() + app.type.slice(1)}
                </text>
            </g>
        );
    };

    if (apps.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-[400px] text-muted-foreground">
                <Network className="h-16 w-16 mb-4 opacity-20" />
                <p className="text-sm">No applications in this MAS</p>
            </div>
        );
    }

    return (
        <div className="w-full flex justify-center overflow-x-auto bg-background rounded-lg">
            <svg
                width={width}
                height={height}
                viewBox={`0 0 ${width} ${height}`}
                className="max-w-full h-auto"
                style={{minHeight: '500px'}}
            >
                {/* Background */}
                <rect width={width} height={height} fill="hsl(var(--card))" />

                {/* Define filters */}
                <defs>
                    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                        <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3" />
                    </filter>
                    <marker
                        id="arrowhead"
                        markerWidth="10"
                        markerHeight="10"
                        refX="9"
                        refY="3"
                        orient="auto"
                        markerUnits="strokeWidth"
                    >
                        <polygon points="0 0, 10 3, 0 6" fill="#64748b" opacity="0.6" />
                    </marker>
                </defs>

                {/* Connection lines from clients to agents */}
                {clients.map((client, clientIndex) => {
                    const clientPos = clientPositions[clientIndex];
                    return agents.map((agent, agentIndex) => {
                        const agentPos = agentPositions[agentIndex];
                        return (
                            <line
                                key={`client-agent-${clientIndex}-${agentIndex}`}
                                x1={clientPos.x + 70}
                                y1={clientPos.y}
                                x2={agentPos.x - 70}
                                y2={agentPos.y}
                                stroke="#64748b"
                                strokeWidth="2"
                                opacity="0.5"
                                markerEnd="url(#arrowhead)"
                            />
                        );
                    });
                })}

                {/* Connection lines from agents to MCP servers */}
                {agents.map((agent, agentIndex) => {
                    const agentPos = agentPositions[agentIndex];
                    return mcpServers.map((mcp, mcpIndex) => {
                        const mcpPos = mcpPositions[mcpIndex];
                        return (
                            <line
                                key={`agent-mcp-${agentIndex}-${mcpIndex}`}
                                x1={agentPos.x + 70}
                                y1={agentPos.y}
                                x2={mcpPos.x - 70}
                                y2={mcpPos.y}
                                stroke="#64748b"
                                strokeWidth="2"
                                opacity="0.5"
                                markerEnd="url(#arrowhead)"
                            />
                        );
                    });
                })}

                {/* Column labels */}
                <text
                    x={startX + columnWidth * 0 + columnWidth / 2}
                    y={40}
                    textAnchor="middle"
                    fill="hsl(var(--card-foreground))"
                    fontSize="16"
                    fontWeight="700"
                >
                    Clients ({clients.length})
                </text>
                <text
                    x={startX + columnWidth * 1 + columnWidth / 2}
                    y={40}
                    textAnchor="middle"
                    fill="hsl(var(--card-foreground))"
                    fontSize="16"
                    fontWeight="700"
                >
                    Agents ({agents.length})
                </text>
                <text
                    x={startX + columnWidth * 2 + columnWidth / 2}
                    y={40}
                    textAnchor="middle"
                    fill="hsl(var(--card-foreground))"
                    fontSize="16"
                    fontWeight="700"
                >
                    MCP Servers ({mcpServers.length})
                </text>

                {/* Render nodes */}
                {clients.map((client, index) => renderNode(client, clientPositions[index], index))}
                {agents.map((agent, index) => renderNode(agent, agentPositions[index], index))}
                {mcpServers.map((mcp, index) => renderNode(mcp, mcpPositions[index], index))}

                {/* MAS name at top */}
                <g>
                    <rect x={width / 2 - 100} y={5} width={200} height={25} rx="12" fill="hsl(var(--primary))" />
                    <text
                        x={width / 2}
                        y={22}
                        textAnchor="middle"
                        fill="hsl(var(--primary-foreground))"
                        fontSize="14"
                        fontWeight="700"
                    >
                        {masName.length > 20 ? masName.substring(0, 20) + '...' : masName}
                    </text>
                </g>
            </svg>
        </div>
    );
}
