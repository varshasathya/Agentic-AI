# LangGraph 101: Multi-Agent Orchestration

## Overview

**LangGraph** is a framework for building stateful, multi-agent applications with LLMs. Unlike simple prompt chaining or routing, LangGraph enables complex workflows with conditional routing, state management, and parallel execution. This implementation demonstrates a customer support system with multiple specialized agents working together.

## Use Case: Customer Support System

This implementation demonstrates a sophisticated customer support system that:

1. **Classifies** user queries by intent
2. **Routes** to specialized agents based on intent
3. **Extracts** entities and fetches data in parallel
4. **Generates** context-aware responses

### Specialized Agents

- **Intent Agent**: Classifies queries into categories (order_status, product_info, tech_support, refund_request, unknown)
- **Entity Agent**: Extracts structured information (product IDs, order numbers, etc.)
- **Product Info Agent**: Fetches product details from a database/API
- **User History Agent**: Retrieves user account information
- **Troubleshoot Agent**: Identifies technical issues and error codes
- **Refund Agent**: Analyzes refund eligibility and policies
- **Reply Agent**: Composes the final response using all collected information

## Architecture

```
User Query
    ↓
[Intent Agent] → Classifies query
    ↓
    ├──→ product_info → [Entity Agent] → [Parallel Node]
    ├──→ order_status → [Entity Agent] → [Parallel Node]
    ├──→ tech_support → [Troubleshoot Agent]
    ├──→ refund_request → [Refund Agent]
    └──→ unknown → [Reply Agent]
         ↓
    [Parallel Node]
         ├──→ Product Info Agent (fetches product data)
         └──→ User History Agent (fetches user data)
         ↓
    [Reply Agent] → Final Response
```

### Example Output

![LangGraph Execution Example](output_examples/example%201.png)
![LangGraph Execution Example](output_examples/example%202.png)

*Screenshot showing the graph execution with query classification, routing, and final response generation.*


### Key Components

1. **StateGraph**: LangGraph's graph builder for creating stateful workflows
2. **AgentState**: TypedDict defining the shared state structure
3. **Conditional Edges**: Routes based on state values (intent classification)
4. **Parallel Execution**: Runs independent agents concurrently
5. **State Management**: Each agent updates only its portion of the state

## Core Concepts: Nodes, Edges, and State

Understanding these three fundamental concepts is key to working with LangGraph:

### Nodes

**Nodes** are the processing units in a LangGraph workflow. Each node is a function that:
- Receives the current state as input
- Performs some processing (LLM calls, API requests, data transformations)
- Returns a partial state update (only the fields it modifies)

In our system, each agent is a node:

```python
# Each agent function is a node
def intent_agent(state: AgentState) -> dict:
    # Process the query
    intent = classify(state["query"])
    # Return only what this node updates
    return {"intent": intent}
```

**Key characteristics:**
- Nodes are **stateless** - they don't remember previous calls
- Nodes receive the **full state** but return **partial updates**
- Multiple nodes can run in parallel if they modify different state keys
- Nodes are **composable** - you can reuse them in different graphs

### Edges

**Edges** define the flow between nodes. They determine:
- Which node runs after another
- Conditional routing based on state values
- When the workflow ends

There are two types of edges:

#### 1. Simple Edges
Direct connections between nodes that always execute:

```python
graph.add_edge("entities", "parallel")  # Always go from entities to parallel
graph.add_edge("reply", END)            # End the workflow after reply
```

#### 2. Conditional Edges
Routes based on state values:

```python
graph.add_conditional_edges(
    "intent",                           # Source node
    lambda s: s.get("intent"),          # Routing function (reads state)
    {
        "product_info": "entities",    # If intent == "product_info", go to entities
        "tech_support": "troubleshoot", # If intent == "tech_support", go to troubleshoot
        "unknown": "reply"              # If intent == "unknown", go to reply
    }
)
```

**Key characteristics:**
- Conditional edges use a **routing function** that reads the state
- The routing function returns a value that maps to a target node
- Only one path is taken per execution
- Simple edges are faster but less flexible

### State

**State** is the shared data structure that flows through the graph. It:
- Persists across all nodes in a single execution
- Gets updated incrementally by each node
- Is defined as a TypedDict for type safety

```python
class AgentState(TypedDict, total=False):
    query: str                    # Set at the start
    intent: Optional[str]         # Updated by intent_agent node
    entities: Dict[str, Any]      # Updated by entity_agent node
    product_info: Optional[Dict] # Updated by product_info_agent node
    # ... more fields
```

**State Update Pattern:**

Each node returns only the fields it updates:

```python
# Node receives full state
def intent_agent(state: AgentState) -> dict:
    # Can read any field from state
    query = state["query"]
    
    # Process and update
    intent = classify(query)
    
    # Return only what this node updates
    return {"intent": intent}  # LangGraph merges this into the full state
```

**Key characteristics:**
- State is **immutable** from the node's perspective (nodes receive a copy)
- Nodes return **partial updates** that LangGraph merges
- State flows **forward** through the graph
- All nodes in a single execution share the same state instance

### How They Work Together

```
┌─────────┐
│  State  │  ← Shared data structure
└────┬────┘
     │
     ↓
┌─────────┐      Edge      ┌─────────┐
│  Node 1 │ ──────────────→ │  Node 2 │
└─────────┘                 └─────────┘
     │                            │
     │ Updates state              │ Updates state
     ↓                            ↓
┌─────────┐                 ┌─────────┐
│  State  │                 │  State  │
│ +field1 │                 │ +field2 │
└─────────┘                 └─────────┘
```

1. **State** flows into a **Node**
2. **Node** processes and returns a partial update
3. LangGraph merges the update into the state
4. **Edge** determines which node runs next
5. Updated **State** flows to the next node

### Example Flow

```python
# Initial state
state = {"query": "What's the battery life?"}

# Node 1: Intent Agent
intent_result = intent_agent(state)
# Returns: {"intent": "product_info"}
# State becomes: {"query": "...", "intent": "product_info"}

# Edge: Conditional routing
# Routes to "entities" because intent == "product_info"

# Node 2: Entity Agent
entity_result = entity_agent(state)
# Returns: {"entities": {"product_id": "Kindle"}}
# State becomes: {"query": "...", "intent": "...", "entities": {...}}

# Edge: Simple edge
# Always goes to "parallel"

# Node 3: Parallel Node
parallel_result = parallel_node(state)
# Returns: {"product_info": {...}, "user_history": {...}}
# State becomes: {..., "product_info": {...}, "user_history": {...}}
```

This pattern continues until reaching the `END` node.

## How It Works

### Step 1: Intent Classification
The intent agent analyzes the user query and classifies it into one of five categories. This determines the routing path through the graph.

### Step 2: Conditional Routing
Based on the classified intent, the graph routes to different specialized agents:
- **product_info** / **order_status** → Entity extraction → Parallel data fetching
- **tech_support** → Troubleshooting analysis
- **refund_request** → Refund eligibility analysis
- **unknown** → Direct to reply agent

### Step 3: Parallel Execution
For product/order queries, two agents run in parallel:
- **Product Info Agent**: Fetches product details (price, stock, warranty)
- **User History Agent**: Retrieves user account information (VIP status, order history)

These agents are independent and can execute simultaneously, improving performance.

### Step 4: Response Generation
The reply agent receives all collected information and generates a context-aware response tailored to the user's intent and available data.

## Parallel Execution Explained

### Why Parallel?

When processing product or order queries, we need two pieces of information:
1. Product details (from product database)
2. User history (from user database)

These are **independent operations** - neither depends on the other. Running them sequentially would take:
- Product Info: ~300ms
- User History: ~200ms
- **Total Sequential**: ~500ms

Running them in parallel:
- Both start simultaneously
- Both complete when ready
- **Total Parallel**: ~300ms (time of the slowest operation)

### Implementation

The parallel execution uses LangChain's `RunnableParallel` for true concurrent execution:

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

# Create RunnableParallel for true parallel execution
parallel_node = RunnableParallel({
    "product_info": RunnableLambda(product_info_agent),
    "user_history": RunnableLambda(user_history_agent)
})
```

**How it works:**
- `RunnableParallel` executes both agents **concurrently** (not sequentially)
- Each agent is wrapped in `RunnableLambda` to make it compatible with LangChain's runnable interface
- The dictionary keys (`"product_info"` and `"user_history"`) become the state keys
- Both agents receive the same state and return partial updates
- `RunnableParallel` automatically merges the results into the state

### Key Points

1. **True Parallelism**: `RunnableParallel` executes agents concurrently using threading/async
2. **Independent Operations**: Both agents read from the same state but write to different keys
3. **No Conflicts**: Since they modify different state keys (`product_info` vs `user_history`), there's no race condition
4. **Automatic Merging**: `RunnableParallel` automatically merges results into state using dictionary keys
5. **Performance**: In production with real API calls, this provides significant speedup (e.g., 500ms sequential → 300ms parallel)

### When to Use Parallel Execution

**Use parallel execution when:**
- Operations are independent (no dependencies)
- Operations modify different state keys
- Operations involve I/O (API calls, database queries)
- Performance improvement is significant

**Don't use parallel execution when:**
- One operation depends on another's output
- Operations modify the same state keys
- Operations are CPU-bound and would compete for resources
- Overhead exceeds benefit (very fast operations)

## Getting Started

### Prerequisites

```bash
pip install langgraph langchain langchain-openai python-dotenv
```

### Setup

1. Set your OpenAI API key. Create a `.env` file in the `langgraph_101` directory:

```bash
OPENAI_API_KEY=your-api-key-here
```

Or set it directly in Python:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

2. Run the graph:

```bash
cd langgraph_101
python graph.py
```

## Usage Example

```python
from graph import runnable

# Process a query
result = runnable.invoke({"query": "What's the battery life of the Kindle Paperwhite?"})

print(f"Intent: {result['intent']}")
print(f"Reply: {result['reply']}")
```

### Example Output

```
QUERY: What's the battery life of the Kindle Paperwhite?

INTENT: product_info

REPLY:
The Kindle Paperwhite offers an impressive battery life of up to 10 weeks 
on a single charge, depending on usage and settings. This includes reading 
for about half an hour a day with wireless turned off...
```

## Key Features

- **Stateful Workflows**: Maintains context across multiple agent interactions
- **Conditional Routing**: Routes queries to appropriate agents based on intent
- **Parallel Execution**: Runs independent agents concurrently for better performance
- **Modular Design**: Each agent is a separate, testable component
- **Type Safety**: Uses TypedDict for state structure validation
- **Clean State Updates**: Each agent returns only the fields it modifies

## Pattern Benefits

1. **Scalability**: Easy to add new agents or modify existing ones
2. **Maintainability**: Each agent has a single, clear responsibility
3. **Performance**: Parallel execution reduces total processing time
4. **Flexibility**: Routing logic can be updated without changing agents
5. **Testability**: Each agent can be tested independently
6. **State Management**: LangGraph handles state merging automatically

## Understanding the State

The `AgentState` is a shared data structure that flows through the graph:

```python
class AgentState(TypedDict, total=False):
    query: str                    # User's original query
    intent: Optional[str]         # Classified intent (set by intent_agent)
    entities: Dict[str, Any]      # Extracted entities (set by entity_agent)
    product_info: Optional[Dict] # Product data (set by product_info_agent)
    user_history: Optional[Dict] # User data (set by user_history_agent)
    errors: List[str]             # Error codes (set by troubleshoot_agent)
    refund: Optional[Dict]       # Refund analysis (set by refund_agent)
    reply: Optional[str]          # Final response (set by reply_agent)
```

### State Update Pattern

Each agent returns **only the fields it updates**:

```python
def intent_agent(state: AgentState) -> dict:
    # Process and classify
    intent = classify_query(state["query"])
    
    # Return only what this agent updates
    return {"intent": intent}  # Not the entire state!
```

LangGraph automatically merges these partial updates into the full state.

## Extending the Pattern

### Adding a New Agent

1. Create the agent function in `nodes/`:

```python
# nodes/new_agent.py
def new_agent(state: AgentState) -> dict:
    """Process something and return state update."""
    result = process(state["query"])
    return {"new_field": result}
```

2. Add the node to the graph:

```python
from nodes.new_agent import new_agent

graph.add_node("new_agent", new_agent)
```

3. Add routing logic:

```python
graph.add_conditional_edges(
    "intent",
    lambda s: s.get("intent"),
    {
        "new_intent": "new_agent",  # Route to new agent
        # ... other routes
    }
)
```

### Adding a New Intent

1. Update the intent agent's prompt to include the new category
2. Add a routing case in `graph.add_conditional_edges`
3. Create or route to the appropriate specialized agent

### Adding Parallel Operations

To add more parallel operations, extend the `RunnableParallel`:

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

parallel_node = RunnableParallel({
    "product_info": RunnableLambda(product_info_agent),
    "user_history": RunnableLambda(user_history_agent),
    "inventory": RunnableLambda(inventory_agent)  # New agent
})
```

Simply add more entries to the dictionary - `RunnableParallel` will execute all of them concurrently.

## When to Use LangGraph

**Use LangGraph when:**
- You need stateful, multi-step workflows
- Different queries require different processing paths
- You want to run independent operations in parallel
- You need conditional routing based on LLM outputs
- You're building complex agentic systems

**Consider alternatives when:**
- Simple single-step queries (use basic LLM calls)
- No state management needed (use routing pattern)
- Linear processing only (use prompt chaining)
- Very simple workflows (use RunnableBranch)

## Comparison with Other Patterns

### vs. Prompt Chaining
- **Prompt Chaining**: Sequential, linear processing
- **LangGraph**: Conditional routing, parallel execution, state management

### vs. Routing Pattern
- **Routing**: Single-step routing to one agent
- **LangGraph**: Multi-step workflows with state persistence

### vs. Simple LLM Calls
- **Simple Calls**: One-shot queries
- **LangGraph**: Complex workflows with multiple agents

## Files Structure

```
langgraph_101/
├── graph.py              # Main graph definition and orchestration
├── state.py              # AgentState TypedDict definition
├── llm.py                # LLM initialization
└── nodes/
    ├── intent_agent.py      # Intent classification
    ├── entity_agent.py      # Entity extraction
    ├── product_node.py       # Product & user history agents
    ├── troubleshoot_agent.py # Technical issue identification
    ├── refund_agent.py      # Refund analysis
    └── composer_agent.py     # Final reply generation
```

## Best Practices

1. **Return Partial State**: Each agent should return only the fields it updates
2. **Type Safety**: Use TypedDict for state structure
3. **Error Handling**: Handle missing state keys gracefully with `.get()`
4. **Modularity**: Keep each agent in its own file
5. **Documentation**: Document what each agent does and what it updates
6. **Testing**: Test each agent independently before integration

## Common Patterns

### Conditional Routing

```python
graph.add_conditional_edges(
    "source_node",
    lambda state: state.get("key"),  # Routing function
    {
        "value1": "node1",
        "value2": "node2",
    }
)
```

### Parallel Execution

Using LangChain's `RunnableParallel`:

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

parallel_node = RunnableParallel({
    "key1": RunnableLambda(agent1),
    "key2": RunnableLambda(agent2)
})
```

The dictionary keys become the state keys, and both agents execute concurrently.

### State Updates

```python
def agent(state: AgentState) -> dict:
    # Process
    new_value = process(state["input"])
    # Return only what you update
    return {"output": new_value}
```

## Troubleshooting

### State Key Errors
- Use `.get()` with defaults: `state.get("key", default_value)`
- Ensure all required keys are initialized before use

### Routing Issues
- Check that intent values match routing keys exactly
- Add a default route for unexpected intents

### Parallel Execution
- Ensure agents modify different state keys
- Verify agents are truly independent

## Related Patterns

- **Prompt Chaining**: For sequential, linear processing
- **Routing Pattern**: For simple single-step routing
- **Agent Orchestration**: For coordinating multiple agentic systems

## Next Steps

1. Add error handling and retry logic
2. Implement logging and monitoring
3. Add validation for state updates
4. Optimize parallel execution for production
5. Add checkpointing for long-running workflows
---

**Note**: This pattern is production-ready but should be enhanced with proper error handling, logging, monitoring, and validation for production deployments.

