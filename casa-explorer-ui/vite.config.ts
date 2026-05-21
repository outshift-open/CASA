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

import path from 'path';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import {defineConfig} from 'vite';

// https://vite.dev/config/
export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src')
        }
    },
    build: {
        chunkSizeWarningLimit: 1600,
        rollupOptions: {
            output: {
                manualChunks(id) {
                    if (!id.includes('node_modules')) return;
                    if (id.includes('elkjs') || id.includes('@xyflow')) return 'vendor-flow';
                    if (id.includes('recharts') || id.includes('/d3-') || id.includes('/d3/')) return 'vendor-charts';
                    if (id.includes('@dnd-kit')) return 'vendor-dnd';
                    if (id.includes('@tanstack')) return 'vendor-query';
                    if (id.includes('@tabler') || id.includes('lucide-react')) return 'vendor-icons';
                    if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('/zod/')) return 'vendor-forms';
                    if (
                        id.includes('@radix-ui') || id.includes('radix-ui') ||
                        id.includes('/cmdk/') || id.includes('/vaul/')
                    ) return 'vendor-radix';
                    if (id.includes('react-router') || id.includes('react-dom') || id.match(/\/react\//) || id.includes('/sonner/') || id.includes('next-themes')) return 'vendor-react';
                }
            }
        }
    },
    server: {
        port: 1234,
        open: true
    },
    preview: {
        port: 1234
    }
});
