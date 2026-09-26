# Author: Vishal Bulbule
# Date: 2026-09-22

"""Make the lab's `agent` package importable for pytest run from this folder."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
