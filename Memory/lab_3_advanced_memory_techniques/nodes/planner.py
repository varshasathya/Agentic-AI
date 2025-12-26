"""Planner node."""
import json
from langchain_core.messages import HumanMessage, AIMessage
from memory_stores.procedural_memory import ProceduralMemory
from utils.extract_json import extract_json_from_response

# LLM will be set in the main notebook
llm = None


def planner_node(state):
    """Select procedure, choose tool, and extract arguments from user input."""
    # Get all available procedures with their allowed tools
    procedures_info = {}
    for proc_id, proc in ProceduralMemory.PROCEDURES.items():
        procedures_info[proc_id] = {
            "name": proc["name"],
            "allowed_tools": proc.get("allowed_tools", [])
        }
    procedures_text = json.dumps(procedures_info, indent=2)
    
    # Get context from state
    semantic_memories = state.get("semantic_memories", [])
    episodic_memories = state.get("episodic_memories", [])
    semantic_count = len(semantic_memories)
    episodic_count = len(episodic_memories)
    
    # Extract semantic memory content for the prompt
    semantic_content = ""
    if semantic_memories:
        semantic_content = "\n".join([
            f"- {mem.get('content', str(mem))}" 
            # Limit to first 5 to avoid token limits
            #Note: Ideally you can summarize the memory content to a few sentences or key points.
            for mem in semantic_memories[:5]  
        ])
    else:
        semantic_content = "None"
    
    # Extract episodic memory content for the prompt
    episodic_content = ""
    if episodic_memories:
        episodic_content = "\n".join([
            f"- {mem.get('content', str(mem))}" 
            # Limit to first 5 to avoid token limits
            #Note: Ideally you can summarize the memory content to a few sentences or key points.
            for mem in episodic_memories[:5]  
        ])
    else:
        episodic_content = "None"
    
    # Build planning prompt
    planning_prompt = f"""You are a CRM support planner. Your job is to:
1. Select the appropriate procedure based on the user's query
2. Choose the appropriate tool from that procedure's allowed tools
3. Extract all required arguments from the conversation history and memories

AVAILABLE PROCEDURES:
{procedures_text}

PROCEDURE SELECTION RULES:
- standard_support: For new issues, general support, ticket creation/updates
- quick_resolution: For simple lookups, status checks (only lookup_ticket allowed)
- escalated_support: For critical issues, escalations (lookup_ticket and update_ticket only)

CONTEXT:
- Semantic memories ({semantic_count} found):
{semantic_content}
- Episodic memories ({episodic_count} found):
{episodic_content}

TOOL SELECTION AND ARGUMENT EXTRACTION:

1. For create_ticket (if in allowed_tools):
   - REQUIRED: Extract customer_name from messages like "I'm X" or "Hi, I'm X"
   - REQUIRED: Extract issue from the problem description
   - OPTIONAL: Extract device if mentioned, otherwise use "-"
   - OPTIONAL: priority (default: "Medium")
   - Only use if NO tickets exist in memories or conversation history
   - Example: {{"tool": "create_ticket", "arguments": {{"customer_name": "Cody", "issue": "slow internet speeds", "device": "-", "priority": "Medium"}}}}

2. For update_ticket (if in allowed_tools):
   - REQUIRED: Extract ticket_id from semantic memories (shown above) or conversation history
   - Look for ticket_id in semantic memories - they may contain text like "ticket_id: 998880" or "Ticket 998880"
   - OPTIONAL: Extract note from new information provided in the user's message
   - OPTIONAL: Extract device if mentioned
   - OPTIONAL: Extract status if mentioned
   - Use when tickets exist in semantic memories AND user provides additional details
   - Example: {{"tool": "update_ticket", "arguments": {{"ticket_id": "998880", "note": "Customer tried restarting modem"}}}}

3. For lookup_ticket (if in allowed_tools):
   - REQUIRED: Extract ticket_id from semantic memories or user message
   - If user says "my ticket" and ticket exists in semantic memories, use that ticket_id
   - Example: {{"tool": "lookup_ticket", "arguments": {{"ticket_id": "998880"}}}}

ARGUMENT EXTRACTION RULES:
- Look through ALL conversation messages and semantic memories (shown above) to find:
  * customer_name: patterns like "I'm X", "Hi, I'm X", "My name is X"
  * issue: the problem description
  * device: device models mentioned
  * ticket_id: CRITICAL - Extract from semantic memories. Look for patterns like "ticket_id: 123456", "Ticket 123456", or "ticket 123456" in the semantic memories shown above
- IMPORTANT: If semantic memories contain a ticket_id and the user provides additional information (device details, troubleshooting steps, updates), you MUST use update_ticket with that ticket_id
- Extract arguments from the latest user message and relevant conversation history
- If ticket_id is missing for update_ticket, check semantic memories again - they should contain the ticket information

Return ONLY JSON (no other text):
{{
  "procedure": "standard_support" | "quick_resolution" | "escalated_support",
  "tool": "create_ticket" | "update_ticket" | "lookup_ticket",
  "arguments": {{
    "customer_name": "...",  // for create_ticket
    "issue": "...",          // for create_ticket
    "device": "...",         // optional
    "priority": "Medium",    // optional for create_ticket
    "ticket_id": "...",      // for lookup_ticket/update_ticket
    "note": "...",           // optional for update_ticket
    "status": "..."          // optional for update_ticket
  }}
}}
"""
    
    # Call LLM to select procedure, tool, and extract arguments
    messages = state["messages"] + [HumanMessage(content=planning_prompt)]
    out = llm.invoke(messages)
    content = extract_json_from_response(out.content)
    
    # Parse JSON
    procedure_name = "standard_support"
    plan_tool = "lookup_ticket"
    tool_arguments = {}
    
    try:
        plan = json.loads(content)
        procedure_name = plan.get("procedure", "standard_support")
        if procedure_name not in ProceduralMemory.PROCEDURES:
            procedure_name = "standard_support"
        
        # Get allowed tools for selected procedure
        procedure = ProceduralMemory.PROCEDURES[procedure_name]
        allowed_tools = procedure.get("allowed_tools", [])
        
        # Get selected tool
        selected_tool = plan.get("tool", "")
        
        # Validate tool is in allowed_tools
        if selected_tool in allowed_tools:
            plan_tool = selected_tool
        elif allowed_tools:
            plan_tool = allowed_tools[0]  # Default to first allowed tool
        
        # Get arguments
        tool_arguments = plan.get("arguments", {})
        if tool_arguments is None:
            tool_arguments = {}
            
    except json.JSONDecodeError:
        # Fallback: use default procedure and first allowed tool
        procedure = ProceduralMemory.PROCEDURES["standard_support"]
        allowed_tools = procedure.get("allowed_tools", [])
        if allowed_tools:
            plan_tool = allowed_tools[0]
        tool_arguments = {}
    except Exception:
        # Fallback: use default procedure and first allowed tool
        procedure = ProceduralMemory.PROCEDURES["standard_support"]
        allowed_tools = procedure.get("allowed_tools", [])
        if allowed_tools:
            plan_tool = allowed_tools[0]
        tool_arguments = {}
    
    # Get allowed tools for return
    procedure = ProceduralMemory.PROCEDURES[procedure_name]
    allowed_tools = procedure.get("allowed_tools", [])
    
    # Build final plan JSON
    final_plan = {
        "procedure": procedure_name,
        "tool": plan_tool,
        "arguments": tool_arguments
    }
    
    return {
        "messages": [AIMessage(content=json.dumps(final_plan))],
        "selected_procedure": procedure_name,
        "allowed_tools": allowed_tools,
        "planner_action": "tool",
        "planner_tool": plan_tool,
        "planner_arguments": tool_arguments
    }

