"""Calc (spreadsheet) tools."""

from mcp.server.fastmcp import FastMCP

from src.office.session import get_session


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
        doc_id: str, range: str, sheet: str | int | None = None
    ) -> dict:
        """Read a cell range (e.g. "A1:C10") as {values: [[...]]}.

        Each row is a list; numeric cells come back as numbers, text as strings.
        sheet selects the sheet by name or 0-based index (defaults to first).
        """
        return await get_session().call(
            "read_cells", doc_id=doc_id, range=range, sheet=sheet
        )
