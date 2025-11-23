"""Refund Analysis Agent

Analyzes refund requests and determines eligibility.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from langchain_core.prompts import ChatPromptTemplate
from llm import llm_gpt
from state import AgentState

refund_prompt = ChatPromptTemplate.from_template("""
You are a refund analysis agent.

Analyze the user's query and determine:
1. Whether the user is requesting a refund
2. Whether the product appears eligible for refund
3. What the next action should be

Return ONLY a JSON dictionary with this structure:
{{
  "refund_intent": true/false,
  "eligible": true/false,
  "reason": "short explanation",
  "next_step": "actionable step for the reply agent"
}}

Rules:
- If refund is mentioned, refund_intent = true
- If product is old, damaged, or outside return window → eligible = false
- If information is insufficient → eligible = false, reason = "need_more_info"
- Keep next_step short and actionable

User query: {query}
Product info: {product_info}
""")


def refund_agent(state: AgentState) -> dict:
    """Analyze refund request and determine eligibility.
    
    Args:
        state: Current agent state containing query and product_info
        
    Returns:
        Dictionary with 'refund' key containing refund analysis
    """
    product_info = state.get("product_info")
    
    result = llm_gpt.invoke(refund_prompt.format_messages(
        query=state["query"],
        product_info=product_info if product_info else "No product information available"
    ))

    try:
        refund_data = json.loads(result.content.strip())
        if not isinstance(refund_data, dict):
            raise ValueError("Invalid refund data format")
    except (json.JSONDecodeError, ValueError):
        refund_data = {
            "refund_intent": True,
            "eligible": False,
            "reason": "parse_error",
            "next_step": "Please provide more details about your refund request"
        }

    return {"refund": refund_data}
