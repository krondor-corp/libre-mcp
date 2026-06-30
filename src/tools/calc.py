"""Calc (spreadsheet) tools."""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session
from src.tools._defaults import INK


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def set_cells(
        doc_id: str, cells: list[dict], sheet: str | int | None = None
    ) -> dict:
        """Write cells in a Calc document. Returns {written}.

        cells is a list of {cell, value?|formula?} entries, e.g.
          [{"cell": "A1", "value": 21}, {"cell": "A2", "formula": "=A1*2"}]
        A "value" that is a number is written numerically; otherwise as text. A
        "formula" (starting with =) is evaluated by Calc. sheet selects the
        target sheet by name or 0-based index (defaults to the first sheet).
        """
        return await get_session().call(
            "set_cells", doc_id=doc_id, cells=cells, sheet=sheet
        )

    @mcp.tool()
    async def read_cells(
        doc_id: str,
        range: str,
        sheet: str | int | None = None,
        formula: bool = False,
    ) -> dict:
        """Read a cell range (e.g. "A1:C10") as {values: [[...]]}.

        Each row is a list; numeric cells come back as numbers, text as strings.
        Set formula=true to read the underlying formula strings instead of
        evaluated values (e.g. "=A1*2") — useful for inspecting an existing model.
        sheet selects the sheet by name or 0-based index (defaults to first).
        """
        return await get_session().call(
            "read_cells", doc_id=doc_id, range=range, sheet=sheet, formula=formula
        )

    @mcp.tool()
    async def add_sheet(doc_id: str, name: str, index: int | None = None) -> dict:
        """Add a worksheet by name (appended, or at `index`). Returns {name, count}."""
        return await get_session().call(
            "add_sheet", doc_id=doc_id, name=name, index=index
        )

    @mcp.tool()
    async def style_cells(
        doc_id: str,
        range: str,
        sheet: str | int | None = None,
        bold: bool | None = None,
        italic: bool = False,
        color: str = INK,
        fill: str | None = None,
        size: float | None = None,
        font: str | None = None,
        align: str | None = None,
        number_format: str | None = None,
    ) -> dict:
        """Format a cell range (e.g. "A1:E1"). bold/italic, text `color`, cell
        `fill`, `size` (pt), `font`, `align` (left|center|right), and
        `number_format` (a Calc format code, e.g. "$#,##0", "0.0%",
        "$#,##0;[RED]($#,##0)"). Only the args you pass are applied.
        """
        return await get_session().call(
            "style_cells",
            doc_id=doc_id,
            range=range,
            sheet=sheet,
            bold=bold,
            italic=italic,
            color=color,
            fill=fill,
            size=size,
            font=font,
            align=align,
            number_format=number_format,
        )

    @mcp.tool()
    async def set_column_width(
        doc_id: str, columns: str, width_cm: float, sheet: str | int | None = None
    ) -> dict:
        """Set the width (cm) of a column or column span, e.g. "A" or "A:E"."""
        return await get_session().call(
            "set_column_width",
            doc_id=doc_id,
            columns=columns,
            width_cm=width_cm,
            sheet=sheet,
        )
