#!/usr/bin/env python3
"""Cycle entrypoint: regenerate AGP public dashboard from metrics + evidence."""
import subprocess
from pathlib import Path
DASH = Path("/workspace/agp/dashboard")
subprocess.check_call(["bash", str(DASH / "generate.sh")])
print("Dashboard regenerated at", DASH)
print("Open:", DASH / "index.html")
