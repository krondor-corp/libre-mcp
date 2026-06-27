"""Writer (text document) tools."""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_text(doc_id: str) -> dict:
        """Return the full plain text of a Writer document as {text}."""
        return await get_session().call("get_text", doc_id=doc_id)

    @mcp.tool()
    async def insert_text(
        doc_id: str, text: str, paragraph_break: bool = False
    ) -> dict:
        """Append text at the end of a Writer document.

        Set paragraph_break to start a new paragraph before inserting.
        """
        return await get_session().call(
            "insert_text", doc_id=doc_id, text=text, paragraph_break=paragraph_break
        )

    @mcp.tool()
    async def find_and_replace(
        doc_id: str, search: str, replace: str, regex: bool = False
    ) -> dict:
        """Replace all occurrences of search with replace. Returns {count}.

        Set regex=true to treat search as a regular expression.
        """
        return await get_session().call(
            "replace_all", doc_id=doc_id, search=search, replace=replace, regex=regex
        )
