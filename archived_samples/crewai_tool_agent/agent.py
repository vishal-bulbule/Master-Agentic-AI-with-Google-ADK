import os
import sys
sys.path.append("..")
import google.cloud.logging

from dotenv import load_dotenv

from google.genai import types
from google.adk import Agent
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import ScrapeWebsiteTool


load_dotenv()


root_agent = Agent(
    name="crewai_tool_agent",
    model=os.getenv("MODEL"),
    description="Agent to track Google Cloud Changes.",
    instruction="Respond to user based on Google Cloud changes using CrewAI Tool",
    generate_content_config=types.GenerateContentConfig(
        temperature=0
    ),
    tools = [
        CrewaiTool(
            name="check_google_cloud_release_notes",
            description=(
                """Scrapes the latest Google Cloud changes from Official Google cloud release notes webpage.
                Use this tool to get the  updates and changes about Google Cloud products and services."""
            ),
            tool=ScrapeWebsiteTool("https://cloud.google.com/release-notes")
        )
    ]
)