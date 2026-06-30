"""Document lifecycle tools: create, open, list, info, save, export, close.

Documents live in the worker and are referenced by an opaque ``doc_id`` returned
from create/open. Most other tools take that ``doc_id``.
"""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_document(kind: str = "writer", show: bool | None = None) -> dict:
        """Create a new empty LibreOffice document.

        kind: one of "writer", "calc", "impress", "draw". Returns {doc_id, kind};
        pass doc_id to subsequent tools.

        show: in live mode, whether to open it in a visible window so edits are
        watchable. Defaults to the server's live setting; pass false to build it
        off-screen, true to pop it up. (No effect on a headless server.)
        """
        return await get_session().call("create_document", kind=kind, show=show)

    @mcp.tool()
    async def open_document(path: str, show: bool | None = None) -> dict:
        """Open an existing document from an absolute filesystem path.

        Returns {doc_id, kind, path}. `show` (live mode) opens it in a visible
        window (true) or edits it off-screen (false); defaults to the server's
        live setting.
        """
        return await get_session().call("open_document", path=path, show=show)

    @mcp.tool()
    async def list_documents() -> dict:
        """List currently open documents as {documents: [{doc_id, kind, url}]}."""
        return await get_session().call("list_documents")

    @mcp.tool()
    async def document_info(doc_id: str) -> dict:
        """Get {kind, url, modified} for an open document."""
        return await get_session().call("document_info", doc_id=doc_id)

    @mcp.tool()
    async def save_document(
        doc_id: str, path: str | None = None, format: str | None = None
    ) -> dict:
        """Save a document.

        With no path, saves in place (the document must already have a location).
        With an absolute path, saves a copy; format is inferred from the
        extension if omitted (e.g. odt, pdf, docx, ods, xlsx, csv, html).
        """
        return await get_session().call(
            "save_document", doc_id=doc_id, path=path, format=format
        )

    @mcp.tool()
    async def export_document(
        doc_id: str, path: str, format: str | None = None
    ) -> dict:
        """Export a document to an absolute path in the given format.

        format examples: pdf, docx, odt, xlsx, ods, csv, html, txt. Inferred from
        the path extension if omitted.
        """
        return await get_session().call(
            "export_document", doc_id=doc_id, path=path, format=format
        )

    @mcp.tool()
    async def close_document(doc_id: str, force: bool = False) -> dict:
        """Close an open document.

        Refuses with a warning if the document has unsaved changes (so in-flight
        work — yours or a human's, in a live window — isn't silently discarded);
        save_document first, or pass force=true to close and discard.
        """
        return await get_session().call("close_document", doc_id=doc_id, force=force)
