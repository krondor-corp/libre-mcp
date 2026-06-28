"""UNO worker — runs under LibreOffice's BUNDLED Python interpreter.

STDLIB ONLY. This file must not import any third-party package: the bundled
interpreter is a reduced 3.10 build (no sqlite3/lzma) and we deliberately keep
it dependency-free so there is nothing to install into the app bundle.

It connects to a headless soffice over URP, then serves newline-delimited JSON
requests on stdin and writes JSON responses on stdout. All diagnostics go to
stderr. Document handles are kept in-process and referenced by doc_id.

Run:  <bundled-python> uno_worker.py --url "uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext"
"""

import argparse
import json
import sys
import time

import uno  # provided by the bundled interpreter
from com.sun.star.beans import PropertyValue


def eprint(*a) -> None:
    print(*a, file=sys.stderr, flush=True)


def _prop(name, value):
    p = PropertyValue()
    p.Name = name
    p.Value = value
    return p


# Export filter names keyed by (doc-kind, format). Format is a short token.
_FILTERS = {
    "writer": {
        "odt": "writer8",
        "pdf": "writer_pdf_Export",
        "docx": "MS Word 2007 XML",
        "doc": "MS Word 97",
        "rtf": "Rich Text Format",
        "txt": "Text",
        "html": "HTML (StarWriter)",
    },
    "calc": {
        "ods": "calc8",
        "pdf": "calc_pdf_Export",
        "xlsx": "Calc MS Excel 2007 XML",
        "xls": "MS Excel 97",
        "csv": "Text - txt - csv (StarCalc)",
        "html": "HTML (StarCalc)",
    },
    "impress": {
        "odp": "impress8",
        "pdf": "impress_pdf_Export",
        "pptx": "Impress MS PowerPoint 2007 XML",
    },
    "draw": {"odg": "draw8", "pdf": "draw_pdf_Export"},
}

_FACTORY = {
    "writer": "private:factory/swriter",
    "calc": "private:factory/scalc",
    "impress": "private:factory/simpress",
    "draw": "private:factory/sdraw",
}


class Worker:
    def __init__(self, url: str) -> None:
        self.url = url
        self.ctx = None
        self.desktop = None
        self.docs: dict[str, object] = {}
        self._counter = 0

    # -- connection -------------------------------------------------------
    def connect(self, timeout: float = 30.0, delay: float = 0.5) -> None:
        retries = max(1, int(timeout / delay))
        local = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local
        )
        last = None
        for _ in range(retries):
            try:
                self.ctx = resolver.resolve(self.url)
                break
            except Exception as e:  # NoConnectException until soffice is ready
                last = e
                time.sleep(delay)
        if self.ctx is None:
            raise RuntimeError(f"could not connect to soffice: {last}")
        smgr = self.ctx.ServiceManager
        self.desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx
        )
        eprint(f"connected to {self.url}")

    # -- helpers ----------------------------------------------------------
    def _new_id(self) -> str:
        self._counter += 1
        return f"doc-{self._counter}"

    def _doc(self, doc_id: str):
        doc = self.docs.get(doc_id)
        if doc is None:
            raise KeyError(f"unknown doc_id: {doc_id}")
        return doc

    @staticmethod
    def _kind_of(doc) -> str:
        checks = (
            ("com.sun.star.text.TextDocument", "writer"),
            ("com.sun.star.sheet.SpreadsheetDocument", "calc"),
            ("com.sun.star.presentation.PresentationDocument", "impress"),
            ("com.sun.star.drawing.DrawingDocument", "draw"),
        )
        for service, kind in checks:
            try:
                if doc.supportsService(service):
                    return kind
            except Exception:
                pass
        return "unknown"

    def _sheet(self, doc, sheet):
        sheets = doc.getSheets()
        if sheet is None:
            return sheets.getByIndex(0)
        if isinstance(sheet, int):
            return sheets.getByIndex(sheet)
        return sheets.getByName(sheet)

    # -- operations -------------------------------------------------------
    def op_ping(self, args):
        return {"pong": True}

    def op_create_document(self, args):
        kind = args.get("kind", "writer")
        if kind not in _FACTORY:
            raise ValueError(f"unknown kind: {kind}")
        doc = self.desktop.loadComponentFromURL(
            _FACTORY[kind], "_blank", 0, (_prop("Hidden", True),)
        )
        doc_id = self._new_id()
        self.docs[doc_id] = doc
        return {"doc_id": doc_id, "kind": kind}

    def op_open_document(self, args):
        path = args["path"]
        url = uno.systemPathToFileUrl(path)
        doc = self.desktop.loadComponentFromURL(
            url, "_blank", 0, (_prop("Hidden", True),)
        )
        doc_id = self._new_id()
        self.docs[doc_id] = doc
        return {"doc_id": doc_id, "kind": self._kind_of(doc), "path": path}

    def op_list_documents(self, args):
        out = []
        for doc_id, doc in self.docs.items():
            try:
                url = doc.getURL()
            except Exception:
                url = ""
            out.append({"doc_id": doc_id, "kind": self._kind_of(doc), "url": url})
        return {"documents": out}

    def op_document_info(self, args):
        doc = self._doc(args["doc_id"])
        return {
            "doc_id": args["doc_id"],
            "kind": self._kind_of(doc),
            "url": doc.getURL() or "",
            "modified": bool(doc.isModified()),
        }

    def op_close_document(self, args):
        doc_id = args["doc_id"]
        doc = self._doc(doc_id)
        doc.close(False)
        del self.docs[doc_id]
        return {"closed": doc_id}

    # writer
    def op_get_text(self, args):
        doc = self._doc(args["doc_id"])
        return {"text": doc.getText().getString()}

    def op_insert_text(self, args):
        doc = self._doc(args["doc_id"])
        text = doc.getText()
        cursor = text.createTextCursor()
        cursor.gotoEnd(False)
        if args.get("paragraph_break"):
            text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        text.insertString(cursor, args["text"], False)
        return {"ok": True}

    def op_replace_all(self, args):
        doc = self._doc(args["doc_id"])
        rd = doc.createReplaceDescriptor()
        rd.setSearchString(args["search"])
        rd.setReplaceString(args["replace"])
        rd.SearchRegularExpression = bool(args.get("regex", False))
        count = doc.replaceAll(rd)
        return {"count": int(count)}

    # calc
    def op_set_cells(self, args):
        doc = self._doc(args["doc_id"])
        sheet = self._sheet(doc, args.get("sheet"))
        written = 0
        for entry in args["cells"]:
            cell = sheet.getCellRangeByName(entry["cell"]).getCellByPosition(0, 0)
            if "formula" in entry and entry["formula"] is not None:
                cell.setFormula(entry["formula"])
            elif isinstance(entry.get("value"), (int, float)):
                cell.setValue(float(entry["value"]))
            else:
                cell.setString(str(entry.get("value", "")))
            written += 1
        return {"written": written}

    def op_read_cells(self, args):
        doc = self._doc(args["doc_id"])
        sheet = self._sheet(doc, args.get("sheet"))
        rng = sheet.getCellRangeByName(args["range"])
        data = [list(row) for row in rng.getDataArray()]
        return {"values": data}

    # impress
    def op_add_slide(self, args):
        doc = self._doc(args["doc_id"])
        slides = doc.getDrawPages()
        idx = slides.getCount()
        slides.insertNewByIndex(idx)
        page = slides.getByIndex(idx)
        layout = args.get("layout")
        page.Layout = 1 if layout is None else int(layout)
        return {"index": idx, "count": slides.getCount()}

    def op_set_slide_content(self, args):
        doc = self._doc(args["doc_id"])
        index = int(args["index"])
        page = doc.getDrawPages().getByIndex(index)
        title = args.get("title")
        bullets = args.get("bullets")
        if title is not None or bullets is not None:
            page.Layout = 1  # title + content placeholders
        if title is not None:
            page.getByIndex(0).setString(title)
        if bullets is not None:
            body = page.getByIndex(1).getText()
            body.setString("")
            cursor = body.createTextCursor()
            for i, line in enumerate(bullets):
                if i:
                    body.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
                body.insertString(cursor, str(line), False)
        return {"index": index}

    def op_list_slides(self, args):
        slides = self._doc(args["doc_id"]).getDrawPages()
        out = []
        for i in range(slides.getCount()):
            page = slides.getByIndex(i)
            title = ""
            for j in range(page.getCount()):
                shape = page.getByIndex(j)
                try:
                    if shape.supportsService(
                        "com.sun.star.presentation.TitleTextShape"
                    ):
                        title = shape.getString()
                        break
                except Exception:
                    pass
            out.append({"index": i, "title": title})
        return {"slides": out, "count": slides.getCount()}

    def op_delete_slide(self, args):
        slides = self._doc(args["doc_id"]).getDrawPages()
        page = slides.getByIndex(int(args["index"]))
        slides.remove(page)
        return {"count": slides.getCount()}

    # persistence
    def op_save_document(self, args):
        doc = self._doc(args["doc_id"])
        path = args.get("path")
        if path is None:
            if not doc.getURL():
                raise ValueError("document has no location; provide path")
            doc.store()
            return {"path": uno.fileUrlToSystemPath(doc.getURL())}
        fmt = args.get("format") or path.rsplit(".", 1)[-1].lower()
        kind = self._kind_of(doc)
        filt = _FILTERS.get(kind, {}).get(fmt)
        if not filt:
            raise ValueError(f"no filter for kind={kind} format={fmt}")
        url = uno.systemPathToFileUrl(path)
        doc.storeToURL(url, (_prop("FilterName", filt),))
        return {"path": path, "filter": filt}

    def op_export_document(self, args):
        # same machinery as save with an explicit format/path
        return self.op_save_document(args)


# Resolved lazily after `import uno` so the constant is real at call time.
PARAGRAPH_BREAK = None


def _load_constants():
    global PARAGRAPH_BREAK
    from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK as PB

    PARAGRAPH_BREAK = PB


_OPS = {name[3:]: name for name in dir(Worker) if name.startswith("op_")}


def serve(worker: Worker) -> None:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except Exception as e:
            sys.stdout.write(
                json.dumps(
                    {
                        "id": 0,
                        "ok": False,
                        "error": {"type": "bad_json", "message": str(e)},
                    }
                )
                + "\n"
            )
            sys.stdout.flush()
            continue

        req_id = req.get("id", 0)
        op = req.get("op", "")
        args = req.get("args", {}) or {}

        if op == "shutdown":
            sys.stdout.write(
                json.dumps({"id": req_id, "ok": True, "result": {}}) + "\n"
            )
            sys.stdout.flush()
            return

        method = _OPS.get(op)
        if method is None:
            sys.stdout.write(
                json.dumps(
                    {
                        "id": req_id,
                        "ok": False,
                        "error": {"type": "unknown_op", "message": op},
                    }
                )
                + "\n"
            )
            sys.stdout.flush()
            continue

        try:
            result = getattr(worker, method)(args)
            resp = {"id": req_id, "ok": True, "result": result}
        except Exception as e:
            fatal = "DisposedException" in type(
                e
            ).__name__ or "DisposedException" in str(e)
            resp = {
                "id": req_id,
                "ok": False,
                "error": {"type": type(e).__name__, "message": str(e), "fatal": fatal},
            }
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--connect-timeout", type=float, default=30.0)
    ns = parser.parse_args()

    worker = Worker(ns.url)
    worker.connect(timeout=ns.connect_timeout)
    _load_constants()
    serve(worker)
    return 0


if __name__ == "__main__":
    sys.exit(main())
