#!/bin/bash
# Install libre-mcp as a uv tool from its latest GitHub Release wheel.
#
#   curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
#
# Pin a version:   LIBRE_MCP_VERSION=v0.1.0 bash install.sh
#
# Requires: curl, and LibreOffice installed on the host (the server drives it).
# uv is installed automatically if missing.
set -euo pipefail

REPO="krondor-corp/libre-mcp"
VERSION="${LIBRE_MCP_VERSION:-latest}"

say() { printf '\033[1m%s\033[0m\n' "$*"; }
err() { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }

command -v curl >/dev/null 2>&1 || err "curl is required"

# 1. Ensure uv is available.
if ! command -v uv >/dev/null 2>&1; then
  say "installing uv (https://astral.sh/uv) ..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || err "uv install failed; add it to PATH and retry"
fi

# 2. Resolve the release tag.
api="https://api.github.com/repos/${REPO}/releases"
if [ "$VERSION" = "latest" ]; then
  TAG="$(curl -fsSL "${api}/latest" | grep '"tag_name"' | head -1 | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')"
  [ -n "$TAG" ] || err "could not resolve the latest release tag"
else
  TAG="$VERSION"
fi
say "installing libre-mcp ${TAG} ..."

# 3. Find the wheel asset on that release.
WHEEL_URL="$(curl -fsSL "${api}/tags/${TAG}" \
  | grep 'browser_download_url' | grep '\.whl' | head -1 \
  | sed -E 's/.*"(https[^"]+\.whl)".*/\1/')"
[ -n "$WHEEL_URL" ] || err "no wheel asset found on release ${TAG}"

# 4. Download and install as an isolated uv tool.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
curl -fsSL -o "${tmp}/pkg.whl" "$WHEEL_URL"
uv tool install --force "${tmp}/pkg.whl"

say "done."
echo
echo "  Registered the 'libre-mcp' command. Add it to Claude Code with:"
echo "    claude mcp add libre -- libre-mcp"
echo
echo "  (Requires LibreOffice installed; on Debian/Ubuntu also: apt install python3-uno)"
