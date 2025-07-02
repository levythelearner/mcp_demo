#!/usr/bin/env python3
"""
Demo 1: Basic ReAct Agent with @tool Decorators
Interactive chat demonstrating how to build agents with @tool decorated functions
"""

import asyncio
import httpx
from datetime import datetime
from langchain_aws import ChatBedrockConverse
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import boto3
import os

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# US Cities with coordinates
US_CITIES = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698),
    "Phoenix": (33.4484, -112.0740),
    "Philadelphia": (39.9526, -75.1652),
    "San Antonio": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "Dallas": (32.7767, -96.7970),
    "Denver": (39.7392, -104.9903)
}

def create_bedrock_client():
    """Create a Bedrock client."""
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    return bedrock_client

async def make_nws_request(url: str) -> dict | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making NWS request: {e}")
            return None

@tool
async def get_city_weather(city_name: str) -> str:
    """Get current weather forecast for a US city."""
    if city_name not in US_CITIES:
        return f"City '{city_name}' not found. Available cities: {', '.join(US_CITIES.keys())}"
    
    lat, lon = US_CITIES[city_name]
    
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{lat},{lon}"
    points_data = await make_nws_request(points_url)
    
    if not points_data:
        return f"Unable to fetch forecast data for {city_name}."
    
    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    
    if not forecast_data:
        return f"Unable to fetch detailed forecast for {city_name}."
    
    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:3]:  # Show next 3 periods
        forecast = f"  {period['name']}: {period['temperature']}°{period['temperatureUnit']} - {period['shortForecast']}"
        forecasts.append(forecast)
    
    return f"{city_name} Weather Forecast:\\n" + "\\n".join(forecasts)

@tool
def calculate(a: float, b: float, operation: str) -> str:
    """Perform mathematical calculations. Operations: add, subtract, multiply, divide"""
    try:
        if operation.lower() == "add":
            result = a + b
            return f"{a} + {b} = {result}"
        elif operation.lower() == "subtract":
            result = a - b
            return f"{a} - {b} = {result}"
        elif operation.lower() == "multiply":
            result = a * b
            return f"{a} × {b} = {result}"
        elif operation.lower() == "divide":
            if b == 0:
                return "Error: Cannot divide by zero"
            result = a / b
            return f"{a} ÷ {b} = {result}"
        else:
            return f"Unknown operation: {operation}. Use: add, subtract, multiply, divide"
    except Exception as e:
        return f"Error calculating: {e}"

@tool
def get_city_info(city_name: str) -> str:
    """Get basic information about major US cities."""
    city_info = {
        "New York": "Population: ~8.3M, Known for: Times Square, Statue of Liberty",
        "Los Angeles": "Population: ~3.9M, Known for: Hollywood, Beaches", 
        "Chicago": "Population: ~2.7M, Known for: Deep dish pizza, Architecture",
        "Houston": "Population: ~2.3M, Known for: Space Center, Oil industry",
        "Phoenix": "Population: ~1.6M, Known for: Desert, Sunshine",
        "Philadelphia": "Population: ~1.6M, Known for: Liberty Bell, Cheesesteaks",
        "San Antonio": "Population: ~1.5M, Known for: The Alamo, River Walk",
        "San Diego": "Population: ~1.4M, Known for: Zoo, Perfect weather",
        "Dallas": "Population: ~1.3M, Known for: Cowboys, BBQ",
        "Denver": "Population: ~715K, Known for: Mountains, Mile high city"
    }
    
    if city_name in city_info:
        return f"{city_name}: {city_info[city_name]}"
    else:
        available = ", ".join(city_info.keys())
        return f"City '{city_name}' not found. Available cities: {available}"

def create_llm():
    """Create LLM with error handling."""
    try:
        bedrock_client = create_bedrock_client()
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
        print("❌ No LLM available. Please configure AWS Bedrock.")
        return None

async def interactive_agent_with_tools():
    """Run interactive chat with @tool decorated functions."""
    print("🤖 Basic Agent Demo - Interactive Chat with @tool Functions")
    print("=" * 65)
    print("Available tools:")
    print("🌤️  Weather: Ask about weather in major US cities")
    print("🔢 Math: Ask for calculations (add, subtract, multiply, divide)")
    print("🏙️  City Info: Ask about city information")
    print("Type 'quit' to exit")
    print()
    
    # Create LLM
    llm = create_llm()
    if not llm:
        return
    
    # Create tools list - demonstrating @tool decorator usage
    tools = [get_city_weather, calculate, get_city_info]
    
    # Create ReAct agent with tools
    agent = create_react_agent(llm, tools)
    
    print(f"🛠️  Agent ready with tools: {[tool.name for tool in tools]}")
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
                            print(f"🔧 Using @tool: {tool_call['name']}")
                    elif hasattr(msg, 'name') and msg.name:
                        print(f"🔧 Used @tool: {msg.name}")
            
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
            print("\\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

async def demo_mode():
    """Run automated demo showing @tool functionality."""
    print("🎬 Demo Mode - Automated @tool Examples")
    print("=" * 50)
    
    llm = create_llm()
    if not llm:
        return
    
    tools = [get_city_weather, calculate, get_city_info]
    agent = create_react_agent(llm, tools)
    
    # Demo queries showcasing different @tool functions
    demo_queries = [
        "What's the weather in Denver?",
        "Calculate 25 plus 17",
        "Tell me about Chicago",
        "What's 15 times 8?",
        "Get weather for San Francisco and info about the city"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\\n🔍 Demo {i}: {query}")
        try:
            response = await agent.ainvoke({
                "messages": [{"role": "user", "content": query}]
            })
            
            # Show tool usage
            if 'messages' in response and len(response['messages']) > 1:
                for msg in response['messages'][1:-1]:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            print(f"🔧 @tool used: {tool_call['name']}")
            
            # Show response
            if 'messages' in response and response['messages']:
                result = response['messages'][-1].content
                print(f"🤖 Response: {result[:200]}{'...' if len(result) > 200 else ''}")
            else:
                print("❌ No response generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo_mode())
    else:
        asyncio.run(interactive_agent_with_tools())