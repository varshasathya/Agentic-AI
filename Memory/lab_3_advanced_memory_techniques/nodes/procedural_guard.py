"""
Procedural guard node - Adds procedural context and handles escalation detection.

This node is currently not used in the graph but kept for reference. It can be integrated after the planner
to add procedure-specific context (steps, tool rules) to messages for downstream nodes, or after tool execution
to detect escalations based on ticket status/priority and automatically switch to escalated_support procedure.
Useful for enforcing procedural workflows and automatic escalation management.

Currently planner node is responsible for selecting the procedure and tool.
But it does not handle escalations.
This node is responsible for handling escalations.
It checks the ticket status/priority and automatically switches to escalated_support procedure if needed.
It also adds the procedural context to the messages for downstream nodes.
It also adds the escalation information to the messages for downstream nodes.
It also adds the allowed tools to the messages for downstream nodes.
It also adds the selected procedure to the messages for downstream nodes.
"""
import json
from langchain_core.messages import SystemMessage
from memory_stores.procedural_memory import ProceduralMemory


def procedural_guard(state):
    """Add procedural context and check for escalations."""
    selected_procedure = state.get("selected_procedure", "standard_support")
    procedure = ProceduralMemory.PROCEDURES.get(selected_procedure, ProceduralMemory.PROCEDURES["standard_support"])
    
    # Add procedural context for tool execution and response node
    procedure_name = procedure.get('name', 'Unknown Procedure')
    steps_text = "\n".join(procedure['steps'])
    tool_rules_text = json.dumps(ProceduralMemory.TOOL_USAGE_RULES, indent=2)
    
    procedural_prompt = f"""
    You are following the {procedure_name} procedure.

    STEPS:
    {steps_text}

    TOOL USAGE RULES:
    {tool_rules_text}

    You MUST follow this procedure. Do not deviate.
    """
    
    # Check for escalation (after tool execution in previous turn)
    tool_result = state.get("tool_result")
    escalation_info = None
    
    if tool_result and "ticket" in tool_result:
        ticket = tool_result.get("ticket", {})
        escalation_info = ProceduralMemory.get_escalation_decision(ticket)
        if escalation_info:
            # Auto-escalate to escalated_support procedure
            return {
                "selected_procedure": "escalated_support",
                "allowed_tools": ProceduralMemory.PROCEDURES["escalated_support"].get("allowed_tools", []),
                "escalation_info": escalation_info,
                "messages": [
                    SystemMessage(content=procedural_prompt),
                    SystemMessage(content=f"ESCALATION: {escalation_info['message']}")
                ]
            }
    
    messages = [SystemMessage(content=procedural_prompt)]
    if escalation_info:
        messages.append(SystemMessage(content=f"ESCALATION: {escalation_info['message']}"))
    
    return {"messages": messages, "escalation_info": escalation_info}
