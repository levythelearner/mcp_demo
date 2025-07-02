#!/usr/bin/env python3
"""
Demo MCP Server: Math Server
Provides mathematical calculation tools via MCP protocol using FastMCP.
"""

import argparse
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Math")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together"""
    result = a + b
    print(f"🧮 Adding: {a} + {b} = {result}")
    return result

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together"""
    result = a * b
    print(f"🧮 Multiplying: {a} × {b} = {result}")
    return result

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract second number from first number"""
    result = a - b
    print(f"🧮 Subtracting: {a} - {b} = {result}")
    return result

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide first number by second number"""
    if b == 0:
        return "Error: Cannot divide by zero"
    result = a / b
    print(f"🧮 Dividing: {a} ÷ {b} = {result}")
    return result

@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent"""
    result = base ** exponent
    print(f"🧮 Power: {base} ^ {exponent} = {result}")
    return result

@mcp.tool()
def calculate_average(numbers: str) -> float:
    """Calculate average of comma-separated numbers"""
    try:
        # Parse comma-separated numbers
        num_list = [float(x.strip()) for x in numbers.split(',')]
        if not num_list:
            return "Error: No numbers provided"
        
        average = sum(num_list) / len(num_list)
        print(f"🧮 Average of {num_list} = {average}")
        return average
    except ValueError:
        return "Error: Invalid number format. Use comma-separated numbers like '1,2,3,4'"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Math MCP Server Demo")
    parser.add_argument("--transport", default="stdio", help="Transport type (default: stdio)")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=6000, help="Port number (default: 6000)")
    
    args = parser.parse_args()
    
    print("🔢 Starting Math MCP Server...")
    print(f"📡 Transport: {args.transport}")
    
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)