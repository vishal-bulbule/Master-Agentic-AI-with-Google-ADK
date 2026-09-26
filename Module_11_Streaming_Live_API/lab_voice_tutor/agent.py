# Author: Vishal Bulbule
# Date: 2026-09-22

"""Voice tutor for Python decorators, run from the adk web call (phone) button.

A Live API agent with one ordinary (non-streaming) tool. The model can call
lookup_definition in the middle of a spoken conversation; ADK runs the tool,
sends the result back over the same live connection, and the model continues
speaking from it.

The model ID comes from LIVE_MODEL because it differs between the Gemini API
and Agent Platform; see .env.example.
"""

import os

from google.adk.agents import LlmAgent

LIVE_MODEL = os.getenv("LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

_DEFINITIONS: dict[str, str] = {
    "closure": (
        "A closure is a function that remembers the variables from the "
        "enclosing scope where it was created, even after that scope has "
        "finished executing. In Python, inner functions automatically close "
        "over names they reference in the enclosing function."
    ),
    "decorator": (
        "A decorator is a callable that takes a function (or class) and "
        "returns a new function (or class), typically adding behavior before "
        "or after the original. The `@decorator` syntax above a def is just "
        "syntactic sugar for `func = decorator(func)`."
    ),
    "generator": (
        "A generator is a function that uses `yield` to produce a sequence "
        "of values lazily. Calling it returns a generator object; values are "
        "computed one at a time when iterated, which makes generators ideal "
        "for streaming or unbounded sequences."
    ),
    "context manager": (
        "A context manager is an object that defines `__enter__` and "
        "`__exit__` methods so it can be used with the `with` statement. It "
        "guarantees setup and teardown around a block: opening files, "
        "acquiring locks, starting transactions."
    ),
    "list comprehension": (
        "A list comprehension is a concise syntax for building a list from "
        "an iterable, with optional filtering: "
        "`[expression for item in iterable if condition]`. It is usually "
        "faster and more readable than the equivalent `for` loop appending "
        "to a list."
    ),
}


def lookup_definition(term: str) -> dict:
    """Looks up a precise definition of a Python concept.

    Use this whenever the learner asks "what is X" or an explanation needs
    canonical wording. Prefer the returned text over a paraphrase for the
    first sentence.

    Args:
        term: The concept to look up, for example "closure", "decorator",
            "generator", "context manager", or "list comprehension".
            Case-insensitive.

    Returns:
        A dict with status, term, and definition. status is "not_found" when
        there is no vetted definition for the term.
    """
    key = (term or "").strip().lower()
    if key in _DEFINITIONS:
        return {"status": "success", "term": key, "definition": _DEFINITIONS[key]}
    return {
        "status": "not_found",
        "term": key,
        "definition": (
            f"No vetted definition for '{term}'. Explain it from general "
            "knowledge and say that no vetted reference was available."
        ),
    }


root_agent = LlmAgent(
    name="decorator_voice_tutor",
    model=LIVE_MODEL,
    instruction=(
        "You are a patient voice tutor whose only topic is Python decorators. "
        "Keep responses short (1 to 3 sentences) so the learner can interrupt "
        "you. Teach progressively: start with closures, then first-class "
        "functions, then a minimal `@my_decorator` example, then real-world "
        "uses (logging, caching, auth). When the learner asks 'what is X', "
        "call the lookup_definition tool first and start your reply with "
        "the returned definition. If they wander off-topic, gently steer "
        "back to decorators."
    ),
    tools=[lookup_definition],
)
