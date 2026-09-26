<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Fix: the variable must be named `root_agent`

## Symptom

```bash
cd Module_02_First_ADK_Agent/common_failures
adk run broken_wrong_name
```

fails before any model call with:

```
ValueError: No root_agent found for 'broken_wrong_name'. Searched in
'broken_wrong_name.agent.root_agent', 'broken_wrong_name.root_agent' and
'broken_wrong_name/root_agent.yaml'.
```

In `adk web` the agent is listed, and the same error comes back when you send
the first message.

## Why

ADK's loader looks for `<folder>.agent.root_agent`, then
`<folder>.root_agent`, then `<folder>/root_agent.yaml`. The variable name is a
fixed convention, not configurable. `agent`, `my_agent` or `capital_agent_v2`
are all invisible to it. (A module can instead expose an `App` object named
`app`; that is covered in later modules.)

## Fix

Rename the variable:

```python
# Before
my_agent = LlmAgent(...)

# After
root_agent = LlmAgent(...)
```

For a friendlier identity, set `name=` on the `LlmAgent`. That name appears in
events, logs and multi-agent routing; the Python variable must still be
`root_agent`.

The folder is the app. The variable is the root.
