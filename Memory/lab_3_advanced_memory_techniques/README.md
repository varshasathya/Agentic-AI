# Lab 3: Multi-Memory Agent

A CRM support agent with semantic, episodic, preference, and procedural memory systems.

## Architecture

### Graph Flow
```
semantic_read → episodic_read → preference_read → planner → procedural_guard → tool → conflict_resolution → respond → salience_gated_memory_write
```

Planner selects the procedure. Procedural guard enforces procedure rules by selecting the tool from allowed_tools and extracting arguments.

### Memory Types
- **Semantic Memory**: Facts (ticket IDs, devices, customer info) - vector store with deterministic keys
- **Episodic Memory**: Experiences (troubleshooting attempts, interactions) - vector store with recency bias
- **Preference Memory**: User preferences (communication style, tone) - key-value store
- **Procedural Memory**: Workflow rules and procedures - structured configuration

## File Structure

```
lab_3_advanced_memory_techniques/
├── lab3_multi_memory.ipynb    # Main notebook with graph definition and demos
├── nodes/                      # Graph nodes
│   ├── semantic_read.py        # Reads semantic memories
│   ├── episodic_read.py        # Reads episodic memories
│   ├── preference_read.py      # Reads user preferences
│   ├── planner.py              # Selects procedure based on user query
│   ├── procedural_guard.py    # Enforces procedure rules: selects tool, extracts arguments
│   ├── tool_node.py            # Executes tools (create/update/lookup ticket)
│   ├── conflict_resolution.py  # Resolves conflicts between tool output and memories
│   ├── response.py             # Generates natural language response
│   └── salience_gated_memory_write.py  # Writes to memory based on salience scores
├── memory_stores/              # Memory implementations
│   ├── semantic_memory.py      # Vector store for facts
│   ├── episodic_memory.py      # Vector store for experiences
│   ├── preference_store.py     # Key-value store for preferences
│   └── procedural_memory.py   # Structured procedures and rules
├── tools/                      # Agent tools
│   └── tools.py                # create_ticket, update_ticket, lookup_ticket
└── utils/                      # Utilities
    ├── extract_json.py         # JSON extraction from LLM responses
    └── salience_scoring.py     # Salience scoring for memory writes
```

## Key Components

### Planner Node
- Selects procedure (standard_support, quick_resolution, escalated_support) based on user query and context
- Uses semantic and episodic memories to make decisions
- Returns selected procedure for procedural guard

### Procedural Guard Node
- Takes selected procedure from planner
- Enforces procedure rules by selecting tool from procedure's allowed_tools
- Extracts arguments from conversation history and semantic/episodic memories
- Validates selected tool is in procedure's allowed_tools list
- Adds procedural context (steps, tool rules) to messages
- Handles escalation detection from previous tool execution

### Salience-Gated Memory Write
- Computes importance, novelty, contradiction, and risk scores
- Only writes to memory if threshold met or explicit trigger (ticket created/updated)
- Extracts semantic facts and episodic experiences using LLM
- Uses deterministic keys for semantic memory (enables overwrite)

### Conflict Resolution
- Tool output is authoritative
- Detects conflicts between tool output and semantic memories
- Updates semantic memory with verified facts from tool output

## Usage

1. Run cells in order from the notebook
2. Use `run_chat()` for simple interactions
3. Use `run_chat_detailed()` for debugging and inspection
4. Check memory stores using the inspection cells

## Next Steps

### Preference System
- Implement preference writing in salience_gated_memory_write or dedicated node
- Use preferences in response node to personalize tone and detail level
- Add automatic preference detection from conversation patterns

### Procedural Guard
- Currently integrated after planner in the graph
- Enforces procedure rules: selects tool from allowed_tools and extracts arguments
- Adds procedure-specific context (steps, tool rules) to messages for downstream nodes
- Detects escalations based on ticket status/priority from previous tool execution
- Can automatically switch to escalated_support procedure when escalation conditions are met

### Enhancements
- Add preference-based routing in planner
- Implement multi-language support using preferences
- Add preference templates for different user types
- Enhance escalation detection with more conditions

## Best Practices

1. **Memory Keys**: Use deterministic keys for semantic memory (e.g., `ticket_{ticket_id}`) to enable overwrite
2. **Salience Threshold**: Adjust threshold (default 0.6) based on use case - lower for more memories, higher for quality
3. **Memory Limits**: Limit semantic/episodic memories in prompts (currently 5) to avoid token limits. Summarize to avoid context/prompt exploding.
4. **Tool Arguments**: Ensure procedural guard extracts all required arguments - check tool definitions
5. **Conflict Resolution**: Tool output always wins - design tools to return authoritative data
6. **Namespace**: Use unique namespaces per user/customer for memory isolation



