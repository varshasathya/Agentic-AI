"""Product Information and User History Agents

These agents fetch product information and user history data.
"""

from state import AgentState


def product_api(product_id: str) -> dict:
    """Mock product API call.
    
    Args:
        product_id: Product identifier
        
    Returns:
        Product information dictionary
    """
    return {
        "id": product_id,
        "name": "Kindle Paperwhite",
        "in_stock": True,
        "price": 139.99,
        "warranty": "1 year"
    }


def product_info_agent(state: AgentState) -> dict:
    """Fetch product information based on extracted entities.
    
    Args:
        state: Current agent state containing entities
        
    Returns:
        Dictionary with 'product_info' key
    """
    entities = state.get("entities", {})
    if not isinstance(entities, dict):
        entities = {}
    
    product_id = entities.get("product_id")
    product_info = product_api(product_id) if product_id else None
    
    return {"product_info": product_info}


def user_history_agent(state: AgentState) -> dict:
    """Fetch user history data.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with 'user_history' key
    """
    # Mock user history - in production, this would query a database
    user_history = {
        "previous_issues": 2,
        "vip": True,
        "total_orders": 15,
        "member_since": "2020-01-15"
    }
    
    return {"user_history": user_history}