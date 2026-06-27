#!/bin/bash
# Dev runner: verbose logging, keeps the soffice profile around for inspection.
# Delegates to run.sh (branch detection, profile dir) after setting dev defaults.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

export LIBRE_MCP_LOG_LEVEL="${LIBRE_MCP_LOG_LEVEL:-DEBUG}"
export LIBRE_MCP_KEEP_PROFILE="${LIBRE_MCP_KEEP_PROFILE:-1}"

exec ./bin/run.sh
