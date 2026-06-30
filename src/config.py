"""Runtime configuration, read from the environment.

Plain class in the house style (cf. krondor-corp/generic py-app config.py).
"""

import os
from enum import Enum as PyEnum


class ConfigExceptionType(PyEnum):
    invalid_value = "invalid_value"


class ConfigException(Exception):
    def __init__(self, type: ConfigExceptionType, message: str):
        self.message = message
        self.type = type
        super().__init__(message)


def _empty_to_none(field: str) -> str | None:
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value


def _bool(field: str, default: bool) -> bool:
    raw = os.getenv(field)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


class Config:
    # explicit overrides for the LibreOffice install (auto-discovered if unset)
    soffice_path: str | None
    python_path: str | None

    # where per-instance soffice profiles are created (isolation + concurrency).
    # UNO uses a unique named pipe per instance, so there is no port to configure.
    profile_dir: str
    keep_profile: bool

    # seconds to wait for soffice to accept a UNO connection
    startup_timeout: float

    log_level: str

    # debug mode (DEBUG log level) — enables dev hot-reload of the UNO worker
    debug: bool

    # live mode — run a VISIBLE LibreOffice window and show documents in it, so
    # edits are watchable in real time (local demo; not for the shipped server)
    live: bool

    def __str__(self) -> str:
        return (
            f"Config(soffice_path={self.soffice_path}, python_path={self.python_path}, "
            f"profile_dir={self.profile_dir}, keep_profile={self.keep_profile}, "
            f"startup_timeout={self.startup_timeout}, log_level={self.log_level}, "
            f"debug={self.debug}, live={self.live})"
        )

    def __init__(self) -> None:
        self.soffice_path = _empty_to_none("LIBRE_MCP_SOFFICE_PATH")
        self.python_path = _empty_to_none("LIBRE_MCP_PYTHON_PATH")

        self.profile_dir = os.getenv(
            "LIBRE_MCP_PROFILE_DIR",
            os.path.join(os.getcwd(), ".lo_profiles"),
        )
        self.keep_profile = _bool("LIBRE_MCP_KEEP_PROFILE", False)

        self.startup_timeout = float(os.getenv("LIBRE_MCP_STARTUP_TIMEOUT", "30"))

        self.log_level = os.getenv("LIBRE_MCP_LOG_LEVEL", "INFO").upper()

        self.debug = self.log_level == "DEBUG"

        self.live = _bool("LIBRE_MCP_LIVE", False)
