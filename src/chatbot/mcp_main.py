import asyncio
from .mcp_chatbot import MCP_ChatBot


async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
        
                if query.lower() == 'quit':
                    break
                    
                await self.process_query(query)
                print("\n")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run(chat_loop)


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()