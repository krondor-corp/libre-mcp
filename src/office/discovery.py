"""Locate the LibreOffice soffice binary and its bundled Python interpreter.

The bundled interpreter matters: it is the only Python that can `import uno`
reliably (pyuno is a native module built against that exact interpreter, and on
macOS SIP strips DYLD_* from child processes so an external Python cannot
bootstrap the URE). We run the dependency-free UNO worker under it.
"""

import os
import shutil
import subprocess

from src.log import get_logger

log = get_logger(__name__)

# macOS app-bundle locations (soffice binary, then bundled python shim).
_MAC_SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
_MAC_PYTHON = "/Applications/LibreOffice.app/Contents/Resources/python"

# Common Linux install roots; each has program/soffice and program/python.
_LINUX_ROOTS = (
    "/usr/lib/libreoffice",
    "/usr/lib64/libreoffice",
    "/opt/libreoffice",
    "/snap/libreoffice/current/lib/libreoffice",
)


class DiscoveryError(RuntimeError):
    pass


def find_soffice(override: str | None = None) -> str:
    if override:
        if not os.path.exists(override):
            raise DiscoveryError(f"LIBRE_MCP_SOFFICE_PATH not found: {override}")
        return override

    candidates: list[str] = []
    if os.path.exists(_MAC_SOFFICE):
        candidates.append(_MAC_SOFFICE)
    for root in _LINUX_ROOTS:
        candidates.append(os.path.join(root, "program", "soffice"))
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    for c in candidates:
        if os.path.exists(c):
            log.debug("found soffice: %s", c)
            return c
    raise DiscoveryError(
        "could not locate the soffice binary; set LIBRE_MCP_SOFFICE_PATH"
    )


def find_bundled_python(override: str | None = None, soffice: str | None = None) -> str:
    if override:
        if not os.path.exists(override):
            raise DiscoveryError(f"LIBRE_MCP_PYTHON_PATH not found: {override}")
        return override

    candidates: list[str] = []
    if os.path.exists(_MAC_PYTHON):
        candidates.append(_MAC_PYTHON)

    # Linux (TDF/opt builds): the interpreter sits next to soffice in program/.
    if soffice:
        program = os.path.dirname(os.path.realpath(soffice))
        candidates.append(os.path.join(program, "python"))
    for root in _LINUX_ROOTS:
        candidates.append(os.path.join(root, "program", "python"))

    for c in candidates:
        if os.path.exists(c):
            log.debug("found bundled python: %s", c)
            return c

    # Debian/Ubuntu ship no bundled interpreter; `uno` is provided to the SYSTEM
    # python3 via the python3-uno package. Probe system interpreters and pick the
    # first that can actually `import uno` — never trust PATH, which in a uv/venv
    # environment resolves python3 to the project venv (which has no uno).
    for candidate in _system_python_candidates():
        if _can_import_uno(candidate):
            log.debug("using system python with uno: %s", candidate)
            return candidate

    raise DiscoveryError(
        "could not locate a python that can `import uno`; install python3-uno "
        "(Debian/Ubuntu) or set LIBRE_MCP_PYTHON_PATH"
    )


def _system_python_candidates() -> list[str]:
    """System python interpreters to probe, system locations first."""
    candidates = ["/usr/bin/python3", "/usr/local/bin/python3"]
    which = shutil.which("python3")
    if which:
        candidates.append(which)
    out: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        if os.path.exists(c):
            real = os.path.realpath(c)
            if real not in seen:
                seen.add(real)
                out.append(c)
    return out


def _can_import_uno(python_path: str) -> bool:
    try:
        proc = subprocess.run(
            [python_path, "-c", "import uno"],
            capture_output=True,
            timeout=15,
        )
        return proc.returncode == 0
    except Exception:
        return False


def worker_script() -> str:
    """Absolute path to the uno_worker.py run under the bundled interpreter."""
    return os.path.join(os.path.dirname(__file__), "uno_worker.py")
