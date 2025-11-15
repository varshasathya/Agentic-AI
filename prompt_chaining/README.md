# Prompt Chaining Pattern in Agentic AI

## Overview

**Prompt Chaining** is a powerful pattern in agentic AI that connects multiple LLM calls in sequence, where the output of one prompt becomes the input for the next. This enables complex, multi-step reasoning and processing that would be difficult to achieve in a single prompt.

## Use Case: Market Research Report Processing

This implementation demonstrates a 3-step prompt chaining pipeline that processes market research reports:

1. **Summarize**: Extract key findings from a market research report
2. **Extract Trends**: Identify emerging trends in structured JSON format
3. **Draft Email**: Generate a professional email summarizing the trends

## Architecture

```
Market Research Report
    ↓
[Step 1: Summary Chain]
    ↓
Executive Summary
    ↓
[Step 2: Trends Chain]
    ↓
Structured Trends (JSON)
    ↓
[Step 3: Email Chain]
    ↓
Professional Email
```

### Key Components

1. **SequentialChain**: LangChain's mechanism for chaining multiple LLM calls
2. **LLMChain**: Individual chain components that process specific tasks
3. **Output Variables**: Each chain passes its output to the next via named variables

## How It Works

### Step 1: Summarization
The first chain takes the raw market research report and generates a concise executive summary highlighting key findings.

### Step 2: Trend Extraction
The summary is then analyzed to extract exactly 3 emerging trends, formatted as structured JSON with supporting data points.

### Step 3: Email Generation
Finally, the trends are used to draft a professional email that can be sent to stakeholders.

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
jupyter notebook prompt.ipynb
```

## Usage Example

```python
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Step 1: Summarize
summary_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["report"],
        template="Summarize the key findings: {report}"
    ),
    output_key="summary"
)

# Step 2: Extract Trends
trends_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["summary"],
        template="Extract trends from: {summary}"
    ),
    output_key="trends"
)

# Step 3: Draft Email
email_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["trends"],
        template="Draft email about: {trends}"
    ),
    output_key="email"
)

# Chain them together
pipeline = SequentialChain(
    chains=[summary_chain, trends_chain, email_chain],
    input_variables=["report"],
    output_variables=["summary", "trends", "email"]
)

# Run the pipeline
result = pipeline.invoke({"report": report_text})
```

## Example Output

The pipeline produces three outputs:

1. **Executive Summary**: A concise overview of key findings
2. **Emerging Trends**: Structured JSON with trend names and supporting data
3. **Professional Email**: A ready-to-send email summarizing the trends

See `sample_output.txt` for a complete example.

## Key Features

- **Sequential Processing**: Each step builds on the previous one
- **Structured Output**: JSON format for trends enables programmatic processing
- **Modular Design**: Easy to add, remove, or modify individual chains
- **Error Handling**: Each chain can be tested independently
- **Verbose Mode**: Track the execution flow with `verbose=True`

## Pattern Benefits

1. **Complex Reasoning**: Break down complex tasks into manageable steps
2. **Context Preservation**: Each step has access to previous outputs
3. **Specialization**: Each chain can be optimized for its specific task
4. **Reusability**: Individual chains can be reused in different pipelines
5. **Debugging**: Easier to debug when each step is isolated

## When to Use Prompt Chaining

- **Multi-Step Processing**: When tasks require sequential reasoning
- **Information Extraction**: When you need to extract and transform data in stages
- **Content Generation**: When creating content that builds on previous analysis
- **Structured Output**: When intermediate steps need structured data
- **Complex Workflows**: When a single prompt would be too complex or unreliable

## Extending the Pattern

### Adding a New Step

1. Create a new chain:
```python
new_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["previous_output"],
        template="Process: {previous_output}"
    ),
    output_key="new_output"
)
```

2. Add it to the SequentialChain:
```python
pipeline = SequentialChain(
    chains=[summary_chain, trends_chain, new_chain, email_chain],
    input_variables=["report"],
    output_variables=["summary", "trends", "new_output", "email"]
)
```

## Alternative Approaches

- **Single Prompt**: Simpler but less reliable for complex tasks
- **Parallel Chains**: Use when steps are independent
- **Conditional Chains**: Add routing logic between chains
- **LCEL (LangChain Expression Language)**: Modern alternative using `|` operator

## Related Patterns

- **Routing Pattern**: For directing queries to different chains
- **Agent Orchestration**: For coordinating multiple agents
- **RAG (Retrieval Augmented Generation)**: For adding external knowledge

## Files

- `prompt.ipynb`: Main notebook with the chaining implementation
- `market_reports.txt`: Sample input data
- `sample_output.txt`: Example output from the pipeline

## Notes

- This example uses `LLMChain` which is deprecated in LangChain 0.1.17+
- For production, consider migrating to LCEL: `prompt | llm | parser`
- The structured JSON output enables easy integration with other systems

---

**Note**: This pattern is production-ready but should be enhanced with proper error handling, logging, and validation for production deployments.

