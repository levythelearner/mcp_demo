#!/usr/bin/env python3
"""
Demo 3: Weather Agent using MCP
Uses ReAct agent with MCP connection to weather_server.py for weather reports
"""

import asyncio
from datetime import datetime
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrockConverse
import boto3
import os

# US Cities for reports
US_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "Denver"
]

def create_bedrock_client():
    """Create a Bedrock client."""
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    return bedrock_client

def append_to_weather_summary(report: str, title: str = "MCP Weather Report"):
    """Append the weather report to weather_summary.txt."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open("weather_summary.txt", "a") as f:
        f.write(f"\n{title} - {timestamp}\n")
        f.write("=" * 50 + "\n")
        f.write(report + "\n")

async def generate_mcp_weather_report():
    """Generate weather reports for 10 US cities using MCP weather server."""
    print("🌤️  Generating MCP Weather Reports...")
    
    # Create LLM
    try:
        bedrock_client = create_bedrock_client()
        llm = ChatBedrockConverse(
            client=bedrock_client,
            model_id="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens=2000,
            temperature=0.1
        )
        print("✅ Connected to AWS Bedrock")
    except Exception as e:
        print(f"❌ Failed to setup LLM: {e}")
        return
    
    # MCP client configuration
    mcp_config = {
        "weather": {
            "command": "/path/to/your/.venv/bin/python", # replace with your own path
            "args": ["/path/to/your/weather_server.py"] # replace with your own path
        }
    }
    
    try:
        # Connect to MCP weather server
        print("🔗 Connecting to MCP weather server...")
        async with MultiServerMCPClient(mcp_config) as client:
            print("✅ Connected to MCP server")
            
            # Get available tools
            tools = client.get_tools()
            print(f"🛠️  Available MCP tools: {[tool.name for tool in tools]}")
            
            # Create ReAct agent with MCP tools
            agent = create_react_agent(llm, tools)
            
            # Generate comprehensive report for all cities
            cities_list = ", ".join(US_CITIES)
            prompt = f"""Generate a comprehensive weather report for these major US cities: {cities_list}.

For each city, please:
1. Use the get_city_weather tool to get the weather forecast
2. Present the information in a clear, organized format with each city's weather clearly separated
3. Include temperature, conditions, and forecast details

Use the available MCP weather tools to get the most current information for each city.
Format the output as a clean summary with clear headings for each city."""
            
            print("🔧 Running MCP agent to generate reports...")
            response = await agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            # Extract the response
            if 'messages' in response and response['messages']:
                report = response['messages'][-1].content
                
                print("\n" + "="*60)
                print("MCP WEATHER REPORT - 10 US CITIES")
                print("="*60)
                print(report)
                print("="*60)
                
                # Append to summary file
                append_to_weather_summary(report, "MCP 10-City Weather")
                print(f"\n✅ MCP report appended to weather_summary.txt")
                
            else:
                print("❌ No response generated")
                
    except Exception as e:
        print(f"❌ Error connecting to MCP server or generating report: {e}")

async def test_individual_city():
    """Test getting weather for a single city using MCP."""
    print("\n🧪 Testing individual city weather via MCP...")
    
    mcp_config = {
        "weather": {
            "command": "/path/to/your/.venv/bin/python", # replace with your own path
            "args": ["/path/to/your/weather_server.py"] # replace with your own path
        }
    }
    
    try:
        async with MultiServerMCPClient(mcp_config) as client:
            tools = client.get_tools()
            
            # Test direct tool call
            for tool in tools:
                if tool.name == "get_city_weather":
                    print("🔧 Testing get_city_weather tool...")
                    result = await tool.ainvoke({"city_name": "San Francisco"})
                    print(f"📊 San Francisco weather result:\n{result[:2000]}...")
                    break
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(test_individual_city())
    else:
        asyncio.run(generate_mcp_weather_report())