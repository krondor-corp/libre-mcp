"""Build the FastMCP server and register the tool surface."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from src.config import Config
from src.log import get_logger
from src.office import discovery
from src.office.session import get_session
from src.tools import calc, document, impress, writer

log = get_logger(__name__)


async def _watch_and_reload() -> None:
    """Dev hot-reload: restart the UNO worker whenever uno_worker.py changes, so
    edits to document logic take effect on the next tool call — no MCP reconnect.
    (Changes to the tool surface itself still need a reconnect; the tool list is
    sent to the client once at initialize.)"""
    try:
        from watchfiles import awatch
    except ImportError:
        log.warning(
            "debug mode on but watchfiles is not installed; hot-reload disabled"
        )
        return
    target = discovery.worker_script()
    log.info("dev hot-reload: watching %s", target)
    async for _ in awatch(target):
        try:
            await get_session().reload_worker()
        except Exception as e:
            log.error("hot-reload failed: %s", e)


INSTRUCTIONS = """Control LibreOffice (Writer and Calc) over UNO.

Typical flow: create_document or open_document to get a doc_id, edit with the
writer/calc tools, then save_document / export_document. Documents persist
between tool calls until close_document. LibreOffice starts on first use.
"""


def create_server(config: Config | None = None) -> FastMCP:
    config = config or Config()
    log.info("creating server: %s", config)
    # prime the session singleton with this config (started lazily on first tool)
    get_session(config)

    @asynccontextmanager
    async def lifespan(_server: FastMCP) -> AsyncIterator[dict]:
        # Reap soffice + the worker when the client disconnects, so we don't
        # leak LibreOffice instances (important for parallel-worktree dev).
        watcher = asyncio.create_task(_watch_and_reload()) if config.debug else None
        try:
            yield {}
        finally:
            if watcher:
                watcher.cancel()
            log.info("server shutting down; tearing down office session")
            await get_session().shutdown()

    mcp = FastMCP("libre-mcp", instructions=INSTRUCTIONS, lifespan=lifespan)
    document.register(mcp)
    writer.register(mcp)
    calc.register(mcp)
    impress.register(mcp)
    return mcp
