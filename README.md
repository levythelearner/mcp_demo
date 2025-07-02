# Demo repo for my sharing at HCM Data Meetup #20 - "Making Sense of MCP and AI Agents: What You Need to Know"

Interactive AI agents using MCP (Model Context Protocol) for external tool integration. This demo showcases three distinct use cases for building agents with external tools through MCP servers.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS Bedrock access (for the agent demo) - or modify code for Azure/Vertex if preferred
- UV package manager (recommended)

### Setup
```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone/download this demo folder
cd mcp_demo

# Create virtual environment and install dependencies using uv.lock
uv sync

# Activate the environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Configure AWS (for agent demo)
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Alternative Setup (without UV)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install langchain-aws langgraph langchain-mcp-adapters fastmcp boto3 requests

# Configure AWS (for agent demo)
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```
## 🔧 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude/Agent  │◄──►│  MCP Protocol    │◄──►│  External Tools │
│                 │    │                  │    │                 │
│ • LangGraph     │    │ • JSON-RPC       │    │ • Math Server   │
│ • ReAct Pattern │    │ • Tool Discovery │    │ • Weather API   │
│ • LLM Reasoning │    │ • Type Safety    │    │ • Custom Tools  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Benefits of MCP:**
- **Separation of Concerns:** Tools run in separate processes
- **Reusability:** Same servers work with multiple agents
- **Security:** Isolated tool execution
- **Scalability:** Independent server scaling
- **Standardization:** Common protocol across tools
## 🛠️ MCP Servers

### Math Server (`math_server.py`)
Mathematical calculation tools via MCP protocol using FastMCP.

**Available Tools:**
- `add(a, b)` - Addition
- `multiply(a, b)` - Multiplication  
- `subtract(a, b)` - Subtraction
- `divide(a, b)` - Division
- `power(base, exponent)` - Exponentiation
- `calculate_average(numbers)` - Average of comma-separated numbers

**Run standalone:**
```bash
python math_server.py
```

### Weather Server (`weather_server.py`)
Weather data tools using National Weather Service API.

**Available Tools:**
- `get_city_weather(city_name)` - Weather for major US cities
- `get_weather_forecast(lat, lon, location)` - Detailed forecasts
- `get_current_conditions(lat, lon, location)` - Current conditions
- `get_weather_alerts(lat, lon, location)` - Active weather alerts

**Supported Cities:**
San Francisco, New York, Los Angeles, Chicago, Houston, Phoenix, Philadelphia, San Antonio, San Diego, Dallas, Miami, Atlanta, Boston, Seattle, Denver

**Run standalone:**
```bash
python weather_server.py  
```
## 📁 Claude Desktop Configuration

Add this to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "math-demo": {
      "command": "/path/to/your/.venv/bin/python",
      "args": ["/path/to/your/math_server.py"]
    },
    "weather-demo": {
      "command": "/path/to/your/.venv/bin/python", 
      "args": ["/path/to/your/weather_server.py"]
    }
  }
}
```

**macOS Location:** `~/Library/Application Support/Claude/claude_config.json`

**Windows Location:** `%APPDATA%\Claude\claude_config.json`


## 🎯 Three Use Cases

### 1. **Basic Agent** (`1_basic_agent.py`)
Real-time conversational ReAct Agent with @tool Decorators.

**Use Case:** Customer support chatbot with live data access
- 🔢 Math: Ask for calculations (add, subtract, multiply, divide)
- 🌤️ Weather: Ask about weather in 10 major US cities
- 🏙️ City Info: Ask about city information


**Run it:**
```bash
source .venv/bin/activate && python 1_basic_agent.py
```
or 

```bash
source .venv/bin/activate && python 1_basic_agent.py --demo
```

### 2. **Agent with MCP Tools** (`2_agent_with_mcp.py`)
Same real-time conversational ReAct Agent as case 1, with external MCP servers as tools.

**Use Case:** Customer support chatbot with live data access
- 🔢 Math: Ask for calculations (add, subtract, multiply, divide)
- 🌤️ Weather: Ask about weather in 10 major US cities

**Run it:**
```bash
source .venv/bin/activate && python 2_agent_with_mcp.py
```
or 

```bash
source .venv/bin/activate && python 2_agent_with_mcp.py --demo
```


**Code pattern:**
```python
async with MultiServerMCP(config) as client:
    tools = client.get_tools()
    agent = create_react_agent(llm, tools)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
```

### 3. **Automatic Weather Agent** (`3_weather_agent_mcp.py`)
Non-interactive agent with external MCP servers as tools. Use to run and append weather report into txt file.

**Use Case:** 

**Run it:**
```bash
source .venv/bin/activate && python 3_weather_agent_mcp.py
```
or 

```bash
source .venv/bin/activate && python 3_weather_agent_mcp.py --demo
```


## 🐛 Troubleshooting

**MCP Connection Issues:**
- Verify Python paths in configuration
- Check virtual environment activation
- Ensure servers are executable

**AWS Bedrock Errors:**
- Configure AWS credentials: `aws configure`
- Enable Claude model access in AWS console
- Check region settings

**Tool Execution Failures:**
- Test servers individually first
- Check network connectivity for weather API
- Verify tool parameter formats


## 🔗 Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AWS Bedrock Setup](https://docs.aws.amazon.com/bedrock/)

---

*For more information, please contact me at:*
- 🐙 **GitHub:** [levythelearner](https://github.com/levythelearner)
- 📧 **Email:** [levy.thelearner@gmail.com](mailto:levy.thelearner@gmail.com)  
- 💼 **LinkedIn:** [levythelearner](https://www.linkedin.com/in/levythelearner/)