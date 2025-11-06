"""Unit tests for TracePostgresRepository."""

import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.source_app_call.types import SourceAppCall
from identity_auth_server.core.trace.postgres.repository import TracePostgresRepository
from identity_auth_server.core.trace.types import Trace


def _mock_database_with_session():
    session = MagicMock()

    def context_factory():
        context_manager = MagicMock()
        context_manager.__enter__.return_value = session
        context_manager.__exit__.return_value = None
        return context_manager

    database = MagicMock()
    database.session_scope.side_effect = context_factory

    return database, session


@pytest.fixture
def database_with_session():
    """Provide a mock PostgresDB and associated session."""
    return _mock_database_with_session()


def _source_model(**overrides):
    defaults = {
        "id": uuid4(),
        "token": "source-token",
        "input": "{}",
        "created_at": datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _source_response_model(source_id, **overrides):
    defaults = {
        "id": uuid4(),
        "source_app_call_id": source_id,
        "token": "source-response-token",
        "output": "{}",
        "created_at": datetime.datetime(2025, 1, 1, 0, 5, tzinfo=datetime.timezone.utc),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _llm_call_model(source_id, **overrides):
    defaults = {
        "id": uuid4(),
        "source_app_call_id": source_id,
        "token": "llm-token",
        "proxy_call_id": f"proxy-{uuid4()}",
        "messages": "[]",
        "tools": "[]",
        "created_at": datetime.datetime(2025, 1, 2, tzinfo=datetime.timezone.utc),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _llm_response_model(llm_call_id, **overrides):
    defaults = {
        "id": uuid4(),
        "llm_app_call_id": llm_call_id,
        "token": "llm-response-token",
        "proxy_call_id": f"proxy-{uuid4()}",
        "message": "{}",
        "tool_calls": "[]",
        "created_at": datetime.datetime(2025, 1, 3, tzinfo=datetime.timezone.utc),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _mcp_tool_call_model(source_id, llm_call_id=None, llm_response_id=None, blocked_by_type_id=None, **overrides):
    defaults = {
        "id": uuid4(),
        "source_app_call_id": source_id,
        "llm_app_call_id": llm_call_id,
        "llm_app_response_id": llm_response_id,
        "token": "tool-token",
        "tool": "{}",
        "blocked": False,
        "blocked_by_type_id": blocked_by_type_id,
        "created_at": datetime.datetime(2025, 1, 4, tzinfo=datetime.timezone.utc),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_get_builds_trace_structure(database_with_session):
    """It should assemble traces with linked LLM calls, responses, and MCP tool calls."""
    database, session = database_with_session
    source = _source_model()
    source_response = _source_response_model(source.id)
    llm_call = _llm_call_model(source.id)
    llm_response = _llm_response_model(llm_call.id, proxy_call_id=llm_call.proxy_call_id)
    blocked_type_id = uuid4()
    mcp_call = _mcp_tool_call_model(
        source.id,
        llm_call_id=llm_call.id,
        llm_response_id=llm_response.id,
        blocked_by_type_id=blocked_type_id,
    )
    blocked_type = SimpleNamespace(id=blocked_type_id, description="Blocked because of guardrails.", type="guardrail")

    source_query = MagicMock()
    source_response_query = MagicMock()
    llm_call_query = MagicMock()
    llm_response_query = MagicMock()
    mcp_query = MagicMock()
    blocked_type_query = MagicMock()

    session.query.side_effect = [
        source_query,
        source_response_query,
        llm_call_query,
        llm_response_query,
        mcp_query,
        blocked_type_query,
    ]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source

    source_response_filtered = MagicMock()
    source_response_query.filter.return_value = source_response_filtered
    source_response_ordered = MagicMock()
    source_response_filtered.order_by.return_value = source_response_ordered
    source_response_ordered.first.return_value = source_response

    llm_filtered = MagicMock()
    llm_call_query.filter.return_value = llm_filtered
    llm_ordered = MagicMock()
    llm_filtered.order_by.return_value = llm_ordered
    llm_ordered.all.return_value = [llm_call]

    response_filtered = MagicMock()
    llm_response_query.filter.return_value = response_filtered
    response_ordered = MagicMock()
    response_filtered.order_by.return_value = response_ordered
    response_ordered.all.return_value = [llm_response]

    mcp_filtered = MagicMock()
    mcp_query.filter.return_value = mcp_filtered
    mcp_ordered = MagicMock()
    mcp_filtered.order_by.return_value = mcp_ordered
    mcp_ordered.all.return_value = [mcp_call]

    blocked_type_filtered = MagicMock()
    blocked_type_query.filter.return_value = blocked_type_filtered
    blocked_type_filtered.all.return_value = [blocked_type]

    repository = TracePostgresRepository(database)

    trace = repository.get(source.id)

    assert trace.source_app_call.id == source.id
    assert trace.source_app_response is not None
    assert trace.source_app_response.id == source_response.id
    assert len(trace.llm_app_calls) == 1
    assert trace.llm_app_calls[0].llm_app_call.id == llm_call.id
    assert trace.llm_app_calls[0].llm_app_response is not None
    assert trace.llm_app_calls[0].llm_app_response.id == llm_response.id
    assert len(trace.mcp_app_tool_calls) == 1
    mcp_trace = trace.mcp_app_tool_calls[0]
    assert mcp_trace.tool_call.id == mcp_call.id
    assert mcp_trace.blocked_by_description == blocked_type.description
    # The trace entry no longer exposes linked LLM or blocked metadata.


def test_get_handles_tool_call_without_llm_references(database_with_session):
    """It should include MCP tool calls even when LLM references are absent."""
    database, session = database_with_session
    source = _source_model()
    source_response = _source_response_model(source.id)
    mcp_call = _mcp_tool_call_model(source.id)

    source_query = MagicMock()
    source_response_query = MagicMock()
    llm_call_query = MagicMock()
    mcp_query = MagicMock()

    # No LLM responses, but we still load the optional source response.
    session.query.side_effect = [source_query, source_response_query, llm_call_query, mcp_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source

    source_response_filtered = MagicMock()
    source_response_query.filter.return_value = source_response_filtered
    source_response_ordered = MagicMock()
    source_response_filtered.order_by.return_value = source_response_ordered
    source_response_ordered.first.return_value = source_response

    llm_filtered = MagicMock()
    llm_call_query.filter.return_value = llm_filtered
    llm_ordered = MagicMock()
    llm_filtered.order_by.return_value = llm_ordered
    llm_ordered.all.return_value = []

    mcp_filtered = MagicMock()
    mcp_query.filter.return_value = mcp_filtered
    mcp_ordered = MagicMock()
    mcp_filtered.order_by.return_value = mcp_ordered
    mcp_ordered.all.return_value = [mcp_call]

    repository = TracePostgresRepository(database)

    trace = repository.get(source.id)

    assert trace.source_app_call.id == source.id
    assert trace.source_app_response is not None
    assert trace.source_app_response.id == source_response.id
    assert trace.llm_app_calls == []
    assert len(trace.mcp_app_tool_calls) == 1
    mcp_trace = trace.mcp_app_tool_calls[0]
    assert mcp_trace.tool_call.id == mcp_call.id


def test_get_all_returns_paginated_results(monkeypatch, database_with_session):
    """It should return paginated traces using provided page data."""
    database, session = database_with_session
    count_query = MagicMock()
    count_query.scalar.return_value = 2

    source_query = MagicMock()
    ordered = MagicMock()
    limited = MagicMock()
    offset = MagicMock()
    source_id_one = uuid4()
    source_id_two = uuid4()
    offset.all.return_value = [SimpleNamespace(id=source_id_one), SimpleNamespace(id=source_id_two)]

    session.query.side_effect = [count_query, source_query]

    source_query.order_by.return_value = ordered
    ordered.limit.return_value = limited
    limited.offset.return_value = offset

    repository = TracePostgresRepository(database)

    traces_created = []

    def fake_build(self, session_arg, model):
        trace_id = model.id
        traces_created.append(trace_id)
        source = SourceAppCall(
            id=trace_id,
            token=f"token-{trace_id}",
            input="{}",
            created_at=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
        )
        return Trace(source_app_call=source, source_app_response=None, llm_app_calls=[], mcp_app_tool_calls=[])

    monkeypatch.setattr(TracePostgresRepository, "_build_trace", fake_build, raising=False)

    result = repository.get_all(page=1, page_size=1)

    assert result.total == 2
    assert result.page == 1
    assert result.page_size == 1
    assert [item.source_app_call.id for item in result.items] == [source_id_one, source_id_two]
    assert traces_created == [source_id_one, source_id_two]


def test_get_raises_when_source_missing(database_with_session):
    """It should raise ValueError when the source app call cannot be found."""
    database, session = database_with_session
    source_query = MagicMock()
    session.query.side_effect = [source_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = None

    repository = TracePostgresRepository(database)

    with pytest.raises(ResourceNotFoundError, match="Source app call not found"):
        repository.get(uuid4())
