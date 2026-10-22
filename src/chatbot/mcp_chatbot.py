from typing import List
import anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv() 

class MCP_ChatBot:
    def __init__(self):
        # Initialize session and client objects
        self.session: ClientSession | None = None
        self.anthropic = anthropic.Anthropic()
        self.available_tools: List[dict] = []


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

                    result = await self.session.call_tool(
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


    async def connect_to_server_and_run(self, chat_loop):
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command="uv",  # Executable
                args=["run", "python","-m","chatbot.research_server"],  # Optional command line arguments
                env=None,  # Optional environment variables
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    # Initialize the connection
                    await session.initialize()
        
                    # List available tools
                    response = await session.list_tools()
                    
                    tools = response.tools
                    print("\nConnected to server with tools:", [tool.name for tool in tools])
                    
                    self.available_tools = [{
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema
                    } for tool in response.tools]

                    # Keep session open during conversation
                    await chat_loop(self)