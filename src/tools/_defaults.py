"""Default colors for the document tools, in one place.

These are the defaults baked into the tool signatures (and thus the MCP schema).
The UNO worker is a separate stdlib-only process and cannot import this module —
it simply applies whatever color the tools pass, so these defaults live here only.
"""

INK = "#222222"  # body text / default foreground
ACCENT = "#c2410c"  # rust accent — highlights, table headers, fills
WHITE = "#ffffff"  # text on accent fills
