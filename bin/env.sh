#!/bin/bash
# Shared environment for the libre-mcp server scripts. Source it, then exec the
# server.
#
# IMPORTANT: emit nothing to stdout. bin/run.sh is launched as a stdio MCP
# server, where stdout is the JSON-RPC channel — diagnostics go to stderr.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Per-branch identity so parallel branches/worktrees stay isolated and legible.
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo no-git)"
BRANCH_SAFE="${BRANCH//\//-}"
export LIBRE_MCP_BRANCH="$BRANCH"
export LIBRE_MCP_PROFILE_DIR="${LIBRE_MCP_PROFILE_DIR:-$PWD/.lo_profiles/$BRANCH_SAFE}"
export LIBRE_MCP_LOG_LEVEL="${LIBRE_MCP_LOG_LEVEL:-INFO}"
