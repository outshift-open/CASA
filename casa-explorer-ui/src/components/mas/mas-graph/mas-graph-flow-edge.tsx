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
    };
    style?: CSSProperties;
    markerEnd?: string;
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

        if (data?.customPath) {
            edgePath = data.customPath;
            const t = data.labelT ?? 0.5;
            labelX = sourceX + (targetX - sourceX) * t;
            labelY = sourceY + (targetY - sourceY) * t;
        } else {
            [edgePath, labelX, labelY] = getBezierPath({
                sourceX: sourceX + (data?.sourceXOffset ?? 0),
                sourceY,
                sourcePosition,
                targetX: targetX + (data?.targetXOffset ?? 0),
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
                                transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
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
