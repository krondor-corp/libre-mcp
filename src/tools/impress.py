"""Impress (presentation) tools."""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def add_slide(doc_id: str, layout: int | None = None) -> dict:
        """Append a slide to an Impress presentation. Returns {index, count}.

        A new presentation already has one slide at index 0. layout is an Impress
        autolayout id (default 1 = title + content).
        """
        return await get_session().call("add_slide", doc_id=doc_id, layout=layout)

    @mcp.tool()
    async def set_slide_content(
        doc_id: str,
        index: int,
        title: str | None = None,
        bullets: list[str] | None = None,
    ) -> dict:
        """Set a slide's title and/or bullet body by 0-based slide index.

        bullets is a list of strings, one per bullet line.
        """
        return await get_session().call(
            "set_slide_content",
            doc_id=doc_id,
            index=index,
            title=title,
            bullets=bullets,
        )

    @mcp.tool()
    async def list_slides(doc_id: str) -> dict:
        """List slides as {slides: [{index, title}], count}."""
        return await get_session().call("list_slides", doc_id=doc_id)

    @mcp.tool()
    async def delete_slide(doc_id: str, index: int) -> dict:
        """Delete a slide by 0-based index. Returns {count}."""
        return await get_session().call("delete_slide", doc_id=doc_id, index=index)
