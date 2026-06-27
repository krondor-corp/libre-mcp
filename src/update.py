"""Self-update for the packaged binary: fetch the latest GitHub Release asset for
this platform and replace the running executable in place. Stdlib only.
"""

import json
import os
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.request

from src import __version__

REPO = "krondor-corp/libre-mcp"


def _platform_tokens() -> tuple[str | None, str | None]:
    os_token = {"Linux": "linux", "Darwin": "darwin"}.get(platform.system())
    arch = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "arm64": "aarch64",
        "aarch64": "aarch64",
    }.get(platform.machine().lower())
    return os_token, arch


def _get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "libre-mcp"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def self_update() -> int:
    if not getattr(sys, "frozen", False):
        print(
            "update is only for the packaged binary; for a source install use git + uv",
            file=sys.stderr,
        )
        return 1

    os_token, arch = _platform_tokens()
    if not os_token or not arch:
        print(
            f"unsupported platform: {platform.system()}/{platform.machine()}",
            file=sys.stderr,
        )
        return 1

    rel = _get_json(f"https://api.github.com/repos/{REPO}/releases/latest")
    tag = rel.get("tag_name", "")
    if tag == f"v{__version__}":
        print(f"already up to date ({tag})", file=sys.stderr)
        return 0

    asset_name = f"libre-mcp-{tag}-{arch}-{os_token}.tar.gz"
    url = next(
        (
            a["browser_download_url"]
            for a in rel.get("assets", [])
            if a["name"] == asset_name
        ),
        None,
    )
    if not url:
        print(f"no asset {asset_name} on release {tag}", file=sys.stderr)
        return 1

    current = os.path.realpath(sys.executable)
    print(f"updating {current}: {__version__} -> {tag} ...", file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        archive = os.path.join(tmp, "pkg.tar.gz")
        urllib.request.urlretrieve(url, archive)
        with tarfile.open(archive) as tf:
            tf.extractall(tmp)
        new_bin = next(
            (
                os.path.join(root, "libre-mcp")
                for root, _, files in os.walk(tmp)
                if "libre-mcp" in files
            ),
            None,
        )
        if not new_bin:
            print("binary not found in archive", file=sys.stderr)
            return 1
        # Stage in the destination dir so os.replace is atomic (same filesystem).
        staged = os.path.join(os.path.dirname(current), ".libre-mcp.update")
        try:
            shutil.copy2(new_bin, staged)
            os.chmod(staged, 0o755)
            os.replace(staged, current)
        except PermissionError:
            print(
                f"no write permission for {current}; re-run with privileges",
                file=sys.stderr,
            )
            return 1

    print(f"updated to {tag}", file=sys.stderr)
    return 0
