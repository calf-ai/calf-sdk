"""`calfkit.mcp.mcp_transport`'s Streamable HTTP client construction.

`http_client` translates a `StreamableHttpParameters` config into the pre-built
HTTP client that `streamable_http_client` requires. The translation is easy to
get silently wrong: the underlying HTTP library's `Timeout` accepts an unknown
object as a scalar default rather than rejecting it, so a mismatched `Timeout`
produces a client whose per-phase timeouts are `Timeout` objects instead of
floats. That configuration is nonsense but constructs cleanly and even reprs
plausibly, so nothing surfaces it until a request actually hangs.

These tests pin the translation by asserting on the constructed client itself.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest

from calfkit.mcp import mcp_transport
from calfkit.mcp.mcp_transport import StreamableHttpParameters


@asynccontextmanager
async def _capturing_streamable_http_client(
    url: str, *, http_client: Any = None, terminate_on_close: bool = True
) -> AsyncIterator[tuple[Any, Any, Any]]:
    """Stand-in for `streamable_http_client` that records what it was handed.

    Records onto the context manager's own attribute store so the test can read
    the client back after the `async with` block has exited.
    """
    _capturing_streamable_http_client.captured = {  # type: ignore[attr-defined]
        "url": url,
        "http_client": http_client,
        "terminate_on_close": terminate_on_close,
    }
    yield ("read", "write", "session_id_callback")


@pytest.fixture
def captured_client(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Run `http_client` against a stubbed transport and return the built HTTP client."""

    async def _run(server: StreamableHttpParameters) -> Any:
        monkeypatch.setattr(mcp_transport, "streamable_http_client", _capturing_streamable_http_client)
        async with mcp_transport.http_client(server):
            pass
        return _capturing_streamable_http_client.captured  # type: ignore[attr-defined]

    return _run


@pytest.mark.asyncio
async def test_timeouts_reach_the_client_as_numbers(captured_client: Any) -> None:
    """`timeout` and `sse_read_timeout` land as real numbers on the built client.

    The regression this guards: passing a `Timeout` from the wrong HTTP library
    is accepted and wrapped as a scalar default, leaving every phase set to a
    nested `Timeout` object. Asserting the numeric values catches that, where
    asserting the client merely constructs would not.
    """
    result = await captured_client(StreamableHttpParameters(url="https://example.test/mcp", timeout=7.5, sse_read_timeout=42.0))
    timeout = result["http_client"].timeout

    assert isinstance(timeout.connect, (int, float)), f"connect timeout is {type(timeout.connect).__name__}, not a number"
    assert isinstance(timeout.read, (int, float)), f"read timeout is {type(timeout.read).__name__}, not a number"

    assert timeout.connect == 7.5
    assert timeout.read == 42.0


@pytest.mark.asyncio
async def test_defaults_are_the_mcp_recommended_values(captured_client: Any) -> None:
    """An otherwise-bare config still yields MCP's recommended timeout defaults."""
    result = await captured_client(StreamableHttpParameters(url="https://example.test/mcp"))
    timeout = result["http_client"].timeout

    assert timeout.connect == mcp_transport.MCP_DEFAULT_TIMEOUT
    assert timeout.read == mcp_transport.MCP_DEFAULT_SSE_READ_TIMEOUT


@pytest.mark.asyncio
async def test_headers_and_terminate_on_close_pass_through(captured_client: Any) -> None:
    """Headers ride on the built client; `terminate_on_close` reaches the transport."""
    result = await captured_client(
        StreamableHttpParameters(url="https://example.test/mcp", headers={"authorization": "Bearer token"}, terminate_on_close=False)
    )

    assert result["http_client"].headers.get("authorization") == "Bearer token"
    assert result["terminate_on_close"] is False
    assert result["url"] == "https://example.test/mcp"
