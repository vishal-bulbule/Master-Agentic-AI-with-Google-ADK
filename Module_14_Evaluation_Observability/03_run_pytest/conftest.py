# Author: Vishal Bulbule
# Date: 2026-09-22

"""Make `weather_agent` importable and load its credentials for pytest.

`AgentEvaluator.evaluate(agent_module="weather_agent")` imports the agent by
module name, so this folder must be on `sys.path`. Unlike `adk eval`, pytest
does not load `.env` files, so load the agent's `.env` here.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent

sys.path.insert(0, str(HERE))
# Existing environment variables win; a missing file is a no-op.
load_dotenv(HERE / "weather_agent" / ".env")
