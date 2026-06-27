"""End-to-end test against a real LibreOffice install.

Skipped automatically when soffice or its bundled python cannot be found.
"""

import os

import pytest

from src.config import Config
from src.office import discovery
from src.office.session import OfficeSession

pytestmark = pytest.mark.asyncio


def _have_libreoffice() -> bool:
    try:
        soffice = discovery.find_soffice(None)
        discovery.find_bundled_python(None, soffice)
        return True
    except discovery.DiscoveryError:
        return False


requires_lo = pytest.mark.skipif(
    not _have_libreoffice(), reason="LibreOffice not installed"
)


@pytest.fixture
async def session(tmp_path):
    config = Config()
    config.profile_dir = str(tmp_path / "profiles")
    config.keep_profile = False
    s = OfficeSession(config)
    try:
        yield s
    finally:
        await s.shutdown()


@requires_lo
async def test_writer_roundtrip(session, tmp_path):
    doc = await session.call("create_document", kind="writer")
    doc_id = doc["doc_id"]
    await session.call("insert_text", doc_id=doc_id, text="Hello libre-mcp")
    out = await session.call("get_text", doc_id=doc_id)
    assert "Hello libre-mcp" in out["text"]

    pdf = str(tmp_path / "out.pdf")
    res = await session.call("export_document", doc_id=doc_id, path=pdf, format="pdf")
    assert os.path.exists(res["path"])
    with open(res["path"], "rb") as fh:
        assert fh.read(5) == b"%PDF-"


@requires_lo
async def test_calc_formula(session):
    doc = await session.call("create_document", kind="calc")
    doc_id = doc["doc_id"]
    await session.call(
        "set_cells",
        doc_id=doc_id,
        cells=[
            {"cell": "A1", "value": 21},
            {"cell": "A2", "value": 2},
            {"cell": "A3", "formula": "=A1*A2"},
        ],
    )
    out = await session.call("read_cells", doc_id=doc_id, range="A3:A3")
    assert out["values"][0][0] == 42.0
