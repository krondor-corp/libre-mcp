"""Logging setup.

CRITICAL: in a stdio MCP server, stdout is the JSON-RPC channel. Every log
record MUST go to stderr or it corrupts the protocol stream. Never use print()
to stdout anywhere in this package.
"""

import logging
import os
import sys

_CONFIGURED = False


def configure() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    level = os.getenv("LIBRE_MCP_LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(getattr(logging, level, logging.INFO))
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure()
    return logging.getLogger(name)
