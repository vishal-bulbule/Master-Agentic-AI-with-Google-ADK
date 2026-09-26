# Author: Vishal Bulbule
# Date: 2026-09-22

"""A vague prompt versus one with role, task, constraints and an example.

Both prompts ask for the same refactor. The structured one states who the
model should act as, what exactly to produce, what it must not do, and shows
one input/output pair. Compare how much less the model has to guess.
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

SLOPPY = "fix this code: def add(a,b):return a+b"

STRUCTURED = """You are a senior Python developer. (ROLE)

Task: Refactor the function below for clarity and add a type-hinted
signature and a one-line docstring. (TASK)

Constraints:
- Keep the same behavior
- Don't change the function name
- Output Python only, no markdown fence (CONSTRAINTS)

Example:
Input:  def mul(a,b):return a*b
Output:
def mul(a: int, b: int) -> int:
    \"\"\"Multiply two integers.\"\"\"
    return a * b
(EXAMPLE)

Now refactor this:
def add(a,b):return a+b
"""

for label, prompt in [("SLOPPY", SLOPPY), ("STRUCTURED", STRUCTURED)]:
    print(f"=== {label} ===")
    resp = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
    print(resp.text)
    print()
