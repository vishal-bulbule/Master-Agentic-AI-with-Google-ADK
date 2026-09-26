# Author: Vishal Bulbule
# Date: 2026-09-22

"""Run the rubric eval for research_agent with pytest.

`AgentEvaluator.evaluate` reads `test_config.json` from the folder of the test
file. That config has a single rubric, `cites_a_source_url`, so every case is
judged on whether the answer contains the source link.
"""

from pathlib import Path

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

HERE = Path(__file__).resolve().parent


@pytest.mark.asyncio
async def test_research_agent_cites_url():
    """Every response must include an http(s):// URL."""
    await AgentEvaluator.evaluate(
        agent_module="research_agent",
        eval_dataset_file_path_or_dir=str(HERE / "rubric.test.json"),
        num_runs=1,
    )
