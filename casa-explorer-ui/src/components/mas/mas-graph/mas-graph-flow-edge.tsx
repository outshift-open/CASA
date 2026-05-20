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

import {memo, CSSProperties} from 'react';
import {BaseEdge, EdgeLabelRenderer, getBezierPath, Position} from '@xyflow/react';

interface MASFlowEdgeProps {
    id: string;
    sourceX: number;
    sourceY: number;
    targetX: number;
    targetY: number;
    sourcePosition: Position;
    targetPosition: Position;
    data?: {
        label?: string;
        curvature?: number;
        sourceXOffset?: number;
        targetXOffset?: number;
        customPath?: string;
        labelT?: number;
        labelYOffset?: number;
        sideToTop?: boolean;
    };
    style?: CSSProperties;
    markerEnd?: string;
}

// Cubic bezier: exits horizontally from a left/right handle, enters vertically into a top handle.
function sideToTopPath(
    sx: number,
    sy: number,
    tx: number,
    ty: number,
    sourcePosition: Position
): [string, number, number] {
    const goRight = sourcePosition === Position.Right;
    const dx = Math.abs(tx - sx);
    const dy = Math.abs(ty - sy);
    const hCtrl = Math.max(dx * 0.6, 60) * (goRight ? 1 : -1);
    const vCtrl = Math.max(dy * 0.6, 60);
    const cx1 = sx + hCtrl;
    const cy1 = sy;
    const cx2 = tx;
    const cy2 = ty - vCtrl;
    const path = `M ${sx},${sy} C ${cx1},${cy1} ${cx2},${cy2} ${tx},${ty}`;
    const t = 0.6;
    const lx = Math.pow(1 - t, 3) * sx + 3 * Math.pow(1 - t, 2) * t * cx1 + 3 * (1 - t) * t * t * cx2 + t * t * t * tx;
    const ly = Math.pow(1 - t, 3) * sy + 3 * Math.pow(1 - t, 2) * t * cy1 + 3 * (1 - t) * t * t * cy2 + t * t * t * ty;
    return [path, lx, ly];
}

export const MASFlowEdge = memo(
    ({
        id,
        sourceX,
        sourceY,
        targetX,
        targetY,
        sourcePosition,
        targetPosition,
        data,
        style,
        markerEnd
    }: MASFlowEdgeProps) => {
        let edgePath: string;
        let labelX: number;
        let labelY: number;

        if (data?.sideToTop) {
            [edgePath, labelX, labelY] = sideToTopPath(sourceX, sourceY, targetX, targetY, sourcePosition);
        } else if (data?.customPath) {
            edgePath = data.customPath;
            const t = data.labelT ?? 0.5;
            labelX = sourceX + (targetX - sourceX) * t;
            labelY = sourceY + (targetY - sourceY) * t;
        } else {
            const sx = sourceX + (data?.sourceXOffset ?? 0);
            const tx = targetX + (data?.targetXOffset ?? 0);
            [edgePath, labelX, labelY] = getBezierPath({
                sourceX: sx,
                sourceY,
                sourcePosition,
                targetX: tx,
                targetY,
                targetPosition,
                curvature: data?.curvature
            });
        }

        const strokeColor = (style?.stroke as string) ?? '#34d399';

        return (
            <>
                <BaseEdge id={id} path={edgePath} style={style} markerEnd={markerEnd} />
                {data?.label && (
                    <EdgeLabelRenderer>
                        <div
                            style={{
                                position: 'absolute',
                                transform: `translate(-50%, -50%) translate(${labelX}px,${labelY + (data?.labelYOffset ?? 0)}px)`,
                                pointerEvents: 'all'
                            }}
                            className="nodrag nopan"
                        >
                            <div
                                style={{
                                    background: 'rgba(4,8,18,0.92)',
                                    border: `1px solid ${strokeColor}44`,
                                    borderRadius: 6,
                                    padding: '3px 8px',
                                    fontSize: 11,
                                    fontWeight: 700,
                                    color: strokeColor,
                                    whiteSpace: 'nowrap',
                                    backdropFilter: 'blur(6px)',
                                    boxShadow: `0 0 8px ${strokeColor}33`
                                }}
                            >
                                {data.label}
                            </div>
                        </div>
                    </EdgeLabelRenderer>
                )}
            </>
        );
    }
);

MASFlowEdge.displayName = 'MASFlowEdge';
