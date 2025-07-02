#!/usr/bin/env python3
"""
Demo 2: Agent with MCP Tools
Interactive Terminal Agent with Math and Weather MCP Tools
"""

import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrockConverse
import boto3

def create_bedrock_client():
    """Create a Bedrock client."""
    
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    return bedrock_client

def create_llm():
    """Create LLM with fallback options."""
    try:
        # Try Bedrock first
        bedrock_client = create_bedrock_client()
        if bedrock_client:
            llm = ChatBedrockConverse(
                client=bedrock_client,
                model_id="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
                max_tokens=1000,
                temperature=0.1
            )
            print("✅ Using AWS Bedrock Claude")
            return llm
    except Exception as e:
        print(f"⚠️  Bedrock setup failed: {e}")
    
    # If Bedrock fails, suggest alternatives
    print("❌ No LLM available. Please configure AWS Bedrock or add another LLM provider.")
    print("💡 Set up AWS credentials with: aws configure")
    return None

async def interactive_chat():
    """Run interactive chat with MCP tools."""
    print("🤖 Interactive MCP Agent")
    print("=" * 40)
    print("Type 'quit' to exit")
    print()
    
    # Create LLM
    llm = create_llm()
    if not llm:
        return
    
    # MCP client configuration
    mcp_config = {
        "math": {
            "command": "/path/to/your/.venv/bin/python", # replace with your own path
            "args": ["/path/to/your/math_server.py"] # replace with your own path
        },
        "weather": {
            "command": "/path/to/your/.venv/bin/python", 
            "args": ["/path/to/your/weather_server.py"]
        }
    }
    
    try:
        async with MultiServerMCPClient(mcp_config) as client:
            print("🔗 Connected to MCP servers")
            
            # Create agent with tools
            tools = client.get_tools()
            agent = create_react_agent(llm, tools)
            
            print(f"🛠️  Available tools: {[tool.name for tool in tools]}")
            print()
            
            while True:
                try:
                    # Get user input
                    user_input = input("You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'bye', 'q', 'goodbye']:
                        print("👋 Goodbye!")
                        break
                    
                    if not user_input:
                        continue
                    
                    # Process with agent
                    print("🤖 Agent: ", end="", flush=True)
                    
                    response = await agent.ainvoke({
                        "messages": [{
                            "role": "user", 
                            "content": user_input
                        }]
                    })
                    
                    # Show tool usage if any
                    if 'messages' in response and len(response['messages']) > 1:
                        for msg in response['messages'][1:-1]:  # Skip user input and final response
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                for tool_call in msg.tool_calls:
                                    print(f"\n🔧 Using tool: {tool_call['name']}")
                            elif hasattr(msg, 'name') and msg.name:
                                print(f"\n🔧 Used tool: {msg.name}")
                    
                    # Extract and print the response
                    if 'messages' in response and response['messages']:
                        last_message = response['messages'][-1]
                        if hasattr(last_message, 'content'):
                            print(last_message.content)
                        else:
                            print(str(last_message))
                    else:
                        print("No response generated")
                    
                    print()  # Add blank line
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Failed to connect to MCP servers: {e}")

def quick_test():
    """Quick test without interactive mode."""
    print("🧪 Quick Test Mode")
    
    async def test():
        mcp_config = {
            "math": {
                "command": "/path/to/your/.venv/bin/python", # replace with your own path
                "args": ["/path/to/your/server.py"] # replace with your own path
            },
            "weather": {
                "command": "/path/to/your/.venv/bin/python", # replace with your own path
                "args": ["/path/to/your/weather_server.py"] # replace with your own path
            }
        }
        
        try:
            async with MultiServerMCPClient(mcp_config) as client:
                tools = client.get_tools()
                print(f"✅ Connected! Available tools: {[tool.name for tool in tools]}")
                
                # Test math tool directly
                for tool in tools:
                    if tool.name == "add":
                        result = await tool.ainvoke({"a": 5, "b": 3})
                        print(f"🧮 Math test: 5 + 3 = {result}")
                        break
                
                # Test weather tool directly
                for tool in tools:
                    if tool.name == "get_city_weather":
                        result = await tool.ainvoke({"city_name": "san francisco"})
                        print(f"🌤️  Weather test: {result[:100]}...")
                        break
                        
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    asyncio.run(test())

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        quick_test()
    else:
        asyncio.run(interactive_chat())