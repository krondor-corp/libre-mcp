"""Session recovery: bridge-health probing and forced close.

No LibreOffice needed. Session tests stub the worker client; worker-op
tests stub the UNO bridge modules in sys.modules before importing
`uno_worker` (same technique as tests/test_unit.py, kept local so this
file stands alone).
"""

import sys
import types

import pytest

from src.config import Config
from src.office.worker import WorkerError


@pytest.fixture
def worker_module():
    saved = dict(sys.modules)
    sys.modules["uno"] = types.ModuleType("uno")
    helper = types.ModuleType("unohelper")
    helper.Base = type("Base", (), {})
    sys.modules["unohelper"] = helper
    for name in (
        "com",
        "com.sun",
        "com.sun.star",
        "com.sun.star.beans",
        "com.sun.star.util",
    ):
        sys.modules[name] = types.ModuleType(name)
    sys.modules["com.sun.star.beans"].PropertyValue = object
    sys.modules["com.sun.star.util"].XModifyListener = type("XModifyListener", (), {})
    sys.modules["com.sun.star.util"].CloseVetoException = type(
        "CloseVetoException", (Exception,), {}
    )
    sys.modules.pop("src.office.uno_worker", None)
    import src.office.uno_worker as worker

    yield worker
    sys.modules.clear()
    sys.modules.update(saved)


class _FakeWorkerClient:
    def __init__(self, behavior):
        self._behavior = behavior
        self.calls = []

    async def call(self, op, **args):
        self.calls.append((op, args))
        action = self._behavior[len(self.calls) - 1]
        if isinstance(action, Exception):
            raise action
        return action

    async def stop(self):
        pass


def _stub_session(monkeypatch, first, second=None):
    from src.office.session import OfficeSession

    session = OfficeSession(Config())
    events = []

    async def fake_ensure():
        events.append("ensure")
        if session._worker is None or session._soffice is None:
            await fake_teardown()
            await fake_start()

    async def fake_teardown():
        events.append("teardown")
        session._worker = None
        session._soffice = None

    async def fake_start():
        events.append("start")
        session._worker = _FakeWorkerClient(second or [{"pong": True}])
        session._soffice = object()

    monkeypatch.setattr(session, "_ensure_started", fake_ensure)
    monkeypatch.setattr(session, "_teardown_locked", fake_teardown)
    monkeypatch.setattr(session, "_start_locked", fake_start)
    session._worker = _FakeWorkerClient(first)
    session._soffice = object()
    return session, events


async def test_fatal_doc_op_keeps_healthy_session(monkeypatch):
    # Only the document is gone (e.g. closed in the live window): the op
    # raises, but the live bridge — and the session — stay up.
    session, events = _stub_session(
        monkeypatch,
        [
            WorkerError("DisposedException", "doc gone", fatal=True),
            {"pong": True, "components": 2},
        ],
    )
    with pytest.raises(WorkerError):
        await session.call("get_text", doc_id="doc-1")
    assert events == ["ensure"]
    assert session._worker is not None


async def test_fatal_doc_op_tears_down_dead_bridge(monkeypatch):
    # Bridge and document both gone: the failing doc op raises (its handle
    # is gone), but the teardown lets the NEXT call rebuild instead of
    # reusing the dead worker.
    session, events = _stub_session(
        monkeypatch,
        [
            WorkerError("DisposedException", "bridge gone", fatal=True),
            WorkerError("DisposedException", "bridge gone", fatal=True),
        ],
    )
    with pytest.raises(WorkerError):
        await session.call("get_text", doc_id="doc-1")
    assert events == ["ensure", "teardown"]
    assert session._worker is None
    out = await session.call("ping")
    assert out == {"pong": True}
    assert events == ["ensure", "teardown", "ensure", "teardown", "start"]


async def test_fatal_docless_op_restarts_and_retries(monkeypatch):
    session, events = _stub_session(
        monkeypatch,
        [WorkerError("DisposedException", "bridge gone", fatal=True)],
        [{"doc_id": "doc-9"}],
    )
    out = await session.call("create_document", kind="writer")
    assert out == {"doc_id": "doc-9"}
    assert events == ["ensure", "teardown", "start"]


async def test_nonfatal_error_raises_without_teardown(monkeypatch):
    session, events = _stub_session(
        monkeypatch, [WorkerError("unknown_op", "nope", fatal=False)]
    )
    with pytest.raises(WorkerError):
        await session.call("get_text", doc_id="doc-1")
    assert events == ["ensure"]
    assert session._worker is not None


def test_ping_reports_desktop_components(worker_module):
    worker = worker_module.Worker("dummy-url")

    class _Enum:
        def __init__(self):
            self.left = 3

        def hasMoreElements(self):
            return self.left > 0

        def nextElement(self):
            self.left -= 1
            return object()

    class _Components:
        def createEnumeration(self):
            return _Enum()

    class _Desktop:
        def getComponents(self):
            return _Components()

    worker.desktop = _Desktop()
    assert worker.op_ping({}) == {"pong": True, "components": 3}


class _VetoDoc:
    def __init__(self, CloseVeto):
        self._CloseVeto = CloseVeto
        self.disposed = False

    def isModified(self):
        return False

    def close(self, _save):
        raise self._CloseVeto("Controller disagree")

    def dispose(self):
        self.disposed = True


def test_close_force_disposes_on_veto(worker_module):
    CloseVeto = sys.modules["com.sun.star.util"].CloseVetoException
    worker = worker_module.Worker("dummy-url")
    doc = _VetoDoc(CloseVeto)
    worker.docs["doc-1"] = doc
    assert worker.op_close_document({"doc_id": "doc-1", "force": True}) == {
        "closed": "doc-1"
    }
    assert doc.disposed
    assert "doc-1" not in worker.docs


def test_close_veto_without_force_raises_and_stays_tracked(worker_module):
    CloseVeto = sys.modules["com.sun.star.util"].CloseVetoException
    worker = worker_module.Worker("dummy-url")
    doc = _VetoDoc(CloseVeto)
    worker.docs["doc-1"] = doc
    with pytest.raises(CloseVeto):
        worker.op_close_document({"doc_id": "doc-1"})
    assert not doc.disposed
    assert worker.docs["doc-1"] is doc
