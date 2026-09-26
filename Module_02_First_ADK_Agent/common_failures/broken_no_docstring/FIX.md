<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Fix: every tool needs a docstring

## Symptom

Also silent in the simplest case. On ADK 2.9 with `gemini-3.5-flash`, "What's
the capital of France?" still calls `get_capital` and answers Paris, because
the function name says what it does. Inspect what the model is actually told:

```bash
cd Module_02_First_ADK_Agent/common_failures
python -c "
from google.adk.tools.function_tool import FunctionTool
from broken_no_docstring.agent import get_capital
print(FunctionTool(get_capital)._get_declaration().description)
"
```

This prints `None`: the tool has no description. (`_get_declaration` is an
internal method, used here only to inspect the declaration.)

The failure shows up as soon as the name is not enough:

- the model never calls the tool, because nothing says it is relevant;
- it calls it with wrong or oddly formatted arguments, because nothing says
  what an argument means (full name or ISO code? any language?);
- with several tools of similar names (`lookup`, `fetch`, `get_info`), it
  picks the wrong one.

## Why

ADK passes the function docstring to the model as the tool's `description`,
and the `Args:` section as the description of each parameter. The model uses
that text to decide whether to call a tool, which one, and what to pass.

## Fix

Add a Google-style docstring. The first line says what the tool does; `Args:`
and `Returns:` describe the inputs and the output.

```python
def get_capital(country: str) -> dict:
    """Returns the capital city of the given country.

    Args:
        country: The country name in English (case-insensitive).

    Returns:
        dict with `status` and either `capital` or `error_message`.
    """
    ...
```

## Rule of thumb

Write the docstring for an engineer who has never seen the tool and cannot
read its code. That is the model's position.
