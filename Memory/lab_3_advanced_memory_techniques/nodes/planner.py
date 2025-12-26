"""Planner node."""
import json
from langchain_core.messages import HumanMessage
from memory_stores.procedural_memory import ProceduralMemory
from utils.extract_json import extract_json_from_response

# LLM will be set in the main notebook
llm = None


def planner_node(state):
    """Select appropriate procedure based on user query and context."""
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
    
    # Build planning prompt - only select procedure
    planning_prompt = f"""You are a CRM support planner. Your job is to select the appropriate procedure based on the user's query.

AVAILABLE PROCEDURES:
{procedures_text}

PROCEDURE SELECTION RULES:
- standard_support: For new issues, general support, ticket creation/updates
- quick_resolution: For simple lookups, status checks
- escalated_support: For critical issues, escalations

CONTEXT:
- Semantic memories ({semantic_count} found):
{semantic_content}
- Episodic memories ({episodic_count} found):
{episodic_content}

Return ONLY JSON (no other text):
{{
  "procedure": "standard_support" | "quick_resolution" | "escalated_support"
}}
"""
    
    # Call LLM to select procedure only
    messages = state["messages"] + [HumanMessage(content=planning_prompt)]
    out = llm.invoke(messages)
    content = extract_json_from_response(out.content)
    
    # Parse JSON
    procedure_name = "standard_support"
    
    try:
        plan = json.loads(content)
        procedure_name = plan.get("procedure", "standard_support")
        if procedure_name not in ProceduralMemory.PROCEDURES:
            procedure_name = "standard_support"
    except (json.JSONDecodeError, Exception):
        procedure_name = "standard_support"
    
    return {
        "selected_procedure": procedure_name
    }

