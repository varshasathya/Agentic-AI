"""LangGraph Customer Support System

A multi-agent system that routes customer queries to specialized agents
based on intent classification.
"""

from langchain_core.runnables import RunnableParallel, RunnableLambda
from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.intent_agent import intent_agent
from nodes.entity_agent import entity_agent
from nodes.product_node import product_info_agent, user_history_agent
from nodes.troubleshoot_agent import troubleshoot_agent
from nodes.composer_agent import reply_agent
from nodes.refund_agent import refund_agent


# Create RunnableParallel for true parallel execution
parallel_node = RunnableParallel({
    "product_info": RunnableLambda(product_info_agent),
    "user_history": RunnableLambda(user_history_agent)
})


# Build the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("intent", intent_agent)
graph.add_node("entities", entity_agent)
graph.add_node("parallel", parallel_node)
graph.add_node("troubleshoot", troubleshoot_agent)
graph.add_node("refund", refund_agent)
graph.add_node("reply", reply_agent)

# Set entry point
graph.set_entry_point("intent")

# Define routing logic
graph.add_conditional_edges(
    "intent",
    lambda s: s.get("intent", "unknown"),
    {
        "unknown": "reply",
        "product_info": "entities",
        "order_status": "entities",
        "refund_request": "refund",
        "tech_support": "troubleshoot",
    }
)

# Define edges
graph.add_edge("entities", "parallel")
graph.add_edge("parallel", "reply")
graph.add_edge("troubleshoot", "reply")
graph.add_edge("refund", "reply")
graph.add_edge("reply", END)

# Compile the graph
runnable = graph.compile()

# Generate and save graph diagram
runnable.get_graph().draw_mermaid_png(output_file_path="graph.png")


if __name__ == "__main__":
    # Example queries
    queries = [
        "What's the battery life of the Kindle Paperwhite?",
        "My Kindle isn't turning on",
        "I want a refund for my order",
        "Where is my order #12345?",
    ]
    
    # Test with all queries
    for query in queries:
        result = runnable.invoke({"query": query})
        print("\n" + "="*60)
        print("QUERY:", result.get("query"))
        print("\nINTENT:", result.get("intent"))
        print("\nREPLY:")
        print(result.get("reply", "No reply generated"))
        print("\n" + "="*60)


