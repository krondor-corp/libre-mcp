"""Writer (text document) tools."""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session
from src.tools._defaults import ACCENT, INK, WHITE


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

    # --- rich documents: styled flow content + page-anchored decoration ---

    @mcp.tool()
    async def page_setup(
        doc_id: str,
        margin: float | None = None,
        top: float | None = None,
        color: str | None = None,
    ) -> dict:
        """Set page margins (cm) and/or page background color (hex) for a Writer
        doc. `margin` sets left/right/bottom; `top` overrides the top margin
        (raise it to clear a header band).
        """
        return await get_session().call(
            "page_setup", doc_id=doc_id, margin=margin, top=top, color=color
        )

    @mcp.tool()
    async def add_paragraph(
        doc_id: str,
        text: str,
        size: float = 11,
        color: str = INK,
        bold: bool = False,
        italic: bool = False,
        align: str = "left",
        font: str | None = None,
        space_before: float = 0,
        space_after: float = 0.2,
        style: str | None = None,
    ) -> dict:
        """Append a styled paragraph to a Writer doc (the workhorse — use a large
        bold size for headings). size is points; color is hex; align is
        left|center|right|justify; space_before/after are cm. `style` optionally
        applies a named paragraph style (e.g. "Heading 1").
        """
        return await get_session().call(
            "add_paragraph",
            doc_id=doc_id,
            text=text,
            size=size,
            color=color,
            bold=bold,
            italic=italic,
            align=align,
            font=font,
            space_before=space_before,
            space_after=space_after,
            style=style,
        )

    @mcp.tool()
    async def add_list(
        doc_id: str,
        items: list[str],
        ordered: bool = False,
        size: float = 11,
        color: str = INK,
    ) -> dict:
        """Append a bulleted (or numbered, if ordered=true) list — one string per
        item."""
        return await get_session().call(
            "add_list",
            doc_id=doc_id,
            items=items,
            ordered=ordered,
            size=size,
            color=color,
        )

    @mcp.tool()
    async def insert_table(
        doc_id: str,
        rows: list[list[str]],
        header: bool = True,
        accent: str = ACCENT,
        color: str = INK,
        size: float = 11,
    ) -> dict:
        """Insert a table from a 2D list of rows. With header=true the first row
        gets the accent background + white bold text.
        """
        return await get_session().call(
            "insert_table",
            doc_id=doc_id,
            rows=rows,
            header=header,
            accent=accent,
            color=color,
            size=size,
        )

    @mcp.tool()
    async def insert_image(doc_id: str, path: str, width_cm: float = 8) -> dict:
        """Insert an image inline from an absolute path, scaled to width_cm
        (aspect preserved)."""
        return await get_session().call(
            "insert_image", doc_id=doc_id, path=path, width_cm=width_cm
        )

    @mcp.tool()
    async def add_page_box(
        doc_id: str,
        x: float,
        y: float,
        w: float,
        h: float,
        text: str | None = None,
        fill: str | None = None,
        color: str = WHITE,
        size: float = 18,
        bold: bool = False,
        align: str = "left",
        font: str | None = None,
        pad: float = 0.3,
    ) -> dict:
        """Place a page-anchored box (a colored band, header, or pull-quote
        callout). x/y/w/h are percent (0-100) of the PAGE; fill is the box color
        (hex, or null for transparent); optional `text` is styled with
        color/size/bold/align. Great for letterheads and report headers.
        """
        return await get_session().call(
            "add_page_box",
            doc_id=doc_id,
            x=x,
            y=y,
            w=w,
            h=h,
            text=text,
            fill=fill,
            color=color,
            size=size,
            bold=bold,
            align=align,
            font=font,
            pad=pad,
        )
