"""End-to-end test over the real MCP stdio protocol.

Spawns the server exactly as an MCP host would (initialize → tools/list →
call_tool), covering the FastMCP wiring that the session-level integration tests
bypass. Listing tools runs always; the tool round-trip is skipped when
LibreOffice is unavailable (it would launch soffice).
"""

import json
import os
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.office import discovery

pytestmark = pytest.mark.asyncio

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _server_params() -> StdioServerParameters:
    env = dict(os.environ)
    env.setdefault("LIBRE_MCP_LOG_LEVEL", "WARNING")
    return StdioServerParameters(
        command=sys.executable, args=["-m", "src"], cwd=REPO_ROOT, env=env
    )


def _data(result) -> dict:
    if getattr(result, "structuredContent", None):
        return result.structuredContent
    text = "".join(getattr(b, "text", "") for b in result.content)
    return json.loads(text)


def _have_libreoffice() -> bool:
    try:
        soffice = discovery.find_soffice(None)
        discovery.find_bundled_python(None, soffice)
        return True
    except discovery.DiscoveryError:
        return False


requires_lo = pytest.mark.skipif(
    not _have_libreoffice(), reason="LibreOffice not installed"
)


async def test_lists_tools_over_stdio():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
    # a representative tool from each group must be registered
    assert {"create_document", "insert_text", "set_cells", "add_slide"} <= names


@requires_lo
async def test_tool_roundtrip_over_stdio():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            created = await session.call_tool(
                "create_document", arguments={"kind": "calc"}
            )
            assert not created.isError
            doc_id = _data(created)["doc_id"]

            await session.call_tool(
                "set_cells",
                arguments={
                    "doc_id": doc_id,
                    "cells": [
                        {"cell": "A1", "value": 6},
                        {"cell": "A2", "formula": "=A1*7"},
                    ],
                },
            )
            result = await session.call_tool(
                "read_cells", arguments={"doc_id": doc_id, "range": "A2:A2"}
            )
            assert _data(result)["values"][0][0] == 42.0
