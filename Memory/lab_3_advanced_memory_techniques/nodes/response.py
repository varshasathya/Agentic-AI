"""Response generation node."""
import json
from langchain_core.messages import SystemMessage, AIMessage

# LLM will be set in the main notebook
llm = None


def response_node(state):
    """Generate response using all memories and tool results."""
    msgs = state["messages"].copy()
    
    # Filter out planner's JSON output
    filtered_msgs = []
    for m in msgs:
        if isinstance(m, AIMessage) and hasattr(m, 'content') and isinstance(m.content, str):
            content = m.content.strip()
            # Skip if it's just a JSON object (planner output)
            if content.startswith('{') and content.endswith('}'):
                try:
                    parsed = json.loads(content)
                    if "action" in parsed or "create_ticket" in parsed or "lookup_ticket" in parsed or "update_ticket" in parsed:
                        continue  # Skip planner JSON
                except:
                    if '"create_ticket"' in content or '"lookup_ticket"' in content or '"update_ticket"' in content or '"action"' in content:
                        continue  # Skip it
        filtered_msgs.append(m)
    msgs = filtered_msgs
    
    # Add tool result if present (if not already added by tool_node)
    tool_result = state.get("tool_result")
    tool_result_in_messages = any(
        isinstance(m, SystemMessage) and "Tool" in m.content 
        for m in msgs
    )
    
    if tool_result and not tool_result_in_messages:
        result_text = json.dumps(tool_result, indent=2)
        msgs.append(SystemMessage(content=f"Tool execution result: {result_text}"))
    
    # Add system instruction (memories are already in messages from read nodes)
    response_system = """You are a CRM support agent with multi-memory access.

    RULES:
    - Use semantic memories for facts (ticket IDs, device models, speed plans)
    - Use episodic memories to avoid repeating past suggestions
    - Respect user preferences (tone, detail level)
    - Tool output is authoritative (overrides memories)
    - Show that you remember past conversations
    - Only use ticket IDs from tool results or semantic memory
    - If no ticket exists, clearly state that

    Keep responses helpful and concise. When a ticket is created, explicitly state the ticket number."""
    
    if not any(isinstance(m, SystemMessage) and "CRM support agent" in m.content for m in msgs):
        msgs = [SystemMessage(content=response_system)] + msgs
    
    # Generate response
    reply = llm.invoke(msgs)
    return {"messages": [reply]}
