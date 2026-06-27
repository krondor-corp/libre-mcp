"""Supervise a headless soffice process listening for UNO connections.

Each instance gets an isolated UserInstallation profile and a UNIQUE named pipe.
Named pipes (rather than TCP ports) make concurrent instances collision-proof:
there is no shared port to race over, which matters for parallel-worktree dev.
Instances are disposable: on death we relaunch rather than revive a hung bridge.
"""

import asyncio
import os
import shutil
import subprocess
import uuid

from src.log import get_logger

log = get_logger(__name__)


def unique_pipe_name() -> str:
    """A pipe name unique across processes and instances on this machine."""
    return f"libre_mcp_{os.getpid()}_{uuid.uuid4().hex[:12]}"


class SofficeProcess:
    def __init__(
        self,
        soffice_path: str,
        pipe_name: str,
        profile_dir: str,
        keep_profile: bool = False,
        startup_timeout: float = 30.0,
    ) -> None:
        self.soffice_path = soffice_path
        self.pipe_name = pipe_name
        self.profile = os.path.abspath(
            os.path.join(profile_dir, f"instance-{pipe_name}")
        )
        self.keep_profile = keep_profile
        self.startup_timeout = startup_timeout
        self._proc: subprocess.Popen | None = None

    @property
    def url(self) -> str:
        return f"uno:pipe,name={self.pipe_name};urp;StarOffice.ComponentContext"

    async def start(self) -> None:
        os.makedirs(self.profile, exist_ok=True)
        accept = f"pipe,name={self.pipe_name};urp;StarOffice.ComponentContext"
        args = [
            self.soffice_path,
            "--headless",
            "--invisible",
            "--norestore",
            "--nologo",
            "--nodefault",
            "--nolockcheck",
            f"-env:UserInstallation=file://{self.profile}",
            f"--accept={accept}",
        ]
        logf = open(os.path.join(self.profile, "soffice.log"), "ab")
        log.info(
            "launching soffice (pipe=%s, profile=%s)", self.pipe_name, self.profile
        )
        self._proc = subprocess.Popen(
            args, stdout=logf, stderr=logf, stdin=subprocess.DEVNULL
        )

        # Brief settle to catch immediate launch/config failures. True readiness
        # is gated by the worker's connect-retry loop (bounded by startup_timeout).
        await asyncio.sleep(0.5)
        if self._proc.poll() is not None:
            raise RuntimeError(
                f"soffice exited early with code {self._proc.returncode}; "
                f"see {self.profile}/soffice.log"
            )

    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    async def stop(self) -> None:
        proc = self._proc
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                await asyncio.get_event_loop().run_in_executor(None, proc.wait, 10)
            except Exception:
                proc.kill()
        self._proc = None
        if not self.keep_profile and os.path.isdir(self.profile):
            shutil.rmtree(self.profile, ignore_errors=True)
