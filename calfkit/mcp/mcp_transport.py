from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx2
from mcp.client._transport import TransportStreams
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import MCP_DEFAULT_SSE_READ_TIMEOUT, MCP_DEFAULT_TIMEOUT, create_mcp_http_client
from pydantic import BaseModel, ConfigDict

__all__ = (
    "StdioServerParameters",
    "StreamableHttpParameters",
    "stdio_client",
    "http_client",
)


class StreamableHttpParameters(BaseModel):
    """Parameters for initializing a ``streamable_http_client``."""

    # httpx2.Auth is not a pydantic-native type; allow it as an arbitrary field.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # The endpoint URL.
    url: str

    # Optional headers to include in requests.
    headers: dict[str, Any] | None = None

    # HTTP timeout for regular operations.
    timeout: float = MCP_DEFAULT_TIMEOUT

    # Timeout for SSE read operations.
    sse_read_timeout: float = MCP_DEFAULT_SSE_READ_TIMEOUT

    # Close the client session when the transport closes.
    terminate_on_close: bool = True

    auth: httpx2.Auth | None = None


# ``TransportStreams`` is mcp's own name for the (read, write) pair both
# transports produce for a ``ClientSession``. mcp 2.0 offers no public path to
# it: ``mcp.client._transport`` is the definition site and does name it in
# ``__all__``, while every re-export — ``mcp.client.session``,
# ``mcp.client.streamable_http`` — is implicit and so rejected under mypy
# strict. Upstream carries a TODO to relocate it. Importing the canonical site
# beats re-declaring the tuple, whose element types are themselves private, or
# silencing the type checker.


@asynccontextmanager
async def http_client(server: StreamableHttpParameters) -> AsyncIterator[TransportStreams]:
    """Connect to a Streamable HTTP MCP server described by ``server``.

    The HTTP analogue of ``mcp.stdio_client``: pass a config object and get back
    the ``(read_stream, write_stream)`` pair to feed a ``ClientSession``. Unlike
    ``stdio_client``, no subprocess is started — the server must already be
    running at ``server.url``.

    ``streamable_http_client`` also yields a session-id callback as a third
    value; it is dropped here so the yielded shape matches ``stdio_client``.
    """
    # streamable_http_client takes a pre-built httpx client rather than loose
    # headers/timeout, so construct one with the MCP-recommended defaults.
    async with create_mcp_http_client(
        headers=server.headers,
        timeout=httpx2.Timeout(
            server.timeout,
            read=server.sse_read_timeout,
        ),
        auth=server.auth,
    ) as httpx_client:
        async with streamable_http_client(
            server.url,
            http_client=httpx_client,
            terminate_on_close=server.terminate_on_close,
        ) as (read_stream, write_stream, *_):
            yield read_stream, write_stream
