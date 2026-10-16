# arXiv Research Chatbot

A Python chatbot that uses Anthropic's Claude API and tool calling to search for academic papers on arXiv, retrieve paper metadata, and generate research summaries.

Built as a learning project while taking DeepLearning.AI's *MCP: Build Rich-Context AI Apps with Anthropic* course.

## Features

- Search arXiv for academic papers by topic.
- Retrieve paper titles, authors, abstracts, publication dates, and PDF URLs.
- Save paper metadata locally in JSON files, organized by topic.
- Look up previously saved papers by arXiv ID.
- Use Claude's tool-calling capabilities to execute searches and retrieve information.
- Interact with the chatbot through a command-line interface.

## Tech Stack

- **Python 3.12+**
- **uv** — Dependency and environment management
- **Anthropic SDK** — Claude API integration
- **arxiv** — Python wrapper for the arXiv API
- **python-dotenv** — Environment variable management

## Project Structure

```text
chatbot/
├── src/
│   └── chatbot/
│       ├── __init__.py
│       ├── main.py           # CLI entry point
│       ├── chatbot.py        # Claude integration and tool execution
│       ├── tools.py          # arXiv search and retrieval functions
│       └── tool_schema.py    # Tool definitions
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

## How It Works

1. The user submits a research question.
2. Claude determines whether a tool is needed.
3. The application executes the requested Python function.
4. The `search_papers` tool queries arXiv and stores paper metadata in JSON files.
5. The `extract_info` tool retrieves information about a previously saved paper.
6. Tool results are returned to Claude, which generates a response.

## Available Tools

| Tool | Description |
|---|---|
| `search_papers(topic, max_results=5)` | Searches arXiv and saves paper metadata |
| `extract_info(paper_id)` | Retrieves locally stored information for a paper |

## Notes

- The application saves paper metadata, not PDF files.
- Chat history is not persisted between queries.
- The project currently uses Anthropic's native tool-calling API. It is not yet an MCP server.
- API requests may be subject to arXiv rate limits.
- Keep API credentials out of version control.

## Acknowledgments

Based on the chatbot example from DeepLearning.AI's *MCP: Build Rich-Context AI Apps with Anthropic* course, adapted into a local Python project using VS Code and uv.