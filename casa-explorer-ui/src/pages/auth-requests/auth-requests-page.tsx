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

import {useMemo, useState, useEffect} from 'react';
import {useSearchParams} from 'react-router-dom';
import {useTraces} from '@/hooks/use-traces';
import {BlockingType, EventType} from '@/types/trace.types';
import {useMAS} from '@/hooks/use-mas';
import {Button} from '@/components/ui/button';
import {Alert, AlertTitle} from '@/components/ui/alert';
import {AuthRequestsTable, SessionTraceSheet} from '@/components/auth-requests';
import type {AuthRequest} from '@/components/auth-requests';
import type {AppNames} from '@/components/traces/event-row';
import {toast} from 'sonner';

const DEFAULT_PAGE_SIZE = 10;

export function AuthRequestsPage() {
    const [searchParams, setSearchParams] = useSearchParams();

    const search = searchParams.get('q') ?? '';
    const authFilter = (searchParams.get('auth') ?? 'all') as 'all' | 'allowed' | 'denied';
    const masFilter = searchParams.get('mas') ?? 'all';
    const denyTypeFilter = (searchParams.get('denyType') ?? 'all') as 'all' | BlockingType;
    const fromDashboard = searchParams.get('from') === 'dashboard';
    const page = Math.max(1, parseInt(searchParams.get('page') ?? '1', 10));

    const [debouncedSearch, setDebouncedSearch] = useState(search);
    const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
    const [selectedUserInputId, setSelectedUserInputId] = useState<string | null>(null);
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);

    useEffect(() => {
        const id = setTimeout(() => setDebouncedSearch(search), 300);
        return () => clearTimeout(id);
    }, [search]);

    const setParam = (key: string, value: string | null, resetPage = true) =>
        setSearchParams(
            (p) => {
                const n = new URLSearchParams(p);
                if (value && value !== 'all') n.set(key, value);
                else n.delete(key);
                if (resetPage) n.delete('page');
                return n;
            },
            {replace: true}
        );

    const setPage = (p: number) =>
        setSearchParams(
            (prev) => {
                const n = new URLSearchParams(prev);
                if (p <= 1) n.delete('page');
                else n.set('page', String(p));
                return n;
            },
            {replace: true}
        );

    const blockedParam = authFilter === 'allowed' ? false : authFilter === 'denied' ? true : undefined;

    const {
        data: tracesData,
        isLoading: tracesLoading,
        isFetching,
        refetch
    } = useTraces({
        page,
        pageSize,
        eventType: EventType.MCPCallStarted,
        blocked: blockedParam,
        masId: masFilter !== 'all' ? masFilter : undefined,
        q: debouncedSearch || undefined,
        blockingType: denyTypeFilter !== 'all' ? denyTypeFilter : undefined
    });

    const {data: masData} = useMAS();

    const masMap = useMemo(() => {
        if (!masData) return {} as Record<string, string>;
        return Object.fromEntries((masData.items ?? []).map((m) => [m.id, m.name]));
    }, [masData]);

    const masList = useMemo(() => (masData?.items ?? []).map((m) => ({id: m.id, name: m.name})), [masData]);

    const appNames = useMemo(() => {
        const result: AppNames = {};
        for (const mas of masData?.items ?? []) {
            for (const app of mas.apps ?? []) {
                if (app.id) result[app.id] = {name: app.name, type: app.type};
            }
        }
        return result;
    }, [masData]);

    const rows = useMemo((): AuthRequest[] => {
        if (!tracesData?.items) return [];
        return Object.values(tracesData.items)
            .flat()
            .map((t) => ({
                id: t.id,
                userInputId: t.user_input_id,
                tool: t.event.tool ?? '—',
                callerAppId: t.event.caller_app_id ?? null,
                calleeAppId: t.event.callee_app_id ?? null,
                masId: t.event.mas_id ?? null,
                blocked: t.event.blocked ?? false,
                blockingType: t.event.blocking_type ?? null,
                blockingReason: t.event.blocking_reason ?? null,
                createdAt: t.created_at
            }));
    }, [tracesData]);

    const total = tracesData?.total ?? 0;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    const dashboardFilterLabel = useMemo(() => {
        if (!fromDashboard) return null;
        const parts: string[] = [];
        if (authFilter === 'allowed') parts.push('allowed calls');
        if (authFilter === 'denied') parts.push('denied calls');
        if (denyTypeFilter === BlockingType.Deterministic) parts.push('deterministic denials');
        if (denyTypeFilter === BlockingType.AIPowered) parts.push('semantic denials');
        if (search) parts.push(`"${search}"`);
        return parts.length > 0 ? parts.join(' · ') : 'filtered view';
    }, [fromDashboard, authFilter, denyTypeFilter, search]);

    const handleRefresh = async () => {
        try {
            await refetch();
            toast.success('Auth requests refreshed successfully');
        } catch {
            toast.error('Failed to refresh auth requests');
        }
    };

    const handleRowClick = (row: AuthRequest) => {
        setSelectedUserInputId(row.userInputId);
        setSelectedTraceId(row.id);
    };

    return (
        <div>
            <div className="flex items-center justify-between pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Auth Requests</h1>
                    <p className="text-muted-foreground">MCP auth requests in traces</p>
                </div>
            </div>

            {dashboardFilterLabel && (
                <Alert className="mb-4 flex items-center justify-between py-2">
                    <AlertTitle className="mb-0">
                        Showing <span className="font-semibold">{dashboardFilterLabel}</span>{' '}
                        <span className="text-muted-foreground font-normal">(from dashboard)</span>
                    </AlertTitle>
                    <Button
                        variant="secondary"
                        size="sm"
                        className="shrink-0 cursor-pointer"
                        onClick={() => setSearchParams(new URLSearchParams(), {replace: true})}
                    >
                        Clear dashboard filter
                    </Button>
                </Alert>
            )}

            <AuthRequestsTable
                rows={rows}
                total={total}
                page={page}
                pageSize={pageSize}
                totalPages={totalPages}
                isLoading={tracesLoading}
                isFetching={isFetching}
                search={search}
                authFilter={authFilter}
                masFilter={masFilter}
                denyTypeFilter={denyTypeFilter}
                masList={masList}
                masMap={masMap}
                appNames={appNames}
                selectedUserInputId={selectedUserInputId}
                onRefresh={handleRefresh}
                onSearchChange={(v) => setParam('q', v)}
                onAuthFilterChange={(v) => setParam('auth', v)}
                onMasFilterChange={(v) => setParam('mas', v)}
                onDenyTypeFilterChange={(v) => setParam('denyType', v)}
                onPageChange={setPage}
                onPageSizeChange={(size) => {
                    setPageSize(size);
                    setPage(1);
                }}
                onRowClick={handleRowClick}
            />

            <SessionTraceSheet
                userInputId={selectedUserInputId}
                focusTraceId={selectedTraceId}
                onClose={() => {
                    setSelectedUserInputId(null);
                    setSelectedTraceId(null);
                }}
            />
        </div>
    );
}
