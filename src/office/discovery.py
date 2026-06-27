"""Locate the LibreOffice soffice binary and its bundled Python interpreter.

The bundled interpreter matters: it is the only Python that can `import uno`
reliably (pyuno is a native module built against that exact interpreter, and on
macOS SIP strips DYLD_* from child processes so an external Python cannot
bootstrap the URE). We run the dependency-free UNO worker under it.
"""

import os
import shutil

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

    # Debian/Ubuntu ship no bundled interpreter; `uno` is provided to the system
    # python3 via the python3-uno package. Use it as a last resort.
    system_py = shutil.which("python3")
    if system_py:
        log.debug("falling back to system python3 (expects python3-uno): %s", system_py)
        return system_py

    raise DiscoveryError(
        "could not locate a python that can `import uno`; install python3-uno "
        "(Debian/Ubuntu) or set LIBRE_MCP_PYTHON_PATH"
    )


def worker_script() -> str:
    """Absolute path to the uno_worker.py run under the bundled interpreter."""
    return os.path.join(os.path.dirname(__file__), "uno_worker.py")
