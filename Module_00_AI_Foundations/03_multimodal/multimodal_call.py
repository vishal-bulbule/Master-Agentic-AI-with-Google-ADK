# Author: Vishal Bulbule
# Date: 2026-09-22

"""Send an image and a text prompt in one Gemini call.

`contents` accepts a list that mixes strings and PIL images; the SDK converts
each image into an inline image part. The model reads both together.

Pass your own image path as an argument. With no argument, the script draws a
small bar chart with Pillow so it runs without any setup.

Run:
    python multimodal_call.py
    python multimodal_call.py path/to/screenshot.png
"""

import sys

from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageDraw

load_dotenv()

client = genai.Client()


def sample_chart() -> Image.Image:
    """Draws a bar chart of monthly signups that grows from January to June."""
    img = Image.new("RGB", (480, 320), "white")
    draw = ImageDraw.Draw(img)
    draw.text((150, 10), "Monthly signups, Jan to Jun", fill="black")
    values = [40, 55, 70, 90, 120, 160]
    for i, value in enumerate(values):
        x = 40 + i * 70
        draw.rectangle([x, 290 - value, x + 45, 290], fill="steelblue")
        draw.text((x + 10, 295), ["Jan", "Feb", "Mar", "Apr", "May", "Jun"][i], fill="black")
        draw.text((x + 10, 275 - value), str(value), fill="black")
    return img


img = Image.open(sys.argv[1]) if len(sys.argv) > 1 else sample_chart()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=["Describe this image in 2 sentences. If it is a chart, summarize the trend.", img],
)

print(response.text)
