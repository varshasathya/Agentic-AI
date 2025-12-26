"""
Preference memory read node - Retrieves user preferences from preference store.

Currently used in the graph but preferences are never written. This node reads user preferences (communication
style, detail level, tone, etc.) and adds them to the message chain for use by planner and response nodes.
To use preferences, implement preference writing functionality (e.g., in salience_gated_memory_write or a
dedicated preference update node) to store user preferences based on conversation patterns or explicit requests.

Note:Refer preference_store.py for more details.
"""
from langchain_core.messages import SystemMessage

# These will be set in the main notebook
namespace = None
preference_store = None


def preference_read(state):
    """Retrieve user preferences."""
    prefs = preference_store.get_all(namespace)
    
    if not prefs:
        return {"preferences": {}}
    
    prefs_text = "User preferences:\n"
    for key, value_dict in prefs.items():
        prefs_text += f"- {key}: {value_dict.get('value', 'N/A')}\n"
    
    return {
        "preferences": prefs,
        "messages": [SystemMessage(content=prefs_text)]
    }

