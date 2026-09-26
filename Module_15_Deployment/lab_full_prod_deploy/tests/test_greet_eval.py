# Author: Vishal Bulbule
# Date: 2026-09-22

"""Eval gate for greet_agent: runs the agent against the real model.

`greet.test.json` has two cases; `test_config.json` next to it requires the
exact tool call and a close answer. If a prompt or model change breaks the
agent, this test fails and the pipeline stops before `adk deploy`.
"""

from pathlib import Path

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

HERE = Path(__file__).resolve().parent


@pytest.mark.asyncio
async def test_greet_agent_eval():
    await AgentEvaluator.evaluate(
        agent_module="greet_agent",
        eval_dataset_file_path_or_dir=str(HERE / "greet.test.json"),
        num_runs=1,
    )
