<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Fix: missing `__init__.py`

## Symptom

On ADK 2.9, `adk web` lists this agent and `adk run common_failures/broken_no_init`
works, which hides the problem. It shows up when a tool loads the agent
through the package's `__init__.py`. `adk eval` does:

```bash
cd Module_02_First_ADK_Agent/common_failures
adk eval broken_no_init
```

```
FileNotFoundError: [Errno 2] No such file or directory: '.../common_failures/broken_no_init/__init__.py'
```

The same command on a correct agent (`adk eval ../capital_agent`) loads the
agent and prints an empty `Eval Run Summary`, because no eval set was given.

## Why

ADK's dev loader (`adk web`, `adk run`, `adk api_server`) imports
`<folder>.agent` and reads `root_agent` from it. Since Python 3.3 a folder
without `__init__.py` still imports, as a namespace package, so that path
works. `adk eval` loads `<folder>/__init__.py` by file path and expects it to
import `agent`, so it fails. Older ADK versions and other tooling that imports
the package behave the same way. The layout ADK documents, and that `adk
create` generates, always includes `__init__.py`.

## Fix

Create `__init__.py` in the agent folder with one line:

```python
from . import agent
```

Importing the package now imports `agent.py`, and `root_agent` is reachable as
`broken_no_init.agent.root_agent` from every loader.

## Working baseline

`../../capital_agent/__init__.py` has the same one line.
