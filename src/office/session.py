"""OfficeSession: lazily start and supervise soffice + the UNO worker, and
expose a single async `call(op, **args)` to the rest of the app.

Instances are disposable. If the worker reports a fatal error (e.g. the URP
bridge was disposed because soffice died), we tear the session down and rebuild
it, retrying the failed call once.
"""

import asyncio

from src.config import Config
from src.log import get_logger
from src.office import discovery
from src.office.soffice import SofficeProcess, unique_pipe_name
from src.office.worker import WorkerClient, WorkerError

log = get_logger(__name__)


class OfficeSession:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._soffice: SofficeProcess | None = None
        self._worker: WorkerClient | None = None
        self._lock = asyncio.Lock()

    async def _ensure_started(self) -> None:
        if (
            self._worker
            and self._worker.is_alive()
            and self._soffice
            and self._soffice.is_alive()
        ):
            return
        async with self._lock:
            if (
                self._worker
                and self._worker.is_alive()
                and self._soffice
                and self._soffice.is_alive()
            ):
                return
            await self._teardown_locked()
            await self._start_locked()

    async def _start_locked(self) -> None:
        soffice_bin = discovery.find_soffice(self.config.soffice_path)
        python_bin = discovery.find_bundled_python(self.config.python_path, soffice_bin)

        soffice = SofficeProcess(
            soffice_path=soffice_bin,
            pipe_name=unique_pipe_name(),
            profile_dir=self.config.profile_dir,
            keep_profile=self.config.keep_profile,
            startup_timeout=self.config.startup_timeout,
        )
        await soffice.start()

        worker = WorkerClient(
            python_bin,
            discovery.worker_script(),
            soffice.url,
            connect_timeout=self.config.startup_timeout,
        )
        try:
            await worker.start()
        except Exception:
            await soffice.stop()
            raise

        self._soffice = soffice
        self._worker = worker

    async def _teardown_locked(self) -> None:
        if self._worker:
            await self._worker.stop()
            self._worker = None
        if self._soffice:
            await self._soffice.stop()
            self._soffice = None

    async def call(self, op: str, **args) -> dict:
        await self._ensure_started()
        assert self._worker
        try:
            return await self._worker.call(op, **args)
        except WorkerError as e:
            if not e.fatal:
                raise
            log.warning("fatal worker error (%s); restarting session and retrying", e)
            async with self._lock:
                await self._teardown_locked()
                await self._start_locked()
            assert self._worker
            return await self._worker.call(op, **args)

    async def shutdown(self) -> None:
        async with self._lock:
            await self._teardown_locked()


_session: OfficeSession | None = None


def get_session(config: Config | None = None) -> OfficeSession:
    global _session
    if _session is None:
        _session = OfficeSession(config or Config())
    return _session
