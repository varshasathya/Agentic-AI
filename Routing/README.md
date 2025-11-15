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
3. **Routing Logic**: Simple conditional logic that matches categories to agents

## How It Works

### Step 1: Router Classification
The router agent analyzes the user query and classifies it into one of the predefined categories.

### Step 2: Agent Selection
Based on the classification, the system selects the appropriate specialized agent.

### Step 3: Response Generation
The selected agent processes the query and generates a contextually appropriate response.

## Getting Started

### Prerequisites

```bash
pip install langchain langchain-openai python-dotenv
```

### Setup

1. Set your OpenAI API key:
```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

Or use a `.env` file:
```bash
OPENAI_API_KEY=your-api-key-here
```

2. Run the notebook:
```bash
jupyter notebook routing.ipynb
```

## Usage Example

```python
from routing import route_with_metadata

# Route a customer query
result = route_with_metadata("Where is my order #12345?")

print(f"Category: {result['category']}")
print(f"Response: {result['response']}")
```

### Example Output

```
Category: order_status
Response: I can help you track your order #12345. Let me check the status for you...
```

## Key Features

- **Simple & Clean**: Uses LangChain Expression Language (LCEL) for composability
- **Extensible**: Easy to add new agent types or categories
- **Metadata Tracking**: Returns routing information for analytics
- **Error Handling**: Graceful fallback to default agent
- **Modern Patterns**: No deprecated APIs, uses current LangChain best practices

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
3. Add routing logic:
```python
if "refund" in category:
    return refund_agent.invoke({"query": query})
```

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

**Note**: This pattern is production-ready but should be enhanced with proper error handling, logging, and monitoring for production deployments.

