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

import {useState, useMemo, useRef, useEffect} from 'react';
import {useNavigate} from 'react-router-dom';
import {PATHS} from '@/router/paths';
import {Search, Network, Activity, CheckCircle2, XCircle} from 'lucide-react';
import {useMAS} from '@/hooks/use-mas';
import {useTraces} from '@/hooks/use-traces';
import {useApps} from '@/hooks/use-apps';
import {cn} from '@/lib/utils';
import {EventType} from '@/types/trace.types';

export function GlobalSearch() {
    const [query, setQuery] = useState('');
    const [debouncedQuery, setDebouncedQuery] = useState('');
    const [open, setOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const id = setTimeout(() => setDebouncedQuery(query.trim().toLowerCase()), 300);
        return () => clearTimeout(id);
    }, [query]);

    const q = debouncedQuery;

    const {data: masData} = useMAS(q ? {q} : undefined);
    const {data: tracesData} = useTraces({q: q || undefined, pageSize: 5}, false, !!q);
    const {data: appsData} = useApps();

    const appNameMap = useMemo(() => {
        if (!appsData?.items) return {} as Record<string, string>;
        return Object.fromEntries(appsData.items.filter((a) => a.id).map((a) => [a.id!, a.name]));
    }, [appsData]);

    const masResults = useMemo(() => {
        if (!q || !masData) return [];
        return (masData.items ?? []).slice(0, 5);
    }, [q, masData]);

    const authResults = useMemo(() => {
        if (!q || !tracesData?.items) return [];
        const seen = new Set<string>();
        return Object.values(tracesData.items)
            .flat()
            .filter((t) => t.event_type === EventType.MCPCallStarted)
            .filter((t) => {
                if (seen.has(t.user_input_id)) return false;
                seen.add(t.user_input_id);
                return true;
            });
    }, [q, tracesData]);

    const hasResults = masResults.length > 0 || authResults.length > 0;

    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        function handleKeyDown(e: KeyboardEvent) {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                inputRef.current?.focus();
                setOpen(true);
            }
            if (e.key === 'Escape') {
                setOpen(false);
                inputRef.current?.blur();
            }
        }
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, []);

    function handleSelect(path: string) {
        navigate(path);
        setQuery('');
        setOpen(false);
    }

    return (
        <div ref={containerRef} className="relative w-[350px]">
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
                <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    placeholder="Search..."
                    onChange={(e) => {
                        setQuery(e.target.value);
                        setOpen(true);
                    }}
                    onFocus={() => setOpen(true)}
                    className="w-full h-8 pl-8 pr-10 rounded-md bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.08)] text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-[rgba(0,188,235,0.4)] focus:bg-[rgba(255,255,255,0.08)] transition-colors"
                />
                <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-muted-foreground/50 font-mono pointer-events-none">
                    ⌘K
                </kbd>
            </div>

            {open && q && (
                <div className="absolute top-full mt-1.5 left-0 right-0 z-50 rounded-lg border border-[rgba(255,255,255,0.08)] bg-[#0D1829] shadow-xl overflow-hidden">
                    {!hasResults ? (
                        <div className="px-3 py-4 text-sm text-muted-foreground text-center">No results found</div>
                    ) : (
                        <>
                            {masResults.length > 0 && (
                                <div>
                                    <div className="px-3 py-1.5 text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider border-b border-[rgba(255,255,255,0.05)]">
                                        Multi-Agent Systems
                                    </div>
                                    {masResults.map((mas) => (
                                        <button
                                            key={mas.id}
                                            type="button"
                                            onClick={() => handleSelect(PATHS.mas.detail(mas.id))}
                                            className={cn(
                                                'w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left',
                                                'hover:bg-[rgba(255,255,255,0.05)] transition-colors cursor-pointer'
                                            )}
                                        >
                                            <Network className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                                            <span className="truncate">{mas.name}</span>
                                        </button>
                                    ))}
                                </div>
                            )}
                            {authResults.length > 0 && (
                                <div
                                    className={cn(masResults.length > 0 && 'border-t border-[rgba(255,255,255,0.05)]')}
                                >
                                    <div className="px-3 py-1.5 text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider border-b border-[rgba(255,255,255,0.05)]">
                                        Auth Requests
                                    </div>
                                    {authResults.map((trace) => {
                                        const blocked = trace.event.blocked ?? false;
                                        return (
                                            <button
                                                key={trace.id}
                                                type="button"
                                                onClick={() =>
                                                    handleSelect(PATHS.authRequests.detail(trace.user_input_id))
                                                }
                                                className={cn(
                                                    'w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left',
                                                    'hover:bg-[rgba(255,255,255,0.05)] transition-colors cursor-pointer'
                                                )}
                                            >
                                                {blocked ? (
                                                    <XCircle className="h-3.5 w-3.5 text-destructive shrink-0" />
                                                ) : (
                                                    <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
                                                )}
                                                <div className="flex flex-col min-w-0">
                                                    <span className="font-mono text-[12px] truncate">
                                                        {trace.event.tool ?? '—'}
                                                    </span>
                                                    {trace.event.callee_app_id && (
                                                        <span className="text-[11px] text-muted-foreground truncate">
                                                            {appNameMap[trace.event.callee_app_id] ??
                                                                trace.event.callee_app_id}
                                                        </span>
                                                    )}
                                                </div>
                                                <Activity className="h-3 w-3 text-muted-foreground/40 shrink-0 ml-auto" />
                                            </button>
                                        );
                                    })}
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
