"""SDK-facing type aliases that mirror the server's domain models."""

from identity_auth_server.core.llm_app_call.types import (
    LlmAppCall as _LlmAppCall,
)
from identity_auth_server.core.llm_app_call.types import (
    LlmAppCallInput as _LlmAppCallInput,
)
from identity_auth_server.core.llm_app_response.types import (
    LlmAppResponse as _LlmAppResponse,
)
from identity_auth_server.core.llm_app_response.types import (
    LlmAppResponseInput as _LlmAppResponseInput,
)
from identity_auth_server.core.mcp_app_tool_call.types import (
    McpAppToolCall as _McpAppToolCall,
)
from identity_auth_server.core.mcp_app_tool_call.types import (
    McpAppToolCallInput as _McpAppToolCallInput,
)
from identity_auth_server.core.session.types import (
    SessionLlmAppInput as _SessionLlmAppInput,
)
from identity_auth_server.core.session.types import (
    SessionLlmAppOutput as _SessionLlmAppOutput,
)
from identity_auth_server.core.session.types import (
    SessionMcpAppInput as _SessionMcpAppInput,
)
from identity_auth_server.core.session.types import (
    SessionMcpAppOutput as _SessionMcpAppOutput,
)
from identity_auth_server.core.session.types import (
    SessionSourceAppInput as _SessionSourceAppInput,
)
from identity_auth_server.core.session.types import (
    SessionSourceAppOutput as _SessionSourceAppOutput,
)
from identity_auth_server.core.source_app_call.types import (
    SourceAppCall as _SourceAppCall,
)
from identity_auth_server.core.source_app_call.types import (
    SourceAppCallInput as _SourceAppCallInput,
)
from identity_auth_server.core.source_app_response.types import (
    SourceAppResponse as _SourceAppResponse,
)
from identity_auth_server.core.source_app_response.types import (
    SourceAppResponseInput as _SourceAppResponseInput,
)
from identity_auth_server.core.trace.types import Trace as _Trace
from identity_auth_server.core.trace.types import TraceList as _TraceList
from identity_auth_server.types import McpServer as _McpServer

# Re-export the core models so SDK consumers can import them from a single namespace.
SourceAppCallInput = _SourceAppCallInput
SourceAppCall = _SourceAppCall
SourceAppResponseInput = _SourceAppResponseInput
SourceAppResponse = _SourceAppResponse
LlmAppCallInput = _LlmAppCallInput
LlmAppCall = _LlmAppCall
LlmAppResponseInput = _LlmAppResponseInput
LlmAppResponse = _LlmAppResponse
McpAppToolCallInput = _McpAppToolCallInput
McpAppToolCall = _McpAppToolCall
McpServer = _McpServer
SessionSourceAppInput = _SessionSourceAppInput
SessionSourceAppOutput = _SessionSourceAppOutput
SessionLlmAppInput = _SessionLlmAppInput
SessionLlmAppOutput = _SessionLlmAppOutput
SessionMcpAppInput = _SessionMcpAppInput
SessionMcpAppOutput = _SessionMcpAppOutput
Trace = _Trace
TraceList = _TraceList

__all__ = [
    "LlmAppCall",
    "LlmAppCallInput",
    "LlmAppResponse",
    "LlmAppResponseInput",
    "McpAppToolCall",
    "McpAppToolCallInput",
    "McpServer",
    "SessionLlmAppInput",
    "SessionLlmAppOutput",
    "SessionMcpAppInput",
    "SessionMcpAppOutput",
    "SessionSourceAppInput",
    "SessionSourceAppOutput",
    "SourceAppCall",
    "SourceAppCallInput",
    "SourceAppResponse",
    "SourceAppResponseInput",
    "Trace",
    "TraceList",
]
