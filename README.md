# GenAI-COP-MCP-and-Agents
code repo for stuff shown in the cop meeting

### 🚀 Open Notebooks in Google Colab

weather_udf.ipynb

https://colab.research.google.com/github/craigjurs/GenAI-COP-MCP-and-Agents/blob/main/weather_udf.ipynb

compute_weather_from_local_mcp.ipynb

https://colab.research.google.com/github/craigjurs/GenAI-COP-MCP-and-Agents/blob/main/compute_weather_from_local_mcp.ipynb

weather_mcp.ipynb

https://colab.research.google.com/github/craigjurs/GenAI-COP-MCP-and-Agents/blob/main/weather_mcp.ipynb


arc_agent_developed_ui.ipynb

https://colab.research.google.com/github/craigjurs/GenAI-COP-MCP-and-Agents/blob/main/full_stack_engineering/arc_agent_developed_ui.ipynb

# MCP Demo Walkthrough

This walk-through explains how agents use tools in three phases:

1. **Native Function Calling**
2. **In-Memory MCP Server**
3. **External MCP Server (Stdio)**  
   _Note: Stdio MCP means the Model Context Protocol (MCP) tools are being served via a subprocess that communicates through standard input (stdin) and standard output (stdout)._

Each demo builds up the concept of structured tool usage by AI agents in increasingly modular and scalable ways.

---

## Demo 1: Native Function Calling

### 🎯 Objective

- Build a weather agent that uses a native function to retrieve current conditions and 5-day forecasts for US cities.
- Use Pydantic models to define structured return types.

### 🛠️ Tool Design

- `PydanticWeatherTool` is a plain Python class.
- The function `get_weather_for_cities()` accepts city/state pairs and returns a structured `CityWeather` list.
- The output uses well-defined models: `CityWeather`, `CurrentConditions`, `DailyForecast`, etc.

### 🤖 Agent Setup

- `AssistantAgent` is configured with an OpenAI-compatible tool schema (`type: function`).
- `UserProxyAgent` registers a function map linking tool name to native function.
- The assistant can now call this native Python method.

### 🔁 Execution Flow

```python
user_proxy.register_function(
    function_map={"get_weather_for_cities": weather_tool.get_weather_for_cities}
)
