#!/bin/bash
# Run the libre-mcp stdio server. stdout is the JSON-RPC channel; logs go to stderr.
#
# The server is stateless across runs (open documents live only for the lifetime
# of one server process), and it isolates LibreOffice per git branch, so multiple
# branches/worktrees can run concurrently without colliding.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Per-branch identity: keeps profiles legible and isolated when the same checkout
# switches branches. (Separate worktrees are already isolated by their cwd.)
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo no-git)"
BRANCH_SAFE="${BRANCH//\//-}"
export LIBRE_MCP_BRANCH="$BRANCH"
export LIBRE_MCP_PROFILE_DIR="${LIBRE_MCP_PROFILE_DIR:-$PWD/.lo_profiles/$BRANCH_SAFE}"
export LIBRE_MCP_LOG_LEVEL="${LIBRE_MCP_LOG_LEVEL:-INFO}"

exec uv run libre-mcp
