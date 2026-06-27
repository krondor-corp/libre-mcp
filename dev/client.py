"""Dev client: drive the libre-mcp server over real MCP stdio.

This spawns the server exactly as an MCP host would, runs the initialize
handshake, and lets you call tools. Two modes:

  list                       list the available tools
  run                        read "TOOL {json-args}" lines from stdin and run
                             them in ONE persistent session (so doc_ids survive
                             across calls)

Examples:
  uv run python dev/client.py list

  uv run python dev/client.py run <<'EOF'
  create_document {"kind": "writer"}
  insert_text {"doc_id": "doc-1", "text": "Hello from the dev client"}
  get_text {"doc_id": "doc-1"}
  export_document {"doc_id": "doc-1", "path": "/tmp/libre_demo.pdf"}
  EOF

Because a single `run` invocation keeps one server (and thus one LibreOffice)
alive for the whole batch, the first created document is doc-1, the next doc-2,
and so on.
"""

import asyncio
import json
import os
import shlex
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _server_params() -> StdioServerParameters:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = dict(os.environ)
    env.setdefault("LIBRE_MCP_LOG_LEVEL", "INFO")
    # LIBRE_MCP_SERVER_CMD lets you point at a built binary (e.g. dist/libre-mcp)
    # instead of the source; otherwise run `python -m src` from the repo root.
    override = os.environ.get("LIBRE_MCP_SERVER_CMD")
    if override:
        parts = shlex.split(override)
        return StdioServerParameters(
            command=parts[0], args=parts[1:], cwd=repo_root, env=env
        )
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "src"],
        cwd=repo_root,
        env=env,
    )


def _render(result) -> str:
    if getattr(result, "structuredContent", None):
        return json.dumps(result.structuredContent)
    parts = []
    for block in result.content:
        parts.append(getattr(block, "text", repr(block)))
    text = "".join(parts)
    return ("ERROR: " + text) if result.isError else text


async def cmd_list() -> int:
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"{t.name}: {t.description.splitlines()[0] if t.description else ''}")
    return 0


def _parse_line(line: str) -> tuple[str, dict] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split(None, 1)
    tool = parts[0]
    args = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else {}
    return tool, args


async def cmd_run() -> int:
    commands = []
    for raw in sys.stdin:
        parsed = _parse_line(raw)
        if parsed:
            commands.append(parsed)
    if not commands:
        print("no commands on stdin", file=sys.stderr)
        return 1

    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            rc = 0
            for tool, args in commands:
                result = await session.call_tool(tool, arguments=args)
                rendered = _render(result)
                print(f"{tool} -> {rendered}")
                if result.isError:
                    rc = 1
    return rc


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    if mode == "list":
        return asyncio.run(cmd_list())
    if mode == "run":
        return asyncio.run(cmd_run())
    print(f"unknown mode: {mode} (use 'list' or 'run')", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
