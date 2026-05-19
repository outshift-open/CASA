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

import type {Node} from '@xyflow/react';

type Box = {
    x: number;
    y: number;
    width: number;
    height: number;
    moved: boolean;
    node: Node;
};

function getBoxes(nodes: Node[], margin = 0): Box[] {
    return nodes.map((node) => ({
        x: node.position.x - margin,
        y: node.position.y - margin,
        width: (node.width ?? 200) + margin * 2,
        height: (node.height ?? 96) + margin * 2,
        moved: false,
        node
    }));
}

export function resolveCollisions(
    nodes: Node[],
    {maxIterations = 50, overlapThreshold = 0.5, margin = 0} = {}
): Node[] {
    const boxes = getBoxes(nodes, margin);

    for (let iter = 0; iter <= maxIterations; iter++) {
        let moved = false;

        for (let i = 0; i < boxes.length; i++) {
            for (let j = i + 1; j < boxes.length; j++) {
                const A = boxes[i];
                const B = boxes[j];

                const centerAX = A.x + A.width * 0.5;
                const centerAY = A.y + A.height * 0.5;
                const centerBX = B.x + B.width * 0.5;
                const centerBY = B.y + B.height * 0.5;

                const dx = centerAX - centerBX;
                const dy = centerAY - centerBY;

                const px = (A.width + B.width) * 0.5 - Math.abs(dx);
                const py = (A.height + B.height) * 0.5 - Math.abs(dy);

                if (px > overlapThreshold && py > overlapThreshold) {
                    A.moved = B.moved = moved = true;
                    if (px < py) {
                        const sx = dx > 0 ? 1 : -1;
                        const move = (px / 2) * sx;
                        A.x += move;
                        B.x -= move;
                    } else {
                        const sy = dy > 0 ? 1 : -1;
                        const move = (py / 2) * sy;
                        A.y += move;
                        B.y -= move;
                    }
                }
            }
        }

        if (!moved) break;
    }

    return boxes.map((box) => (box.moved ? {...box.node, position: {x: box.x + margin, y: box.y + margin}} : box.node));
}
