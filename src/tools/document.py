"""Document lifecycle tools: create, open, list, info, save, export, close.

Documents live in the worker and are referenced by an opaque ``doc_id`` returned
from create/open. Most other tools take that ``doc_id``.
"""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_document(kind: str = "writer") -> dict:
        """Create a new empty LibreOffice document.

        kind: one of "writer", "calc", "impress", "draw". Returns {doc_id, kind};
        pass doc_id to subsequent tools.
        """
        return await get_session().call("create_document", kind=kind)

    @mcp.tool()
    async def open_document(path: str) -> dict:
        """Open an existing document from an absolute filesystem path.

        Returns {doc_id, kind, path}.
        """
        return await get_session().call("open_document", path=path)

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
    async def close_document(doc_id: str) -> dict:
        """Close an open document (discarding unsaved changes)."""
        return await get_session().call("close_document", doc_id=doc_id)
