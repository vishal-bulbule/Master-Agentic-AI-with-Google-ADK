from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name = "my_first_agent",
    model = "gemini-2.0-flash",
    description = "An example agent that  will answer user query , If can not give answer clearly inform user",
    instruction = """
    You are a helpful assistant that provides information based on user queries.
    """,
    #tools = [google_search]
    )