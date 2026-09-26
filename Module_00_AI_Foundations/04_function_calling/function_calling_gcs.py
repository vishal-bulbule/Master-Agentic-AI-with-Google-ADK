# Author: Vishal Bulbule
# Date: 2026-09-22

"""Automatic function calling against a real Google Cloud API.

Pass a plain Python function in `tools` and the SDK does the whole loop:
it sends the declaration, runs `list_buckets` when the model asks for it,
returns the result, and gives you the final answer. The chat API is the
SDK's recommended entry point for automatic function calling.

`list_buckets` makes a live, read-only Cloud Storage call, so this script
needs Application Default Credentials (`gcloud auth application-default login`)
and GOOGLE_CLOUD_PROJECT set, even if you use a Gemini API key for the model.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.cloud import storage

load_dotenv()

client = genai.Client()


def list_buckets() -> dict:
    """Returns the Cloud Storage buckets in the current Google Cloud project.

    Returns:
        dict with `status`, `count` and `buckets` (a list of bucket names).
    """
    storage_client = storage.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])
    names = [b.name for b in storage_client.list_buckets()]
    return {"status": "success", "count": len(names), "buckets": names}


chat = client.chats.create(model="gemini-3.5-flash", config={"tools": [list_buckets]})
response = chat.send_message("How many storage buckets do I have? Name up to five.")

print("Final answer:", response.text)

# The chat history holds the function_call and function_response turns the
# SDK exchanged on your behalf before the final answer.
for content in chat.get_history():
    for part in content.parts or []:
        if part.function_call:
            print(f"Function called: {part.function_call.name}({dict(part.function_call.args or {})})")
        if part.function_response:
            print(f"Function result: {str(part.function_response.response)[:120]}")
