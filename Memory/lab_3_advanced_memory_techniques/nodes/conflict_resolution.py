"""Conflict resolution node."""
import uuid
import re
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage

# These will be set in the main notebook
namespace = None
semantic_store = None


def conflict_resolution(state):
    """Resolve conflicts between tool output and memories. Tool output is authoritative."""
    tool_result = state.get("tool_result")
    semantic_memories = state.get("semantic_memories", [])
    
    if not tool_result or "ticket" not in tool_result:
        return {}
    
    # Tool output is authoritative - merge verified facts back into semantic memory
    ticket = tool_result["ticket"]
    ticket_id = tool_result.get("ticket_id", "")
    
    # Extract verified facts from tool output
    verified_facts = []
    if ticket_id:
        verified_facts.append(f"Customer has active ticket {ticket_id}")
    if ticket.get("device") and ticket.get("device") != "-":
        verified_facts.append(f"Customer device: {ticket['device']}")
    if ticket.get("customer_name"):
        verified_facts.append(f"Customer name: {ticket['customer_name']}")
    if ticket.get("status"):
        verified_facts.append(f"Ticket {ticket_id} status: {ticket['status']}")
    
    # Detect conflicts: check if semantic memories contain conflicting information
    conflicts_detected = []
    if semantic_memories:
        # Check for conflicts with ticket ID, device, or customer name
        for memory in semantic_memories:
            memory_content = memory.get('content', '').lower()
            # Check for conflicting ticket IDs
            if ticket_id and f"ticket {ticket_id}" not in memory_content and "ticket" in memory_content:
                # Extract ticket ID from memory if different
                mem_ticket_match = re.search(r'ticket[:\s#]*(\d+)', memory_content)
                if mem_ticket_match and mem_ticket_match.group(1) != ticket_id:
                    conflicts_detected.append(f"Ticket ID conflict: memory had {mem_ticket_match.group(1)}, tool verified {ticket_id}")
            # Check for conflicting device info
            if ticket.get("device") and ticket.get("device") != "-":
                device_lower = ticket.get("device", "").lower()
                if device_lower not in memory_content and ("device" in memory_content or "router" in memory_content):
                    conflicts_detected.append(f"Device conflict detected in memory")
    
    # Update semantic memory with tool-verified facts (overwrites any conflicting memories)
    for fact in verified_facts:
        # Use deterministic keys for overwrite
        if ticket_id:
            key = f"ticket_{ticket_id}_verified"
        else:
            key = f"tool_verified_{uuid.uuid4().hex[:8]}"
        semantic_store.put(namespace, key, fact, metadata={"source": "tool_verified", "timestamp": datetime.now(timezone.utc).isoformat()})
    
    # Build conflict message
    if conflicts_detected:
        conflict_msg = f"Tool output verified. {len(conflicts_detected)} conflict(s) detected and resolved. Conflicting memories have been updated with authoritative tool data."
    else:
        conflict_msg = "Tool output verified. No conflicts detected. Memories updated with tool data."
    
    return {"messages": [SystemMessage(content=conflict_msg)]}

