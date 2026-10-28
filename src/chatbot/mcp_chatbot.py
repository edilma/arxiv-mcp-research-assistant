from dotenv import load_dotenv
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import List, Dict, TypedDict
from contextlib import AsyncExitStack
import json


load_dotenv(override=True) 

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class MCP_ChatBot:
    def __init__(self):
        # Initialize session and client objects
        self.sessions: List[ClientSession] = []
        self.exit_stack = AsyncExitStack()
        self.anthropic = anthropic.Anthropic()
        self.available_tools: List[ToolDefinition] = []
        self.tool_to_session: Dict[str, ClientSession] = {}



    async def connect_to_server(
        self, server_name: str, server_config: dict
    ) -> None:
        """Connect to a single MCP server."""

        server_params = StdioServerParameters(**server_config)

        # Open the server transport
        read, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # Create and initialize the MCP session
        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        await session.initialize()
        self.sessions.append(session)

        # Discover tools exposed by this server
        response = await session.list_tools()

        print(
            f"Connected to {server_name} with tools:",
            [tool.name for tool in response.tools]
        )

        for tool in response.tools:
            self.tool_to_session[tool.name] = session

            self.available_tools.append({
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.input_schema
            })

        # Discover resources and prompts from the research server
        if server_name == "research":
            resources = await session.list_resources()
            templates = await session.list_resource_templates()
            prompts = await session.list_prompts()

            print("Resources:", [
                str(r.uri) for r in resources.resources
            ])

            print("Templates:", [
                t.uri_template for t in templates.resource_templates
            ])

            print("Prompts:", [
                p.name for p in prompts.prompts
            ])

    async def connect_to_servers(self):
        """Connect to all configured MCP servers."""

        with open("server_config.json", "r") as file:
            data = json.load(file)

        servers = data.get("mcpServers", {})

        for server_name, server_config in servers.items():
            await self.connect_to_server(server_name, server_config)


    async def process_query(self, query):
        messages = [{"role": "user", "content": query}]

        

        while True:
            response = self.anthropic.messages.create(
                max_tokens=2024,
                model="claude-sonnet-4-6",
                tools=self.available_tools,
                messages=messages
            )

            assistant_content = response.content
            tool_results = []

            for content in assistant_content:
                if content.type == "text":
                    print(content.text)

                elif content.type == "tool_use":
                    tool_name = content.name
                    tool_args = content.input
                    tool_id = content.id

                    print(f"Calling tool {tool_name} with args {tool_args}")

                    result = await self.tool_to_session[tool_name].call_tool(
                        tool_name,
                        arguments=tool_args
                    )

                    # Convert MCP result to text
                    result_text = "\n".join(
                        block.text
                        for block in result.content
                        if block.type == "text"
                    )

                    # Collect results instead of sending immediately
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result_text,
                        "is_error": result.is_error
                    })

            # No tool requests: Claude has finished responding
            if not tool_results:
                break

            # Add the complete assistant response
            messages.append({
                "role": "assistant",
                "content": assistant_content
            })

            # Send ALL tool results together
            messages.append({
                "role": "user",
                "content": tool_results
            })

    async def cleanup(self):
        """Close all MCP server connections."""
        await self.exit_stack.aclose()
