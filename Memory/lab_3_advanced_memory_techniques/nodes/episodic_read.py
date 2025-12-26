"""Episodic memory read node."""
from langchain_core.messages import SystemMessage

# These will be set in the main notebook
namespace = None
episodic_store = None


def episodic_read(state):
    """Retrieve episodic memories (experiences, past interactions)."""
    query = state["messages"][-1].content if state["messages"] else ""
    
    # Search episodic store with recency bias
    results = episodic_store.search(namespace, query, top_k=3)
    
    if not results:
        return {"episodic_memories": []}
    
    memory_text = "Episodic memories (past experiences):\n"
    memory_text += "\n".join([f"- {r['content']}" for r in results])
    
    return {
        "episodic_memories": results,
        "messages": [SystemMessage(content=memory_text)]
    }

