"""Client for the UNO worker subprocess.

The worker (uno_worker.py) runs under LibreOffice's bundled Python, holds the
URP connection to soffice, and speaks newline-delimited JSON over stdio:

    -> {"id": 1, "op": "create_document", "args": {"kind": "writer"}}
    <- {"id": 1, "ok": true, "result": {"doc_id": "doc-1", "kind": "writer"}}

Requests are serialized with a lock; soffice document ops are single-threaded
anyway.
"""

import asyncio
import json

from src.log import get_logger

log = get_logger(__name__)


class WorkerError(RuntimeError):
    def __init__(self, type: str, message: str, fatal: bool = False):
        self.type = type
        self.message = message
        self.fatal = fatal
        super().__init__(f"{type}: {message}")


class WorkerClient:
    def __init__(
        self, python_path: str, script: str, url: str, connect_timeout: float = 30.0
    ) -> None:
        self.python_path = python_path
        self.script = script
        self.url = url
        self.connect_timeout = connect_timeout
        self._proc: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()
        self._next_id = 0
        self._stderr_task: asyncio.Task | None = None

    async def start(self) -> None:
        log.info("starting uno worker: %s %s", self.python_path, self.script)
        self._proc = await asyncio.create_subprocess_exec(
            self.python_path,
            self.script,
            "--url",
            self.url,
            "--connect-timeout",
            str(self.connect_timeout),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        # readiness handshake
        pong = await self.call("ping")
        if not pong.get("pong"):
            raise WorkerError("worker", "did not answer ping")
        log.info("uno worker ready")

    async def _drain_stderr(self) -> None:
        assert self._proc and self._proc.stderr
        async for raw in self._proc.stderr:
            line = raw.decode(errors="replace").rstrip()
            if line:
                log.debug("[worker] %s", line)

    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.returncode is None

    async def call(self, op: str, **args) -> dict:
        if self._proc is None:
            raise WorkerError("worker", "worker not started", fatal=True)
        async with self._lock:
            self._next_id += 1
            req_id = self._next_id
            payload = json.dumps({"id": req_id, "op": op, "args": args}) + "\n"
            assert self._proc.stdin and self._proc.stdout
            self._proc.stdin.write(payload.encode())
            await self._proc.stdin.drain()

            raw = await self._proc.stdout.readline()
            if not raw:
                rc = self._proc.returncode
                raise WorkerError("worker", f"worker closed (rc={rc})", fatal=True)
            resp = json.loads(raw.decode())

        if not resp.get("ok"):
            err = resp.get("error", {})
            raise WorkerError(
                err.get("type", "error"),
                err.get("message", "unknown worker error"),
                fatal=bool(err.get("fatal")),
            )
        return resp.get("result", {})

    async def stop(self) -> None:
        proc = self._proc
        self._proc = None
        if proc is None:
            return
        try:
            if proc.returncode is None and proc.stdin:
                proc.stdin.write(
                    (
                        json.dumps({"id": 0, "op": "shutdown", "args": {}}) + "\n"
                    ).encode()
                )
                await proc.stdin.drain()
                await asyncio.wait_for(proc.wait(), timeout=5)
        except Exception:
            pass
        if proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=5)
            except Exception:
                proc.kill()
        if self._stderr_task:
            self._stderr_task.cancel()
