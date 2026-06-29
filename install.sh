#!/usr/bin/env bash
set -euo pipefail

REPO="krondor-corp/libre-mcp"
BINARY="libre-mcp"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"

TMP=""
trap 'rm -rf "${TMP}"' EXIT

main() {
    local os arch version url

    os="$(detect_os)"
    arch="$(detect_arch)"

    if [ "$os" = "darwin" ] && [ "$arch" = "x86_64" ]; then
        echo "No prebuilt binary for Intel macOS. Build from source:" >&2
        echo "  git clone https://github.com/${REPO} && cd libre-mcp && make install" >&2
        exit 1
    fi

    version="$(latest_version)"

    echo "Installing ${BINARY} ${version} (${arch}-${os})..."

    url="https://github.com/${REPO}/releases/download/${version}/${BINARY}-${version}-${arch}-${os}.tar.gz"

    TMP="$(mktemp -d)"

    curl -fsSL "${url}" | tar -xz -C "${TMP}"
    mkdir -p "${INSTALL_DIR}"
    mv "${TMP}"/${BINARY}-${version}-${arch}-${os}/${BINARY} "${INSTALL_DIR}/${BINARY}"
    chmod +x "${INSTALL_DIR}/${BINARY}"

    echo "Installed ${BINARY} to ${INSTALL_DIR}/${BINARY}"
    echo "Register it with: claude mcp add libre -- ${INSTALL_DIR}/${BINARY}"
    echo "(Requires LibreOffice; on Debian/Ubuntu also: apt install python3-uno)"

    if ! echo ":${PATH}:" | grep -q ":${INSTALL_DIR}:"; then
        echo ""
        echo "Add to your PATH:"
        echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
    fi
}

detect_os() {
    case "$(uname -s)" in
        Linux*)  echo "linux" ;;
        Darwin*) echo "darwin" ;;
        *)       echo "Unsupported OS: $(uname -s)" >&2; exit 1 ;;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64)  echo "x86_64" ;;
        arm64|aarch64) echo "aarch64" ;;
        *)             echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;;
    esac
}

latest_version() {
    curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
        | grep '"tag_name"' \
        | head -1 \
        | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/'
}

main
