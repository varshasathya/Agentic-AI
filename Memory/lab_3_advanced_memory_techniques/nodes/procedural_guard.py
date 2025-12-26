"""
Procedural guard node - Enforces procedure rules: selects tool and extracts arguments based on selected procedure.

After planner selects a procedure, this node enforces the procedure's rules by selecting the appropriate tool
from allowed_tools and extracting required arguments. It also handles escalation detection and adds procedural
context to messages for downstream nodes.
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from memory_stores.procedural_memory import ProceduralMemory
from utils.extract_json import extract_json_from_response

# LLM will be set in the main notebook
llm = None


def procedural_guard(state):
    """Enforce procedure rules: select tool and extract arguments based on selected procedure."""
    selected_procedure = state.get("selected_procedure", "standard_support")
    procedure = ProceduralMemory.PROCEDURES.get(selected_procedure, ProceduralMemory.PROCEDURES["standard_support"])
    
    # Get allowed tools for this procedure
    allowed_tools = procedure.get("allowed_tools", [])
    procedure_name = procedure.get('name', 'Unknown Procedure')
    steps_text = "\n".join(procedure['steps'])
    tool_rules_text = json.dumps(ProceduralMemory.TOOL_USAGE_RULES, indent=2)
    
    # Get context from state
    semantic_memories = state.get("semantic_memories", [])
    episodic_memories = state.get("episodic_memories", [])
    
    # Extract semantic memory content for the prompt
    semantic_content = ""
    if semantic_memories:
        semantic_content = "\n".join([
            f"- {mem.get('content', str(mem))}" 
            for mem in semantic_memories[:5]
        ])
    else:
        semantic_content = "None"
    
    # Extract episodic memory content for the prompt
    episodic_content = ""
    if episodic_memories:
        episodic_content = "\n".join([
            f"- {mem.get('content', str(mem))}" 
            for mem in episodic_memories[:5]
        ])
    else:
        episodic_content = "None"
    
    # Build prompt for tool selection and argument extraction
    guard_prompt = f"""You are enforcing the {procedure_name} procedure.

PROCEDURE STEPS:
{steps_text}

ALLOWED TOOLS FOR THIS PROCEDURE:
{json.dumps(allowed_tools, indent=2)}

TOOL USAGE RULES:
{tool_rules_text}

CONTEXT:
- Semantic memories:
{semantic_content}
- Episodic memories:
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
    
    # Call LLM to select tool and extract arguments
    messages = state["messages"] + [HumanMessage(content=guard_prompt)]
    out = llm.invoke(messages)
    content = extract_json_from_response(out.content)
    
    # Parse JSON
    plan_tool = "lookup_ticket"
    tool_arguments = {}
    
    try:
        plan = json.loads(content)
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
            
    except (json.JSONDecodeError, Exception):
        # Fallback: use first allowed tool
        if allowed_tools:
            plan_tool = allowed_tools[0]
        tool_arguments = {}
    
    # Add procedural context for downstream nodes
    procedural_prompt = f"""
    You are following the {procedure_name} procedure.

    STEPS:
    {steps_text}

    TOOL USAGE RULES:
    {tool_rules_text}

    You MUST follow this procedure. Do not deviate.
    """
    
    # Check for escalation (from previous tool execution)
    tool_result = state.get("tool_result")
    escalation_info = None
    
    if tool_result and "ticket" in tool_result:
        ticket = tool_result.get("ticket", {})
        escalation_info = ProceduralMemory.get_escalation_decision(ticket)
        if escalation_info:
            # Auto-escalate to escalated_support procedure
            escalated_procedure = ProceduralMemory.PROCEDURES["escalated_support"]
            return {
                "selected_procedure": "escalated_support",
                "allowed_tools": escalated_procedure.get("allowed_tools", []),
                "escalation_info": escalation_info,
                "planner_action": "tool",
                "planner_tool": plan_tool,
                "planner_arguments": tool_arguments,
                "messages": [
                    SystemMessage(content=procedural_prompt),
                    SystemMessage(content=f"ESCALATION: {escalation_info['message']}"),
                    AIMessage(content=json.dumps({"tool": plan_tool, "arguments": tool_arguments}))
                ]
            }
    
    # Build final plan JSON
    final_plan = {
        "tool": plan_tool,
        "arguments": tool_arguments
    }
    
    messages = [
        SystemMessage(content=procedural_prompt),
        AIMessage(content=json.dumps(final_plan))
    ]
    if escalation_info:
        messages.append(SystemMessage(content=f"ESCALATION: {escalation_info['message']}"))
    
    return {
        "messages": messages,
        "escalation_info": escalation_info,
        "planner_action": "tool",
        "planner_tool": plan_tool,
        "planner_arguments": tool_arguments,
        "allowed_tools": allowed_tools
    }
