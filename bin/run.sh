#!/bin/bash
# Run the libre-mcp stdio server — the command .mcp.json points at.
# stdout is the JSON-RPC channel; env setup is delegated to env.sh (stdout-clean).
#
#   bin/run.sh          plain run (INFO logging)
#   bin/run.sh --dev    debug logging + kept profile + hot-reload of uno_worker.py
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEV=0
for arg in "$@"; do
  [ "$arg" = "--dev" ] && DEV=1
done

if [ "$DEV" = "1" ]; then
  # DEBUG log level is what turns on hot-reload in the server.
  export LIBRE_MCP_LOG_LEVEL="${LIBRE_MCP_LOG_LEVEL:-DEBUG}"
  export LIBRE_MCP_KEEP_PROFILE="${LIBRE_MCP_KEEP_PROFILE:-1}"
fi

source "$SCRIPT_DIR/env.sh"

if [ "$DEV" = "1" ]; then
  {
    echo "libre-mcp dev server"
    echo "  branch:  $LIBRE_MCP_BRANCH"
    echo "  profile: $LIBRE_MCP_PROFILE_DIR"
    echo "  log:     $LIBRE_MCP_LOG_LEVEL"
    echo "  reload:  on (debug; watching uno_worker.py)"
  } >&2
fi

exec uv run libre-mcp
