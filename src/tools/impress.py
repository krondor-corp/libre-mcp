"""Impress (presentation) tools."""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session
from src.tools._defaults import ACCENT, INK, WHITE


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

    # --- graphics: positions/sizes are PERCENT (0-100) of the slide,
    #     colors are hex "#RRGGBB". Build slides background-first, then content. ---

    @mcp.tool()
    async def set_presentation_size(doc_id: str, preset: str = "16:9") -> dict:
        """Set the slide aspect ratio for the whole deck: "16:9" (default) or "4:3".

        Call this once on a new presentation before laying out slides.
        """
        return await get_session().call(
            "set_presentation_size", doc_id=doc_id, preset=preset
        )

    @mcp.tool()
    async def set_slide_background(
        doc_id: str,
        slide: int,
        color: str,
        color2: str | None = None,
        angle: float = 0,
    ) -> dict:
        """Fill a slide's background. Call this FIRST on a slide (it stacks at the
        back). Pass color2 for a linear gradient from color→color2 at `angle`
        degrees. Colors are hex like "#1a1a1a".
        """
        return await get_session().call(
            "set_slide_background",
            doc_id=doc_id,
            slide=slide,
            color=color,
            color2=color2,
            angle=angle,
        )

    @mcp.tool()
    async def add_textbox(
        doc_id: str,
        slide: int,
        text: str,
        x: float,
        y: float,
        w: float,
        h: float,
        size: float = 18,
        color: str = INK,
        bold: bool = False,
        italic: bool = False,
        align: str = "left",
        valign: str = "top",
        font: str | None = None,
    ) -> dict:
        """Place a styled text box. x/y/w/h are percent (0-100) of the slide;
        size is in points; color is hex; align is left|center|right; valign is
        top|center|bottom. Use newlines in `text` for multiple lines.
        """
        return await get_session().call(
            "add_textbox",
            doc_id=doc_id,
            slide=slide,
            text=text,
            x=x,
            y=y,
            w=w,
            h=h,
            size=size,
            color=color,
            bold=bold,
            italic=italic,
            align=align,
            valign=valign,
            font=font,
        )

    @mcp.tool()
    async def add_shape(
        doc_id: str,
        slide: int,
        x: float,
        y: float,
        w: float,
        h: float,
        shape: str = "rect",
        fill: str | None = ACCENT,
        fill2: str | None = None,
        angle: float = 0,
        corner: int = 300,
        line: str | None = None,
        line_width: int = 40,
        text: str | None = None,
        text_color: str = WHITE,
        text_size: float = 16,
        text_bold: bool = False,
    ) -> dict:
        """Draw a shape: shape is rect|round|ellipse|line. x/y/w/h are percent of
        the slide. fill is hex (or null for none); pass fill2 for a gradient at
        `angle`. `line`/`line_width` add a border (1/100 mm). Optional centered
        `text` with its own color/size/bold. `corner` (1/100 mm) rounds "round"
        rects.
        """
        return await get_session().call(
            "add_shape",
            doc_id=doc_id,
            slide=slide,
            x=x,
            y=y,
            w=w,
            h=h,
            shape=shape,
            fill=fill,
            fill2=fill2,
            angle=angle,
            corner=corner,
            line=line,
            line_width=line_width,
            text=text,
            text_color=text_color,
            text_size=text_size,
            text_bold=text_bold,
        )

    @mcp.tool()
    async def add_image(
        doc_id: str, slide: int, path: str, x: float, y: float, w: float, h: float
    ) -> dict:
        """Place an image from an absolute path. x/y/w/h are percent of the slide."""
        return await get_session().call(
            "add_image", doc_id=doc_id, slide=slide, path=path, x=x, y=y, w=w, h=h
        )
