import os
import sys
sys.path.append("..")
from google.adk import Agent

from google.adk.agents import Agent
import requests
import json
import sys
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# GITHUB_USERNAME = "vishal-bulbule"
# GITHUB_TOKEN = "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"

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def github_create_repo_tool(repo_name: str, description: str = "", private: bool = True):
    """
    Creates a new repository on GitHub.

    This function uses the GitHub API to create a new repository under the
    specified user account. It requires a GitHub username and a Personal Access
    Token with the 'repo' scope.

    Args:
        repo_name (str): The name of the new repository.
        description (str): A brief description of the repository. Defaults to "".
        private (bool): If True, creates a private repository. Defaults to True.
    """
    api_url = f"https://api.github.com/user/repos"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": False  # We'll initialize it locally and push later
    }
    
    print(f"Attempting to create GitHub repository: {repo_name}")

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        repo_data = response.json()
        print(f"Successfully created GitHub repository: {repo_data['html_url']}")
        print("Use the following commands to link your local repository:")
        print(f"  git remote add origin {repo_data['clone_url']}")
        print(f"  git push -u origin main")

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 422:
            print(f"Error: A repository with the name '{repo_name}' already exists.", file=sys.stderr)
        else:
            print(f"HTTP Error: {err}", file=sys.stderr)
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

def github_delete_repo_tool(repo_name: str):
    """
    Deletes a repository on GitHub.

    This function uses the GitHub API to delete a repository. This action
    is irreversible and should be used with caution.

    Args:
        repo_name (str): The name of the repository to delete.
    """
    if not GITHUB_USERNAME:
        print("Error: GitHub username not found. Please set the GITHUB_USERNAME environment variable in your .env file.", file=sys.stderr)
        return

    if not GITHUB_TOKEN:
        print("Error: GitHub token not found. Please set the GITHUB_TOKEN environment variable in your .env file.", file=sys.stderr)
        return

    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print(f"Attempting to delete GitHub repository: {repo_name}")
    
    try:
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status()
        
        if response.status_code == 204:
            print(f"Successfully deleted GitHub repository: {repo_name}")
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            print(f"Error: Repository '{repo_name}' not found.", file=sys.stderr)
        elif err.response.status_code == 403:
            print(f"Error: Forbidden. Check if your token has the necessary permissions to delete this repository.", file=sys.stderr)
        else:
            print(f"HTTP Error: {err}", file=sys.stderr)
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Agent using the tool
root_agent = Agent(
    name="github_repo_agent",
    model="gemini-2.0-flash",
    description="Agent that creates & delete GitHub repositories.",
    instruction="""
    If user want to create repository Ask the user for repo details (name, description, private/public) before creating.
    If user want to delete repository Ask the user for repo name before deleting.
    Always confirm with the user before deleting a repository as this action is irreversible.
    """,
    tools=[github_create_repo_tool,github_delete_repo_tool]
)
