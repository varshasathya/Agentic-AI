"""Agent State Definition

Defines the shared state structure used across all agents in the graph.
"""

from typing import TypedDict, Optional, Dict, Any, List


class AgentState(TypedDict, total=False):
    """State shared across all agents in the customer support graph.
    
    All fields except 'query' are optional and can be set by different agents.
    """
    query: str  # User's original query
    intent: Optional[str]  # Classified intent (set by intent_agent)
    entities: Dict[str, Any]  # Extracted entities (set by entity_agent)
    product_info: Optional[Dict[str, Any]]  # Product data (set by product_info_agent)
    user_history: Optional[Dict[str, Any]]  # User history (set by user_history_agent)
    errors: List[str]  # Error codes (set by troubleshoot_agent)
    refund: Optional[Dict[str, Any]]  # Refund analysis (set by refund_agent)
    reply: Optional[str]  # Final response (set by reply_agent)