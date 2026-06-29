#!/bin/bash
# Dev runner: debug logging + a kept profile, with a startup banner. The banner
# goes to STDERR because stdout is the MCP protocol channel. Env setup is shared
# with run.sh via env.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LIBRE_MCP_LOG_LEVEL="${LIBRE_MCP_LOG_LEVEL:-DEBUG}"
export LIBRE_MCP_KEEP_PROFILE="${LIBRE_MCP_KEEP_PROFILE:-1}"
source "$SCRIPT_DIR/env.sh"

{
  echo "libre-mcp dev server"
  echo "  branch:  $LIBRE_MCP_BRANCH"
  echo "  profile: $LIBRE_MCP_PROFILE_DIR"
  echo "  log:     $LIBRE_MCP_LOG_LEVEL"
} >&2

exec uv run libre-mcp
