"""Build the FastMCP server and register the tool surface."""

import asyncio
import importlib
import os
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.session import ServerSession
from mcp.types import ContentBlock

from src.config import Config
from src.log import get_logger
from src.office import discovery
from src.office.session import get_session
from src.tools import calc, document, impress, writer

log = get_logger(__name__)

INSTRUCTIONS = """Control LibreOffice (Writer, Calc, Impress) over UNO.

Typical flow: create_document or open_document to get a doc_id, edit with the
writer/calc/impress tools, then save_document / export_document. Documents
persist between tool calls until close_document. LibreOffice starts on first use.
"""

# Tool groups, in registration order. Editing one of these files hot-reloads the
# tool surface in debug mode (see _reload_tools).
_TOOL_MODULES = (document, writer, calc, impress)

# Captured by _DevFastMCP on each tool call so the dev watcher (a background task,
# with no request context of its own) can push tools/list_changed to the client.
_active_session: ServerSession | None = None


class _DevFastMCP(FastMCP):
    """FastMCP that remembers the active session, for dev tool-surface reload."""

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> Sequence[ContentBlock] | dict[str, Any]:
        global _active_session
        ctx = self.get_context()
        if ctx.request_context is not None:
            _active_session = ctx.request_context.session
        return await super().call_tool(name, arguments)


def _register_tools(mcp: FastMCP) -> None:
    for module in _TOOL_MODULES:
        module.register(mcp)


async def _reload_tools(mcp: FastMCP) -> None:
    """Re-import the tool modules and re-register them, then tell the client to
    re-fetch. Covers adding/renaming/changing tools in an existing group file; a
    brand-new group file still needs a server restart (it isn't imported here)."""
    for module in _TOOL_MODULES:
        importlib.reload(module)
    for name in list(mcp._tool_manager._tools):
        mcp.remove_tool(name)
    _register_tools(mcp)
    count = len(mcp._tool_manager._tools)
    if _active_session is not None:
        try:
            await _active_session.send_tool_list_changed()
            log.info("reloaded tool surface (%d tools); sent tools/list_changed", count)
            return
        except Exception as e:
            log.warning("re-registered tools but could not notify the client: %s", e)
    log.info("reloaded tool surface (%d tools); reconnect to pick it up", count)


async def _watch_and_reload(mcp: FastMCP) -> None:
    """Dev hot-reload. Edits to uno_worker.py restart the UNO worker (live, no
    reconnect); edits to src/tools/* re-register the tool surface and push
    tools/list_changed so the client re-fetches."""
    try:
        from watchfiles import awatch
    except ImportError:
        log.warning(
            "debug mode on but watchfiles is not installed; hot-reload disabled"
        )
        return
    worker_file = os.path.abspath(discovery.worker_script())
    tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
    log.info("dev hot-reload: watching %s and %s", worker_file, tools_dir)
    async for changes in awatch(worker_file, tools_dir):
        paths = {os.path.abspath(p) for _, p in changes}
        try:
            if any(p.endswith("uno_worker.py") for p in paths):
                await get_session().reload_worker()
            if any(f"{os.sep}tools{os.sep}" in p and p.endswith(".py") for p in paths):
                await _reload_tools(mcp)
        except Exception as e:
            log.error("hot-reload failed: %s", e)


def create_server(config: Config | None = None) -> FastMCP:
    config = config or Config()
    log.info("creating server: %s", config)
    # prime the session singleton with this config (started lazily on first tool)
    get_session(config)

    @asynccontextmanager
    async def lifespan(_server: FastMCP) -> AsyncIterator[dict]:
        # Reap soffice + the worker when the client disconnects, so we don't leak
        # LibreOffice instances; in debug mode also run the hot-reload watcher.
        watcher = (
            asyncio.create_task(_watch_and_reload(_server)) if config.debug else None
        )
        try:
            yield {}
        finally:
            if watcher:
                watcher.cancel()
            log.info("server shutting down; tearing down office session")
            await get_session().shutdown()

    cls = _DevFastMCP if config.debug else FastMCP
    mcp = cls("libre-mcp", instructions=INSTRUCTIONS, lifespan=lifespan)
    _register_tools(mcp)
    return mcp
