"""Reply Composer Agent

Generates the final response to the user based on all collected information.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.prompts import ChatPromptTemplate
from llm import llm_gpt
from state import AgentState

reply_prompt = ChatPromptTemplate.from_template("""
You are a helpful customer support agent. Generate a clear, helpful response.

Context:
- User Query: {query}
- Intent: {intent}
- Entities: {entities}
- Product Info: {product_info}
- User History: {user_history}
- Errors: {errors}
- Refund Analysis: {refund}

Rules by intent:

- tech_support:
  • Do NOT ask what the issue is — the user already told you
  • Use errors[] to provide specific troubleshooting steps
  • Be concrete and actionable
  • Escalate if hardware damage is suspected

- product_info:
  • Provide specific product details (name, stock, price, warranty)
  • Be informative and helpful

- order_status:
  • Reference product_id or order data if available
  • Provide clear status information

- refund_request:
  • Explain refund policy clearly
  • Use refund analysis to guide your response
  • Provide next steps

- unknown:
  • Ask ONE specific clarifying question
  • Do not ask generic questions like "How can I help?"
""")


def reply_agent(state: AgentState) -> dict:
    """Generate final reply to user.
    
    Args:
        state: Current agent state with all collected information
        
    Returns:
        Dictionary with 'reply' key containing the final response
    """
    result = llm_gpt.invoke(reply_prompt.format_messages(
        query=state.get("query", ""),
        intent=state.get("intent", "unknown"),
        entities=state.get("entities", {}),
        product_info=state.get("product_info"),
        user_history=state.get("user_history"),
        errors=state.get("errors", []),
        refund=state.get("refund"),
    ))
    
    reply = result.content.strip()
    return {"reply": reply}



    
