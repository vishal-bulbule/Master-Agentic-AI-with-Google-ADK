<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Fix: tool parameters need type hints

## Symptom

This one is silent. On ADK 2.9 with `gemini-3.5-flash`, asking "What's the
capital of France?" still produces a `get_capital(country="France")` call and
the right answer: the parameter name and docstring are enough for the model
to guess a string. The bug is in what the model is told, not in this one
answer. Look at the declaration ADK sends:

```bash
cd Module_02_First_ADK_Agent/common_failures
python -c "
from google.adk.tools.function_tool import FunctionTool
from broken_no_type_hint.agent import get_capital
print(FunctionTool(get_capital)._get_declaration().parameters_json_schema)
"
```

```
{'properties': {'country': {'title': 'Country'}}, 'required': ['country'], ...}
```

`country` has no `type`. With a typed signature the same property reads
`{'title': 'Country', 'type': 'string'}`. (`_get_declaration` is an internal
method, used here only to inspect the schema. In `adk web` you can see the
same declaration in the request shown for a model call in the trace view.)

Without types, the model is free to send `42`, `["France"]` or `{"name":
"France"}`. The more parameters a tool has, and the less obvious their names,
the more often that happens, and the tool then fails inside your code
(`country.lower()` on a non-string raises `AttributeError`) instead of the
model sending the right shape in the first place.

## Why

ADK converts the function signature into the JSON schema the model uses to
decide whether and how to call the tool. Type hints are the only source of
the parameter types. The docstring describes meaning; it does not set types.

## Fix

Add a type hint to every parameter and to the return value:

```python
# Before
def get_capital(country):
    ...

# After
def get_capital(country: str) -> dict:
    ...
```

For more complex tools:

```python
def search(query: str, limit: int = 10, include_archived: bool = False) -> dict:
    ...
```

## Companion rule

Tools should return a `dict` with a `status` key. Every agent in this
repository follows that convention; it gives the model a structured way to
tell success from failure.
