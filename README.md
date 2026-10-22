# arXiv Research Chatbot

A Python research assistant that integrates Anthropic's Claude API, the arXiv API, and the Model Context Protocol (MCP) to discover, retrieve, and summarize academic research papers.

The project includes a command-line chatbot using Claude's native tool calling and a separate MCP server that exposes research tools to compatible MCP clients.

Developed as a learning project based on DeepLearning.AI's *MCP: Build Rich-Context AI Apps with Anthropic* course.

## Features

- Search arXiv for academic papers by topic.
- Retrieve paper titles, authors, abstracts, publication dates, and PDF URLs.
- Store paper metadata locally in JSON files, organized by topic.
- Retrieve previously saved papers by arXiv ID
- Generate research summaries using Claude and tool calling
- Interact with the research chatbot through a command-line interface
- Expose research functionality through an MCP server
- Discover and test MCP tools using MCP Inspector

## Tech Stack

- **Python 3.12+**
- **uv** — Dependency and environment management
- **Anthropic SDK** — Claude API integration
- **MCP Python SDK** — MCP server implementation and tool registration
- **arxiv** — Python wrapper for the arXiv API
- **python-dotenv** — Environment variable management
- **MCP Inspector** — MCP server testing and debugging

## Project Structure

```text
chatbot/
├── src/
│   └── chatbot/
│       ├── __init__.py
│       ├── main.py           # Original chatbot entry point
│       ├── chatbot.py        # Original Claude chatbot
│       ├── mcp_main.py       # New MCP chatbot entry point
│       ├── mcp_chatbot.py    # New MCP client orchestration
│       ├── tools.py          # arXiv functions
│       └── tool_schema.py    # Original Claude Tool Schemas
│       └── research_server.py# MCP Server
├── papers/                   # Locally saved paper metadata
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

**1. Install dependencies**

From the project root:

```bash
uv sync
```

**2. Configure your API key**

Create a `.env` file in the project root:

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**3. Run the chatbot**

```bash
uv run chatbot
```

Enter a research topic or question at the prompt. Type `quit` to exit.

**4. Run the MCP server**

```bash
uv run python -m chatbot.research_server
```

The MCP server uses the stdio transport and waits for connections from an MCP client.

**5. Test the MCP server with MCP Inspector**

```bash
npx @modelcontextprotocol/inspector uv run python -m chatbot.research_server
```
Open the local Inspector URL displayed in the terminal, connect to the server, and test the available tools.

## How It Works
The project currently has two components:

### Claude Research Chatbot

1. The user submits a research question
2. Claude receives the question and available tool definitions
3. Claude decides whether to request a tool
4. The Python application executes the requested function
5. Tool results are returned to Claude
6. Claude generates a natural-language response

### MCP Research Server

1. The MCP server exposes research tools using the Python MCP SDK
2. Tool schemas are generated from Python function signatures and docstrings
3. An MCP client discovers and invokes available tools
4. The server executes the requested Python functions and returns their results
5. Research metadata is stored locally in JSON files organized by topic

## Available Tools

| Tool | Description |
|---|---|
| `search_papers(topic, max_results=5)` | Searches arXiv and saves paper metadata |
| `extract_info(paper_id)` | Retrieves locally stored information for a paper |

## Notes

- The application saves paper metadata, not PDF files
- Chat history is not persisted between queries
- The Claude chatbot currently uses Anthropic's native tool-calling API
- The MCP server is implemented separately and can be tested using MCP Inspector
- The existing chatbot is not yet connected to the MCP server.
- API requests may be subject to arXiv rate limits.
- Keep API credentials must remain outside version control.

## Acknowledgments

Inspired by DeepLearning.AI'ss *MCP: Build Rich-Context AI Apps with Anthropic* course, adapted into a local Python project using VS Code and uv.