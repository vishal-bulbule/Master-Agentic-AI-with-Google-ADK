# Author: Vishal Bulbule
# Date: 2026-09-22

"""Unit tests for greet_agent: fast, no model calls, no credentials.

They catch the cheap failures first (a typo in agent.py, a missing
`__init__.py`, a tool that raises instead of returning an error dict) before
the pipeline spends time and money on the eval in `test_greet_eval.py`.
"""

import importlib

from greet_agent.agent import greet


def test_agent_imports():
    module = importlib.import_module("greet_agent.agent")
    assert module.root_agent.name == "greet_agent"


def test_greet_happy_path():
    result = greet("Priya")
    assert result["status"] == "success"
    assert result["message"] == "Hello, Priya!"


def test_greet_rejects_empty_name():
    result = greet("   ")
    assert result["status"] == "error"
    assert "error_message" in result
