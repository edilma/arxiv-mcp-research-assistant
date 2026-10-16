from dotenv import load_dotenv
import anthropic

from .tools import search_papers, extract_info
from .tool_schema import tools


load_dotenv() 
client = anthropic.Anthropic()

mapping_tool_function = {
    "search_papers": search_papers,
    "extract_info": extract_info
}

def execute_tool(tool_name, tool_args):
    
    result = mapping_tool_function[tool_name](**tool_args)

    if result is None:
        result = "The operation completed but didn't return any results."
        
    elif isinstance(result, list):
        result = ', '.join(result)
        
    elif isinstance(result, dict):
        # Convert dictionaries to formatted JSON strings
        result = json.dumps(result, indent=2)
    
    else:
        # For any other type, convert using str()
        result = str(result)
    return result

def process_query(query):
    
    messages = [{'role': 'user', 'content': query}]
    
    response = client.messages.create(max_tokens=2024,
                                      #model = 'claude-3-7-sonnet-20250219', #deprecated model
                                       model='claude-sonnet-4-6',
                                       tools=tools,
                                       messages=messages)
    
    process_query = True
    while process_query:
        assistant_content = []
        tool_results = []
        has_tool_use = False

        for content in response.content:
            if content.type == 'text':
                print(content.text)
                assistant_content.append(content)

            elif content.type == 'tool_use':
                has_tool_use = True
                assistant_content.append(content)

                tool_id = content.id
                tool_args = content.input
                tool_name = content.name
                print(f"Calling tool {tool_name} with args {tool_args}")

                result = execute_tool(tool_name, tool_args)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result
                })

        # One assistant message per turn, with ALL content blocks
        messages.append({'role': 'assistant', 'content': assistant_content})

        if not has_tool_use:
            process_query = False
        else:
            # One user message with ALL tool_results for that turn
            messages.append({"role": "user", "content": tool_results})
            response = client.messages.create(max_tokens=2024,
                                              #model = 'claude-3-7-sonnet-20250219', #deprecated model
                                               model='claude-sonnet-4-6',
                                               tools=tools,
                                               messages=messages)