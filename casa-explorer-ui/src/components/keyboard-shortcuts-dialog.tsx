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

import {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {PATHS} from '@/router/paths';
import {Dialog, DialogContent, DialogHeader, DialogTitle} from '@/components/ui/dialog';
import {Keyboard} from 'lucide-react';

const SHORTCUTS = [
    {keys: ['?'], description: 'Show keyboard shortcuts'},
    {keys: ['⌘B', 'Ctrl+B'], description: 'Toggle sidebar'},
    {keys: ['G', 'D'], description: 'Go to Dashboard'},
    {keys: ['G', 'M'], description: 'Go to Multi-Agent Systems'},
    {keys: ['G', 'A'], description: 'Go to Auth Requests'}
];

export function KeyboardShortcutsDialog() {
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        let pendingG = false;
        let gTimer: ReturnType<typeof setTimeout> | null = null;

        const handler = (e: KeyboardEvent) => {
            const tag = (e.target as HTMLElement).tagName;
            if (['INPUT', 'TEXTAREA'].includes(tag)) return;

            if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                setOpen((v) => !v);
                return;
            }

            if (e.key === 'Escape') {
                setOpen(false);
                return;
            }

            // G-then-X navigation shortcuts
            if (e.key === 'g' && !e.ctrlKey && !e.metaKey) {
                pendingG = true;
                if (gTimer) clearTimeout(gTimer);
                gTimer = setTimeout(() => {
                    pendingG = false;
                }, 1000);
                return;
            }

            if (pendingG) {
                pendingG = false;
                if (gTimer) clearTimeout(gTimer);
                if (e.key === 'd') {
                    navigate(PATHS.dashboard);
                    return;
                }
                if (e.key === 'm') {
                    navigate(PATHS.mas.list);
                    return;
                }
                if (e.key === 'a') {
                    navigate(PATHS.authRequests.list);
                    return;
                }
            }
        };

        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [navigate]);

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogContent className="max-w-sm">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <Keyboard className="h-4 w-4" />
                        Keyboard Shortcuts
                    </DialogTitle>
                </DialogHeader>
                <div className="divide-y">
                    {SHORTCUTS.map((s) => (
                        <div key={s.description} className="flex items-center justify-between py-2">
                            <span className="text-sm text-muted-foreground">{s.description}</span>
                            <div className="flex items-center gap-1">
                                {s.keys.map((k, i) => (
                                    <span key={k} className="flex items-center gap-1">
                                        {i > 0 && <span className="text-xs text-muted-foreground">then</span>}
                                        <kbd className="px-2 py-0.5 rounded bg-muted text-xs font-mono border border-border">
                                            {k}
                                        </kbd>
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </DialogContent>
        </Dialog>
    );
}
