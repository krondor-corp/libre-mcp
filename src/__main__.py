import sys

from src import __version__
from src.log import get_logger

log = get_logger(__name__)

USAGE = """libre-mcp — MCP server for controlling LibreOffice

Usage:
  libre-mcp            run the MCP server over stdio (default)
  libre-mcp update     update the binary to the latest release
  libre-mcp version    print the version
"""


def run_server() -> int:
    from src.config import Config, ConfigException
    from src.server import create_server

    try:
        config = Config()
    except ConfigException as e:
        log.error("configuration error: %s", e.message)
        return 1

    try:
        server = create_server(config)
        log.info("starting libre-mcp stdio server")
        # FastMCP.run() owns stdout for JSON-RPC; logging is on stderr.
        server.run(transport="stdio")
        return 0
    except KeyboardInterrupt:
        log.info("interrupted")
        return 0
    except Exception as e:
        log.exception("fatal error: %s", e)
        return 1


def main() -> int:
    args = sys.argv[1:]
    if not args:
        return run_server()

    cmd = args[0]
    if cmd in ("update", "--update"):
        from src.update import self_update

        return self_update()
    if cmd in ("version", "--version", "-V"):
        print(__version__)
        return 0
    if cmd in ("help", "--help", "-h"):
        print(USAGE)
        return 0

    print(f"unknown command: {cmd}\n\n{USAGE}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
