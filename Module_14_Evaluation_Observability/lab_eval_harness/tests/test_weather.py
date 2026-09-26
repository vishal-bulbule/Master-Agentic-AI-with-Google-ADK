# Author: Vishal Bulbule
# Date: 2026-09-22

"""Run the lab's 15 eval cases with pytest.

`AgentEvaluator.evaluate` walks `tests/` for `*.test.json` files and applies the
`test_config.json` found next to each one:
  reference/  10 cases, tool trajectory + ROUGE-1 against a reference answer
  rubric/      5 cases, tool trajectory + rubric judge, no reference answer
Any case that misses a threshold fails the test, which fails CI.
"""

from pathlib import Path

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

HERE = Path(__file__).resolve().parent


@pytest.mark.asyncio
async def test_weather_agent_eval_suite():
    await AgentEvaluator.evaluate(
        agent_module="weather_agent",
        eval_dataset_file_path_or_dir=str(HERE),
        num_runs=1,
    )
