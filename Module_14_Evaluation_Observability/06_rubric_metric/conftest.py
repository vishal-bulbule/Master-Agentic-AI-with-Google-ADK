# Author: Vishal Bulbule
# Date: 2026-09-22

"""Make `research_agent` importable and load its credentials for pytest.

pytest does not load `.env` files itself, unlike `adk eval`.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent

sys.path.insert(0, str(HERE))
# Existing environment variables win; a missing file is a no-op.
load_dotenv(HERE / "research_agent" / ".env")
