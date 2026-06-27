import sys

from src.config import Config, ConfigException
from src.log import get_logger
from src.server import create_server

log = get_logger(__name__)


def main() -> int:
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


if __name__ == "__main__":
    sys.exit(main())
