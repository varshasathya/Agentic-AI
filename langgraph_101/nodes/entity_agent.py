"""Entity Extraction Agent

Extracts structured entities (like product_id) from user queries.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import re
from langchain_core.prompts import ChatPromptTemplate
from llm import llm_gpt
from state import AgentState

entity_prompt = ChatPromptTemplate.from_template("""
Extract structured information from the user query.

Return a JSON object with any relevant entities.
For example: {{"product_id": "12345"}} or {{"order_number": "ORD-789"}}

If no entities are found, return {{}}.

Query: {query}
""")


def entity_agent(state: AgentState) -> dict:
    """Extract entities from user query.
    
    Args:
        state: Current agent state containing the user query
        
    Returns:
        Dictionary with 'entities' key containing extracted entities
    """
    result = llm_gpt.invoke(entity_prompt.format_messages(query=state["query"]))
    content = result.content.strip()
    
    # Try to parse JSON directly
    try:
        entities = json.loads(content)
    except json.JSONDecodeError:
        # Extract JSON from text if embedded
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content)
        if json_match:
            try:
                entities = json.loads(json_match.group())
            except json.JSONDecodeError:
                entities = {}
        else:
            entities = {}
    
    # Ensure entities is a dict
    if not isinstance(entities, dict):
        entities = {}
    
    return {"entities": entities}