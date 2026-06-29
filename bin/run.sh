#!/bin/bash
# Run the libre-mcp stdio server — the command the committed .mcp.json points at.
# stdout is the JSON-RPC channel; env setup is delegated to env.sh (stdout-clean).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

exec uv run libre-mcp
