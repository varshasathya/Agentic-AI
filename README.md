# Agentic AI Patterns: Code Examples

A collection of practical code examples demonstrating fundamental patterns in agentic AI systems. Each pattern includes working code, detailed explanations, and real-world use cases.

## What is Agentic AI?

**Agentic AI** refers to AI systems that can autonomously make decisions, take actions, and coordinate multiple steps to accomplish complex tasks. Unlike simple chatbots, agentic AI systems use patterns like routing, chaining, and orchestration to handle sophisticated workflows.

## Available Patterns

Each folder in this repository contains a complete example of an agentic AI pattern:

- **Working Code**: Jupyter notebooks with runnable examples
- **Detailed Documentation**: README files explaining the pattern
- **Real-world Use Cases**: Practical applications and examples

Browse the folders to explore different patterns. Each pattern folder includes:
- `README.md` - Pattern explanation and usage guide
- `*.ipynb` - Interactive code examples
- Additional files as needed (data, configs, etc.)

## Quick Start

### Prerequisites

```bash
pip install langchain langchain-openai python-dotenv
```

### Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd blogs
```

2. Set your OpenAI API key:
```bash
# Create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

Or set it directly in Python:
```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

3. Run the notebooks:
```bash
jupyter notebook
```

## Repository Structure

```
repository/
├── README.md                 # This file
├── pattern_name/            # Each pattern/blog_topic has its own folder
│   ├── README.md            # Pattern documentation
│   ├── *.ipynb              # Code examples
│   └── ...                  # Additional files as needed
└── ...
```

## Learning Path

1. **Explore Patterns**: Browse the available patterns and choose one that interests you
2. **Read the Documentation**: Each pattern folder contains a detailed README
3. **Run the Examples**: Execute the notebooks to see the pattern in action
4. **Experiment**: Modify the code to understand how it works
5. **Combine Patterns**: Use multiple patterns together for complex workflows

## Technologies Used

- **LangChain**: Framework for building LLM applications
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs
- **OpenAI GPT-4o-mini**: Language model for processing(you can use any open source LLMs)
- **Jupyter Notebooks**: Interactive development and documentation
- **Python**: Programming language

## Combining Patterns

Patterns can be combined to build more sophisticated systems:

- **Sequential Combinations**: Use patterns in sequence (e.g., route then chain)
- **Conditional Logic**: Apply patterns conditionally based on context
- **Multi-Agent Orchestration**: Coordinate multiple patterns for complex workflows

## Blog Posts

These code examples accompany blog posts about agentic AI patterns. Each pattern folder may reference its corresponding blog post.

## Contributing

Feel free to:
- Add new patterns
- Improve existing examples
- Fix bugs or add features
- Enhance documentation

## License

This repository contains educational examples for demonstrating agentic AI patterns. Feel free to use and modify for your projects.

## 🔗 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Agentic AI Concepts](https://www.anthropic.com/research)

## Notes

- These examples may use `LLMChain` which is deprecated in LangChain 0.1.17+
- For production, consider migrating to LCEL (LangChain Expression Language)
- Always handle errors, add logging, and validate inputs for production use

---

**Happy Building!**

If you find these examples helpful, consider giving the repository a ⭐ star!

