"""PyInstaller entry point — bundles the libre-mcp server into one binary."""

import sys

from src.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
