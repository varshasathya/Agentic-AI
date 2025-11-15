# Routing Pattern in Agentic AI

## Overview

The **Routing Pattern** is a fundamental design pattern in agentic AI systems that intelligently directs user queries to specialized AI agents based on the query type. This pattern enables systems to provide more accurate, context-aware responses by leveraging domain-specific expertise.

## Use Case: Customer Support System

This implementation demonstrates a customer support routing system that classifies queries and routes them to specialized agents:

- **Order Status Agent**: Handles order tracking, delivery, shipping, returns, and refunds
- **Product Information Agent**: Provides product features, specifications, availability, and pricing
- **Technical Support Agent**: Troubleshoots technical issues, bugs, and provides step-by-step solutions

## Architecture

```
User Query
    ↓
Router Agent (Classifies query)
    ↓
    ├──→ Order Status Agent
    ├──→ Product Information Agent
    └──→ Technical Support Agent
```

### Key Components

1. **Router Agent**: An LLM-based classifier that determines the query category
2. **Specialized Agents**: Domain-specific agents optimized for their respective tasks
3. **RunnableBranch**: LangChain's declarative routing mechanism for conditional execution

## How It Works

### Step 1: Router Classification
The router agent analyzes the user query and classifies it into one of the predefined categories.

### Step 2: Agent Selection
Using `RunnableBranch`, the system routes to the appropriate specialized agent based on the classification. This provides a clean, declarative way to handle conditional routing.

### Step 3: Response Generation
The selected agent processes the query and generates a contextually appropriate response.

## Getting Started

### Prerequisites

```bash
pip install langchain langchain-openai python-dotenv
```

### Setup

1. Set your OpenAI API key. The notebook will automatically load from a `.env` file:
```bash
# Create .env file in the same directory
OPENAI_API_KEY=your-api-key-here
```

Or set it directly in Python (before running the notebook):
```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

2. Run the notebook:
```bash
jupyter notebook routing.ipynb
```

**Note**: The notebook includes automatic environment variable validation and will show clear error messages if the API key is missing.

## Usage Example

```python
# Route a customer query
result = route_with_metadata("Where is my order #12345?")

print(f"Category: {result['category']}")
print(f"Response: {result['response']}")
```

### Using RunnableBranch

The implementation uses `RunnableBranch` for declarative routing:

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda

branch_router = RunnableBranch(
    (lambda x: "order" in x.get("category", "").lower(), order_agent),
    (lambda x: "product" in x.get("category", "").lower(), product_agent),
    (lambda x: "tech" in x.get("category", "").lower(), tech_agent),
    tech_agent  # default chain
)
```

### Example Output

```
Category: order_status
Response: I can help you track your order #12345. Let me check the status for you...
```

## Key Features

- **RunnableBranch**: Uses LangChain's declarative routing mechanism for clean, maintainable code
- **LCEL Composition**: Built with LangChain Expression Language for seamless composability
- **Extensible**: Easy to add new agent types or categories by adding branches
- **Metadata Tracking**: Returns routing information for analytics and debugging
- **Error Handling**: Graceful fallback to default agent with environment variable validation
- **Modern Patterns**: Uses current LangChain best practices (no deprecated APIs)

## Pattern Benefits

1. **Scalability**: Add new specialized agents without modifying existing code
2. **Maintainability**: Each agent has a single, focused responsibility
3. **Performance**: Route queries to the most appropriate agent quickly
4. **Flexibility**: Swap or update agents independently
5. **Specialization**: Each agent can be fine-tuned for its specific domain

## Extending the Pattern

### Adding a New Agent

1. Create a new specialized agent:
```python
refund_agent = ChatPromptTemplate.from_messages([
    ("system", "You are a refund specialist..."),
    ("user", "{query}")
]) | llm | StrOutputParser()
```

2. Update the router prompt to include the new category

3. Add a new branch to `RunnableBranch`:
```python
branch_router = RunnableBranch(
    (lambda x: "order" in x.get("category", "").lower(), order_agent),
    (lambda x: "product" in x.get("category", "").lower(), product_agent),
    (lambda x: "refund" in x.get("category", "").lower(), refund_agent),  # New branch
    (lambda x: "tech" in x.get("category", "").lower(), tech_agent),
    tech_agent  # default chain
)
```

The order of branches matters - `RunnableBranch` evaluates conditions from top to bottom and uses the first matching branch.

## When to Use This Pattern

- **Multiple Domains**: When queries span different knowledge domains
- **Specialized Expertise**: When different queries require different expertise
- **Scalable Systems**: When you need to add new capabilities over time
- **Customer Support**: When handling diverse customer inquiries
- **Multi-Agent Systems**: As a foundation for more complex agentic systems

## Alternative Approaches

- **Single Agent**: Simpler but less specialized
- **Rule-Based Routing**: Faster but less flexible
- **Multi-Agent Orchestration**: More complex but handles multi-step workflows

## Contributing

Feel free to extend this pattern with:
- Additional agent types
- Enhanced routing logic
- Performance optimizations
- Error handling improvements

## License

This is an educational example for demonstrating routing patterns in agentic AI systems.

---

## Implementation Details

- **RunnableBranch**: Provides declarative, composable routing logic
- **Environment Variables**: Automatic validation with helpful error messages
- **LCEL Chains**: All agents use LangChain Expression Language for consistency
- **Type Safety**: Uses type hints for better code maintainability

---

**Note**: This pattern is production-ready but should be enhanced with proper error handling, logging, and monitoring for production deployments.

