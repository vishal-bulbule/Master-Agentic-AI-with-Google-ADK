# Author: Vishal Bulbule
# Date: 2026-09-22

"""Tool module referenced from root_agent.yaml.

Agent Config imports tools by dotted path, so `get_capital` is referenced in
the YAML as `yaml_config_agent.tools.get_capital`. ADK builds the tool
declaration from the signature and docstring, exactly as for a Python agent.
"""


def get_capital(country: str) -> dict:
    """Returns the capital city of the given country.

    Args:
        country: Country name in English (case-insensitive).

    Returns:
        dict with `status` and either `capital` or `error_message`.
    """
    capitals = {
        "france": "Paris",
        "japan": "Tokyo",
        "india": "New Delhi",
        "germany": "Berlin",
    }
    capital = capitals.get(country.lower())
    if capital is None:
        return {
            "status": "not_found",
            "error_message": f"No capital on record for '{country}'.",
        }
    return {"status": "success", "capital": capital}
