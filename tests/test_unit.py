"""Fast unit tests for the UNO worker's window handling.

No LibreOffice needed. The `uno_worker` module imports UNO bridge modules at
the top level, so tests stub `uno` / `unohelper` / `com.sun.star.*` in
sys.modules before importing it.
"""

import sys
import types


def _load_worker_helpers():
    if "src.office.uno_worker" in sys.modules:
        return sys.modules["src.office.uno_worker"]
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
    import src.office.uno_worker as worker

    return worker


class _FakeWindow:
    def __init__(self, failures=0):
        self.failures = failures
        self.set_visible_calls = 0
        self.to_front_calls = 0

    def setVisible(self, visible):
        assert visible
        self.set_visible_calls += 1
        if self.set_visible_calls <= self.failures:
            raise RuntimeError("window not realizable yet")

    def toFront(self):
        self.to_front_calls += 1


class _FakeDoc:
    def __init__(self, window):
        self._window = window

    def getCurrentController(self):
        return self

    def getFrame(self):
        return self

    def getContainerWindow(self):
        return self._window


def test_show_maps_window():
    w = _load_worker_helpers()
    worker = w.Worker("dummy-url")
    window = _FakeWindow()
    worker._show(_FakeDoc(window))
    assert window.set_visible_calls == 1


def test_show_never_calls_to_front():
    # toFront() on a Wayland container window disposes the URP bridge,
    # failing every later op on the connection — and the compositor owns
    # focus anyway. setVisible alone must map the window.
    w = _load_worker_helpers()
    worker = w.Worker("dummy-url")
    window = _FakeWindow()
    worker._show(_FakeDoc(window))
    assert window.to_front_calls == 0


def test_show_retries_transient_failure():
    w = _load_worker_helpers()
    worker = w.Worker("dummy-url")
    window = _FakeWindow(failures=2)
    worker._show(_FakeDoc(window))
    assert window.set_visible_calls == 3
    assert window.to_front_calls == 0


def test_show_never_raises():
    w = _load_worker_helpers()
    worker = w.Worker("dummy-url")
    window = _FakeWindow(failures=999)
    worker._show(_FakeDoc(window))  # must not raise
    assert window.set_visible_calls == w._SHOW_ATTEMPTS
