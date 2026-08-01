"""The integration roundtrip harnesses start and speak MCP — checked offline.

``tests/integration/_mcp_roundtrip_server{,_b}.py`` are real MCP servers built on
the real ``mcp`` package, spawned as stdio subprocesses. Until now they were only
ever exercised by the ``kafka`` lane, which needs Docker — so an mcp upgrade that
broke them was invisible until CI, and even there it surfaced only as
``MCPError: Connection closed``, with the real cause (an ImportError at module
scope) buried in the subprocess's stderr. That is exactly how the mcp 2.0 removal
of ``mcp.server.fastmcp`` reached CI.

Nothing about these servers actually needs a broker: they are subprocesses over
stdio. Handshaking with them directly costs a fraction of a second and needs no
Docker, network, or credentials. The failure still surfaces as ``Connection
closed`` — that is what a dead subprocess looks like from the client — but the
subprocess's traceback lands in the captured output alongside it, so the real
cause is right there. These tests therefore live in the default lane,
deliberately unmarked.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

_HARNESS_DIR = Path(__file__).parent / "integration"


async def _list_and_call(harness: str, tool: str, args: dict[str, object]) -> tuple[set[str], str]:
    """Spawn ``harness`` over stdio, complete a handshake, and call one tool.

    Returns the advertised tool names and the called tool's text result.
    """
    params = StdioServerParameters(command=sys.executable, args=[str(_HARNESS_DIR / harness)])
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            names = {tool_def.name for tool_def in (await session.list_tools()).tools}
            result = await session.call_tool(tool, args)
            return names, result.content[0].text  # type: ignore[union-attr]


@pytest.mark.parametrize(
    ("harness", "expected_tools", "tool", "args", "expected"),
    [
        pytest.param(
            "_mcp_roundtrip_server.py",
            {"add", "echo", "ping", "danger", "domain_error", "enable_bonus"},
            "add",
            {"a": 2, "b": 3},
            "5",
            id="server-a",
        ),
        pytest.param(
            "_mcp_roundtrip_server_b.py",
            {"mul", "upper"},
            "mul",
            {"a": 4, "b": 5},
            "20",
            id="server-b",
        ),
    ],
)
async def test_harness_starts_and_advertises_its_tools(
    harness: str, expected_tools: set[str], tool: str, args: dict[str, object], expected: str
) -> None:
    """The harness imports, completes an MCP handshake, and dispatches a call.

    Asserting the full advertised set — not just a subset — means a tool silently
    dropped by an upstream decorator change fails here too, not only a server that
    refuses to start.
    """
    names, result = await _list_and_call(harness, tool, args)

    assert names == expected_tools
    assert result == expected
