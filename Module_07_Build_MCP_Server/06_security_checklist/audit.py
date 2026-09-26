# Author: Vishal Bulbule
# Date: 2026-09-22

"""Checklist item 6: structured audit logging for tool calls.

Each call writes one JSON line: tool name, argument names, outcome, and
duration. Cloud Run sends stdout and stderr to Cloud Logging and parses JSON
lines into structured entries you can filter and alert on.

Argument values are not logged by default: they often contain personal data
(emails, names) that should not end up in logs. Log values only for
arguments you have checked are safe.
"""

import json
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger("mcp.audit")


def audit_tool(name: str, log_values_for: tuple[str, ...] = ()) -> Callable:
    """Decorator that logs each call of a sync tool function as one JSON line.

    Args:
        name: Tool name to record.
        log_values_for: Argument names whose values are safe to log.

    Returns:
        A decorator for the tool function. Put it below `@mcp.tool()`.
    """

    def wrap(fn: Callable) -> Callable:
        @wraps(fn)  # keeps the signature, so FastMCP still sees the parameters
        def inner(*args: Any, **kwargs: Any) -> Any:
            started = time.monotonic()
            ok, error = True, None
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                ok, error = False, type(e).__name__
                raise
            finally:
                logger.info(
                    json.dumps(
                        {
                            "event": "mcp_tool_call",
                            "tool": name,
                            "arg_names": sorted(kwargs),
                            "args": {k: kwargs[k] for k in log_values_for if k in kwargs},
                            "ok": ok,
                            "error": error,
                            "duration_ms": int((time.monotonic() - started) * 1000),
                        }
                    )
                )

        return inner

    return wrap
