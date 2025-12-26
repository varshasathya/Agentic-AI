"""Tool execution node."""
import json
from langchain_core.messages import SystemMessage
from tools.tools import TOOLS


def tool_node(state):
    """Execute tool based on planner decision."""
    # Get planner's JSON output from last message
    last_msg = state["messages"][-1]
    raw = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    
    # Parse JSON
    plan = None
    try:
        plan = json.loads(raw)
    except:
        # Try to extract JSON using brace matching
        brace_count = 0
        start_idx = raw.find('{')
        if start_idx != -1:
            for i in range(start_idx, len(raw)):
                if raw[i] == '{':
                    brace_count += 1
                elif raw[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = raw[start_idx:i+1]
                        try:
                            plan = json.loads(json_str)
                            break
                        except:
                            break
    
    # Get tool name and arguments from state
    if plan:
        tool_name = plan.get("tool")
        arguments = plan.get("arguments", {})
    else:
        # Fallback to state
        tool_name = state.get("planner_tool")
        arguments = state.get("planner_arguments", {})
    
    # Execute tool
    if tool_name:
        for t in TOOLS:
            if t["name"] == tool_name:
                try:
                    result = t["func"](arguments)
                    result_text = json.dumps(result, indent=2)
                    return {
                        "tool_result": result,
                        "messages": [SystemMessage(content=f"Tool '{tool_name}' executed successfully. Result: {result_text}")]
                    }
                except Exception as e:
                    import traceback
                    error_result = {"error": str(e), "tool": tool_name, "arguments": arguments}
                    return {
                        "tool_result": error_result,
                        "messages": [SystemMessage(content=f"Tool '{tool_name}' failed with error: {str(e)}")]
                    }
        
        # Tool not found
        return {
            "tool_result": {"error": f"Tool '{tool_name}' not found in available tools"},
            "messages": [SystemMessage(content=f"Tool '{tool_name}' not found. Available tools: {[t['name'] for t in TOOLS]}")]
        }
    
    # No tool specified - should not happen, but handle gracefully
    return {"tool_result": None}
