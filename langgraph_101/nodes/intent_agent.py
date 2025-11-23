"""Intent Classification Agent

Classifies user queries into one of: order_status, product_info, 
tech_support, refund_request, or unknown.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.prompts import ChatPromptTemplate
from llm import llm_gpt
from state import AgentState

intent_prompt = ChatPromptTemplate.from_template("""
Classify the user's intent into one of these categories:
- order_status
- product_info
- tech_support
- refund_request
- unknown

Return ONLY the intent value, nothing else.

Query: {query}
""")


def intent_agent(state: AgentState) -> dict:
    """Classify user query intent.
    
    Args:
        state: Current agent state containing the user query
        
    Returns:
        Dictionary with 'intent' key containing the classified intent
    """
    result = llm_gpt.invoke(intent_prompt.format_messages(query=state["query"]))
    intent = result.content.strip().lower()  
    return {"intent": intent}