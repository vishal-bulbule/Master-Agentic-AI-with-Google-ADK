# Author: Vishal Bulbule
# Date: 2026-09-22

"""Run the weather agent evals inside pytest with `AgentEvaluator`.

The first test lets `AgentEvaluator.evaluate` find `test_config.json` next to
the test file, which is how you normally wire it. The second builds the
`EvalConfig` in code, which is useful when thresholds differ per test.

A case that misses a threshold raises `AssertionError`, so pytest reports it
as a normal test failure with the per-invocation details printed above it.
"""

from pathlib import Path

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_set import EvalSet

HERE = Path(__file__).resolve().parent
TEST_FILE = HERE / "weather.test.json"


@pytest.mark.asyncio
async def test_weather_agent_with_config_file():
    """Criteria come from tests/test_config.json."""
    await AgentEvaluator.evaluate(
        agent_module="weather_agent",
        eval_dataset_file_path_or_dir=str(TEST_FILE),
        # The default is 2 runs per case. One keeps model calls low while
        # learning; raise it in CI to smooth out non-determinism.
        num_runs=1,
    )


@pytest.mark.asyncio
async def test_weather_agent_trajectory_only():
    """Criteria built in code: only the tool trajectory must match."""
    eval_set = EvalSet.model_validate_json(TEST_FILE.read_text())
    eval_config = EvalConfig(criteria={"tool_trajectory_avg_score": 1.0})
    await AgentEvaluator.evaluate_eval_set(
        agent_module="weather_agent",
        eval_set=eval_set,
        eval_config=eval_config,
        num_runs=1,
    )
