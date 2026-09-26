<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02: Return Value Status Patterns

## What this shows

Three tools, three status patterns. A short, predictable `status` field lets
the model choose between using the data (`success`), explaining a problem
(`error`), and asking a clarifying question (`ambiguous`), without that
logic being spelled out in the prompt. Returning an error dict instead of
raising keeps the failure visible to the model.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_04_Custom_Tools/02_return_value_status`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "Find Asha"

Terminal alternative: `adk run agent`.

## Try it

| Tool | Status it returns | Prompt |
|---|---|---|
| `get_employee` | `success` / `error` | "Look up E-042", then "Look up E-999" |
| `divide` | `success` / `error` | "Divide 10 by 0" |
| `find_employee_by_name` | `success` / `error` / `ambiguous` | "Find Asha" (ambiguous), "Find Karan" (success) |

## What to look for

- "Find Asha": the function response has `status: ambiguous` and two
  `options`; the agent lists both and asks which one.
- "Divide 10 by 0": no exception. The response carries `error_message` and
  the agent asks for a non-zero denominator.
