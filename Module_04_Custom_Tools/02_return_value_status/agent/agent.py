# Author: Vishal Bulbule
# Date: 2026-09-22

"""Return-value patterns: success, error, and ambiguous status dicts.

The model reads a tool's return value as data. A short, predictable `status`
field tells it what to do next:
    success    use the data
    error      explain `error_message` to the user
    ambiguous  present `options` and ask the user to pick

Returning an error dict instead of raising keeps the failure visible to the
model, so it can recover in conversation.
"""

from google.adk.agents import LlmAgent


def get_employee(emp_id: str) -> dict:
    """Looks up an employee by exact employee ID.

    Args:
        emp_id: The exact employee ID, for example `E-042`.

    Returns:
        `status` "success" with the `employee` record, or `status` "error"
        with a human-readable `error_message` when no match exists.
    """
    db = {"E-042": {"name": "Asha Rao", "team": "platform"}}
    if emp_id.upper() not in db:
        return {
            "status": "error",
            "error_message": f"No employee with ID {emp_id!r}. Ask the user to double-check.",
        }
    return {"status": "success", "employee": db[emp_id.upper()]}


def divide(numerator: float, denominator: float) -> dict:
    """Divides `numerator` by `denominator`.

    Args:
        numerator: The top of the fraction.
        denominator: The bottom of the fraction. Must be non-zero.

    Returns:
        `status` "success" with `result`, or `status` "error" with an
        `error_message` when the denominator is zero.
    """
    if denominator == 0:
        return {
            "status": "error",
            "error_message": "Cannot divide by zero. Ask the user for a non-zero denominator.",
        }
    return {"status": "success", "result": numerator / denominator}


def find_employee_by_name(name: str) -> dict:
    """Searches employees by case-insensitive, partial name match.

    Args:
        name: A full or partial name to search for.

    Returns:
        `status` "success" with one `employee`; `status` "ambiguous" with a
        `message` and the candidate `options` when several match; or
        `status` "error" when nothing matches.
    """
    roster = [
        {"id": "E-042", "name": "Asha Rao", "team": "platform"},
        {"id": "E-117", "name": "Asha Mehta", "team": "growth"},
        {"id": "E-208", "name": "Karan Singh", "team": "platform"},
    ]
    needle = name.strip().lower()
    matches = [row for row in roster if needle in row["name"].lower()]
    if not matches:
        return {"status": "error", "error_message": f"No employee matches {name!r}."}
    if len(matches) > 1:
        return {
            "status": "ambiguous",
            "message": f"Multiple employees match {name!r}. Ask the user which one they meant.",
            "options": matches,
        }
    return {"status": "success", "employee": matches[0]}


root_agent = LlmAgent(
    name="status_patterns_agent",
    model="gemini-3.5-flash",
    description="Demonstrates the three return-status patterns.",
    instruction=(
        "Help the user query employee records and do basic math. "
        "When a tool returns status='ambiguous', present the options and ask which to pick. "
        "When status='error', read the error_message and explain it plainly."
    ),
    tools=[get_employee, divide, find_employee_by_name],
)
