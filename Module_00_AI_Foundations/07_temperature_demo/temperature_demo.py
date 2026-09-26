# Author: Vishal Bulbule
# Date: 2026-09-22

"""Run one prompt three times at three temperatures and compare the variance.

Low temperature makes the model pick the most likely tokens, so repeated runs
look alike. High temperature spreads the choice and runs diverge.

Gemini 3.x models are tuned for the default temperature of 1.0, and Google
recommends not lowering it: values below 1.0 can cause looping or weaker
reasoning. For consistent agent behavior on these models, use a precise
system instruction and structured output rather than temperature 0.
Thinking is set to MINIMAL only to keep the nine calls fast and cheap.
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

prompt = "Reply with one 3-word product tagline for an AI coding assistant and nothing else."

for temp in (0.0, 0.3, 1.0):
    print(f"\n=== temperature = {temp} ===")
    for run in range(3):
        resp = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temp,
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            ),
        )
        print(f"  run {run + 1}: {resp.text.strip()}")
