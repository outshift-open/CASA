# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tracer repository implementation."""

from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Integer, String, case, literal, union_all
from sqlalchemy import cast as sa_cast
from sqlmodel import JSON, Column, Field, Session, SQLModel, asc, desc, func, select

from casa_auth_server.core.events import (
    BaseEvent,
    MCPCallStartedEvent,
    MCPToolBlockingType,
    TokenExchangedEvent,
    TokenIssuedEvent,
)
from casa_auth_server.core.types import MultiAgentSystem


class Trace(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel for storing event traces."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_input_id: UUID | None = Field(foreign_key="userinput.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    event_type: str
    event: dict[str, Any] = Field(sa_column=Column(JSON))


class TraceList(BaseModel):
    """Paginated list of events."""

    items: dict[str, list[Trace]]
    total: int
    page: int
    page_size: int


class BlockReasonStat(BaseModel):
    """Count of denied MCP calls for a specific blocking reason."""

    reason: str
    count: int


class MASTraceStat(BaseModel):
    """Aggregated trace counts for a single MAS."""

    mas_id: str
    traces: int
    allowed: int
    denied: int


class MASFlowEdge(BaseModel):
    """Observed caller→callee MCP call counts for a MAS."""

    caller_app_id: str
    callee_app_id: str
    call_count: int
    blocked_count: int


class MetricsSnapshot(BaseModel):
    """Pre-aggregated metrics snapshot."""

    total_mas: int
    token_requests: int
    mcp_calls_allowed: int
    mcp_calls_denied: int
    total_mcp_calls: int
    deterministic_blocks: int
    ai_powered_blocks: int
    block_reasons: list[BlockReasonStat]


class TracerRepository(ABC):
    """Interface exposing the methods of TracerRepository."""

    @abstractmethod
    def store_event(self, event):
        """Stores an event in the database."""

    @abstractmethod
    def get_all(
        self,
        page: int,
        page_size: int,
        mas_id: UUID | None = None,
        fetch_all: bool = False,
        sort_asc: bool = False,
        user_input_id: UUID | None = None,
        blocked: bool | None = None,
        q: str | None = None,
        event_type: str | None = None,
        blocking_type: str | None = None,
    ) -> TraceList:
        """Retrieve traces for all source app calls using pagination."""
        pass

    @abstractmethod
    def get_session(self, user_input_id: UUID) -> list[Trace]:
        """Retrieve all traces for a single session, ordered by creation time ascending."""
        pass

    @abstractmethod
    def get_traces_by_user_input_and_event_type(self, user_input_id: str, event_type: str) -> list[Trace]:
        """Retrieve traces for a specific user input and event type."""
        pass

    @abstractmethod
    def get_metrics(self, total_mas: int) -> MetricsSnapshot:
        """Return pre-aggregated metrics snapshot."""
        pass

    @abstractmethod
    def get_mas_trace_counts(self, mas_ids: list[str]) -> list[MASTraceStat]:
        """Return trace/allowed/denied counts for each of the given MAS IDs in one query."""
        pass

    @abstractmethod
    def get_mas_flow_edges(self, mas_id: str) -> list[MASFlowEdge]:
        """Return aggregated caller→callee MCP call edges observed for a MAS."""
        pass


class TracerPostgresRepository(TracerRepository):
    """Postgre implementation of TracerRepository."""

    def __init__(self, session: Session):
        """Initialize the tracer repository.

        Args:
            session: SQLModel database session.
        """
        self._session = session

    def _active_mas_ids(self) -> list[str]:
        """Return IDs of non-deleted MAS as strings."""
        rows = self._session.exec(select(MultiAgentSystem.id).where(MultiAgentSystem.deleted_at.is_(None))).all()  # type: ignore[union-attr]
        return [str(r) for r in rows]

    def store_event(self, event: BaseEvent):
        """Stores an event in the database."""
        trace = Trace(
            id=event.id,
            user_input_id=UUID(event.user_input_id),
            created_at=event.created_at,
            event_type=type(event).__name__,
            event=event.model_dump(mode="json"),
        )
        self._session.add(trace)

    def get_all(
        self,
        page: int = 0,
        page_size: int = 100,
        mas_id: UUID | None = None,
        fetch_all: bool = False,
        sort_asc: bool = False,
        user_input_id: UUID | None = None,
        blocked: bool | None = None,
        q: str | None = None,
        event_type: str | None = None,
        blocking_type: str | None = None,
    ) -> TraceList:
        """Retrieve traces for all source app calls using pagination."""
        order_fn = asc if sort_asc else desc
        active_ids = self._active_mas_ids()

        if user_input_id is not None:
            # Single-session fetch — bypass pagination, return all events for that session.
            traces = self._session.exec(
                select(Trace).where(Trace.user_input_id == user_input_id).order_by(asc(Trace.created_at))
            ).all()
            items: dict[str, list[Trace]] = defaultdict(list)
            for trace in traces:
                items[str(trace.user_input_id)].append(trace)
            return TraceList(items=items, total=len(traces), page=page, page_size=page_size)

        if mas_id is not None:
            if str(mas_id) not in active_ids:
                return TraceList(items={}, total=0, page=page, page_size=page_size)
            mas_filter = Trace.event["mas_id"].as_string() == str(mas_id)  # type: ignore[assignment]
        else:
            mas_filter = Trace.event["mas_id"].as_string().in_(active_ids)  # type: ignore[assignment]

        filters = [mas_filter]
        if blocked is not None:
            filters.append(Trace.event["blocked"].as_boolean() == blocked)  # type: ignore[arg-type]
        if q is not None:
            # Only MCPCallStarted events carry a "tool" field; restrict q to that event type
            # to avoid silently excluding all other event types whose "tool" field is null.
            filters.append(Trace.event_type == MCPCallStartedEvent.__name__)
            filters.append(Trace.event["tool"].as_string().ilike(f"%{q}%"))  # type: ignore[arg-type]
        if event_type is not None:
            filters.append(Trace.event_type == event_type)
        if blocking_type is not None:
            filters.append(Trace.event["blocking_type"].as_string() == blocking_type)  # type: ignore[arg-type]

        # When row-level filters are active, skip session-grouping and page rows directly.
        if blocked is not None or q is not None or event_type is not None or blocking_type is not None:
            base_qry = select(Trace).where(*filters)
            total_qry = select(func.count()).select_from(base_qry.subquery())
            total = self._session.exec(total_qry).one()
            if not fetch_all:
                base_qry = base_qry.order_by(order_fn(Trace.created_at)).offset((page - 1) * page_size).limit(page_size)
            else:
                base_qry = base_qry.order_by(order_fn(Trace.created_at))
            traces = self._session.exec(base_qry).all()
            result: dict[str, list[Trace]] = defaultdict(list)
            for trace in traces:
                result[str(trace.user_input_id)].append(trace)
            return TraceList(items=result, total=total, page=page, page_size=page_size)

        group_by_qry = (
            select(Trace.user_input_id, func.max(Trace.created_at).label("created_at"))
            .where(*filters)
            .group_by(Trace.user_input_id)
            .subquery()
        )
        paginated_qry = select(group_by_qry.c.user_input_id).order_by(order_fn(group_by_qry.c.created_at))
        if not fetch_all:
            paginated_qry = paginated_qry.offset((page - 1) * page_size).limit(page_size)
        total_qry = select(func.count()).select_from(group_by_qry)
        traces_qry = select(Trace).filter(Trace.user_input_id.in_(paginated_qry)).order_by(desc(Trace.created_at))  # type: ignore[union-attr]
        traces = self._session.exec(traces_qry).all()
        total = self._session.exec(total_qry).one()

        grouped: dict[str, list[Trace]] = defaultdict(list)
        for trace in traces:
            grouped[str(trace.user_input_id)].append(trace)

        for uid in grouped:
            grouped[uid].sort(key=lambda t: t.created_at)

        return TraceList(items=grouped, total=total, page=page, page_size=page_size)

    def get_session(self, user_input_id: UUID) -> list[Trace]:
        """Retrieve all traces for a single session, ordered by creation time ascending."""
        return list(
            self._session.exec(
                select(Trace).where(Trace.user_input_id == user_input_id).order_by(asc(Trace.created_at))
            ).all()
        )

    def get_traces_by_user_input_and_event_type(self, user_input_id: str, event_type: str) -> list[Trace]:
        """Retrieve traces for a specific user input and event type."""
        traces = self._session.exec(
            select(Trace).where(Trace.user_input_id == UUID(user_input_id)).where(Trace.event_type == event_type)
        ).all()
        return traces

    def get_metrics(self, total_mas: int) -> MetricsSnapshot:
        """Return pre-aggregated metrics snapshot."""
        active_ids = self._active_mas_ids()
        rows = self._session.exec(
            select(
                Trace.event_type,
                Trace.event["blocked"].as_boolean(),
                Trace.event["blocking_type"].as_string(),
                Trace.event["blocking_reason"].as_string(),
                func.count().label("cnt"),
            )
            .where(Trace.event["mas_id"].as_string().in_(active_ids))
            .group_by(
                Trace.event_type,
                Trace.event["blocked"].as_boolean(),
                Trace.event["blocking_type"].as_string(),
                Trace.event["blocking_reason"].as_string(),
            )
        ).all()

        token_requests = 0
        mcp_allowed = 0
        mcp_denied = 0
        deterministic_blocks = 0
        ai_powered_blocks = 0
        reason_counts: dict[str, int] = {}

        for event_type, blocked, blocking_type, blocking_reason, cnt in rows:
            if event_type == TokenIssuedEvent.__name__:
                token_requests += cnt
            elif event_type == MCPCallStartedEvent.__name__:
                if blocked:
                    mcp_denied += cnt
                    if blocking_type == MCPToolBlockingType.DETERMINISTIC:
                        deterministic_blocks += cnt
                    elif blocking_type == MCPToolBlockingType.AI_POWERED:
                        ai_powered_blocks += cnt
                    if blocking_reason:
                        reason_counts[blocking_reason] = reason_counts.get(blocking_reason, 0) + cnt
                else:
                    mcp_allowed += cnt

        block_reasons = sorted(
            [BlockReasonStat(reason=r, count=c) for r, c in reason_counts.items()],
            key=lambda x: x.count,
            reverse=True,
        )

        return MetricsSnapshot(
            total_mas=total_mas,
            token_requests=token_requests,
            mcp_calls_allowed=mcp_allowed,
            mcp_calls_denied=mcp_denied,
            total_mcp_calls=mcp_allowed + mcp_denied,
            deterministic_blocks=deterministic_blocks,
            ai_powered_blocks=ai_powered_blocks,
            block_reasons=block_reasons,
        )

    def get_mas_trace_counts(self, mas_ids: list[str]) -> list[MASTraceStat]:
        """Return trace/allowed/denied counts for each of the given MAS IDs in one query."""
        if not mas_ids:
            return []

        session_rows = self._session.exec(
            select(
                Trace.event["mas_id"].as_string().label("mas_id"),
                func.count(func.distinct(Trace.user_input_id)).label("session_count"),
            )
            .where(Trace.event["mas_id"].as_string().in_(mas_ids))
            .group_by(Trace.event["mas_id"].as_string())
        ).all()

        mcp_rows = self._session.exec(
            select(
                Trace.event["mas_id"].as_string().label("mas_id"),
                Trace.event["blocked"].as_boolean().label("blocked"),
                func.count().label("event_count"),
            )
            .where(
                Trace.event["mas_id"].as_string().in_(mas_ids),
                Trace.event_type == MCPCallStartedEvent.__name__,
            )
            .group_by(
                Trace.event["mas_id"].as_string(),
                Trace.event["blocked"].as_boolean(),
            )
        ).all()

        stats: dict[str, dict[str, int]] = {mid: {"traces": 0, "allowed": 0, "denied": 0} for mid in mas_ids}
        for mas_id, session_count in session_rows:
            if mas_id in stats:
                stats[mas_id]["traces"] = session_count
        for mas_id, blocked, event_count in mcp_rows:
            if mas_id not in stats:
                continue
            if blocked:
                stats[mas_id]["denied"] += event_count
            else:
                stats[mas_id]["allowed"] += event_count

        return [MASTraceStat(mas_id=mid, **counts) for mid, counts in stats.items()]

    def get_mas_flow_edges(self, mas_id: str) -> list[MASFlowEdge]:
        """Return aggregated caller→callee flow edges observed for a MAS.

        Combines MCPCallStartedEvent (caller_app_id/callee_app_id) and
        TokenExchangedEvent (subject_app_id/act_app_id) to build the full
        observed call graph. Blocked counts only apply to MCP calls.
        """
        blocked_col = Trace.event["blocked"].as_boolean()  # type: ignore[assignment]

        mcp_calls = select(
            Trace.event["caller_app_id"].as_string().cast(String).label("caller_app_id"),
            Trace.event["callee_app_id"].as_string().cast(String).label("callee_app_id"),
            sa_cast(case((blocked_col, 1), else_=0), Integer).label("is_blocked"),
        ).where(
            Trace.event_type == MCPCallStartedEvent.__name__,
            Trace.event["mas_id"].as_string() == mas_id,
            Trace.event["caller_app_id"].as_string().isnot(None),
            Trace.event["callee_app_id"].as_string().isnot(None),
        )

        token_exchanges = select(
            Trace.event["subject_app_id"].as_string().cast(String).label("caller_app_id"),
            Trace.event["act_app_id"].as_string().cast(String).label("callee_app_id"),
            literal(0).label("is_blocked"),
        ).where(
            Trace.event_type == TokenExchangedEvent.__name__,
            Trace.event["mas_id"].as_string() == mas_id,
            Trace.event["subject_app_id"].as_string().isnot(None),
            Trace.event["act_app_id"].as_string().isnot(None),
        )

        combined = union_all(mcp_calls, token_exchanges).subquery()

        rows = self._session.execute(
            select(
                combined.c.caller_app_id,
                combined.c.callee_app_id,
                func.count().label("call_count"),
                func.sum(combined.c.is_blocked).label("blocked_count"),
            ).group_by(combined.c.caller_app_id, combined.c.callee_app_id)
        ).all()

        return [
            MASFlowEdge(
                caller_app_id=row.caller_app_id,
                callee_app_id=row.callee_app_id,
                call_count=row.call_count,
                blocked_count=row.blocked_count or 0,
            )
            for row in rows
            if row.caller_app_id and row.callee_app_id
        ]
