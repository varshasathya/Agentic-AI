"""Salience-gated memory write node."""
import json
import uuid
import re
from langchain_core.messages import SystemMessage, HumanMessage
from utils.extract_json import extract_json_from_response

# These will be set in the main notebook
namespace = None
llm = None
salience_scorer = None
semantic_store = None
episodic_store = None


def salience_gated_memory_write(state):
    """Write to memory stores only if salience threshold met or explicit trigger."""
    # Get recent conversation
    recent = state["messages"][-6:] if len(state["messages"]) >= 6 else state["messages"]
    conversation = "\n".join([f"{type(m).__name__}: {m.content}" for m in recent])
    
    tool_result = state.get("tool_result")
    
    # Check for explicit triggers (ticket lifecycle events)
    explicit_trigger = False
    if tool_result:
        if "ticket_id" in tool_result and tool_result.get("status") in ["created", "updated"]:
            explicit_trigger = True
        if "ticket" in tool_result and tool_result["ticket"].get("status") in ["Escalated", "Resolved"]:
            explicit_trigger = True
    
    # Compute salience scores
    scores = salience_scorer.compute_salience(conversation, tool_result)
    
    should_write = salience_scorer.should_write(scores, threshold=0.6, explicit_trigger=explicit_trigger)
    
    if not should_write:
        return {"salience_scores": scores, "memory_written": False}
    
    # Extract memories using LLM
    EXTRACT_PROMPT = """
    Extract structured memories from this conversation.

    SEMANTIC (facts, structured data):
    - Ticket IDs, device models, house layout, technical specs
    - Format: "Customer has [device] in [location]. Ticket [ID]."

    EPISODIC (experiences, what happened):
    - What troubleshooting was tried, what was suggested, user corrections
    - Format: "Customer tried [action]. Agent suggested [action]."

    Return JSON:
    {"semantic": ["fact1", "fact2"], "episodic": ["experience1", "experience2"]}
    """
    
    response = llm.invoke([
        SystemMessage(content=EXTRACT_PROMPT),
        HumanMessage(content=conversation)
    ])
    
    content = extract_json_from_response(response.content)
    
    try:
        memories = json.loads(content)
        
        # Write semantic memories with deterministic keys for overwrite support
        semantic_count = 0
        for i, fact in enumerate(memories.get("semantic", [])):
            if len(fact.strip()) > 10:
                # Extract deterministic key from fact (e.g., ticket_id, device_model)
                # This enables overwrite/consolidation
                key = None
                fact_lower = fact.lower()
                
                # Try to extract ticket ID
                ticket_match = re.search(r'ticket[:\s#]*(\d+)', fact_lower)
                if ticket_match:
                    key = f"ticket_{ticket_match.group(1)}"
                # Try to extract device model
                elif "router" in fact_lower or "device" in fact_lower:
                    device_match = re.search(r'(netgear|archer|nighthawk|router[-\s]*[a-z0-9]+)', fact_lower)
                    if device_match:
                        key = f"device_{device_match.group(1).replace(' ', '_')}"
                # Try to extract customer name
                elif "customer" in fact_lower:
                    name_match = re.search(r'customer[:\s]+([a-z]+)', fact_lower)
                    if name_match:
                        key = f"customer_{name_match.group(1)}"
                
                # Fallback to UUID if no deterministic key found
                if not key:
                    key = f"semantic_{uuid.uuid4().hex[:8]}"
                
                # Upsert (overwrites if key exists)
                semantic_store.put(namespace, key, fact)
                semantic_count += 1
        
        # Write episodic memories (keep UUID keys - these are experiences, not facts)
        episodic_count = 0
        for i, experience in enumerate(memories.get("episodic", [])):
            if len(experience.strip()) > 10:
                key = f"episodic_{uuid.uuid4().hex[:8]}"
                salience = scores.get("importance", 0.5)
                episodic_store.put(namespace, key, experience, salience_score=salience)
                episodic_count += 1
        
    except Exception as e:
        pass
    
    return {
        "salience_scores": scores,
        "memory_written": True,
        "semantic_written_count": semantic_count,
        "episodic_written_count": episodic_count
    }

