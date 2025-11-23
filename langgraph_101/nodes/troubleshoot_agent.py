"""Technical Troubleshooting Agent

Identifies technical issues and returns structured error codes.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from langchain_core.prompts import ChatPromptTemplate
from llm import llm_gpt
from state import AgentState

troubleshoot_prompt = ChatPromptTemplate.from_template("""
You are a technical troubleshooting agent.

Analyze the user's query and identify the technical issues.
Return a JSON array of error codes.

Valid error codes:
- "device_not_powering_on"
- "possible_hardware_damage"
- "battery_issue"
- "screen_unresponsive"
- "charging_issue"
- "unknown_issue"

Rules:
- ALWAYS return a JSON array (e.g., ["device_not_powering_on"])
- If no clear issue is found, return ["unknown_issue"]

User query: {query}
""")


def troubleshoot_agent(state: AgentState) -> dict:
    """Identify technical issues from user query.
    
    Args:
        state: Current agent state containing the user query
        
    Returns:
        Dictionary with 'errors' key containing list of error codes
    """
    result = llm_gpt.invoke(troubleshoot_prompt.format_messages(query=state["query"]))
    
    try:
        errors = json.loads(result.content.strip())
        if not isinstance(errors, list):
            errors = []
    except json.JSONDecodeError:
        errors = ["unknown_issue"]
    
    return {"errors": errors}