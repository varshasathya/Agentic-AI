"""Semantic memory read node."""
from langchain_core.messages import SystemMessage

# These will be set in the main notebook
namespace = None
semantic_store = None


def semantic_read(state):
    """Retrieve semantic memories (facts, domain knowledge)."""
    query = state["messages"][-1].content if state["messages"] else ""
    
    # Search semantic store
    results = semantic_store.search(namespace, query, top_k=3)
    
    if not results:
        return {"semantic_memories": []}
    
    memory_text = "Semantic memories (facts, domain knowledge):\n"
    memory_text += "\n".join([f"- {r['content']}" for r in results])
    
    return {
        "semantic_memories": results,
        "messages": [SystemMessage(content=memory_text)]
    }
