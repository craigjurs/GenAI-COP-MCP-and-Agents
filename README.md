# GenAI-COP-MCP-and-Agents
code repo for stuff shown in the cop meeting

### 🚀 Open Notebooks in Google Colab

weather_udf.ipynb

https://colab.research.google.com/github/craigjurs/GenAI-COP-MCP-and-Agents/blob/main/weather_udf.ipynb


weather_mcp.ipynb

https://colab.research.google.com/github/craigjurs/GenAI-COP-MCP-and-Agents/blob/main/weather_mcp.ipynb


arc_agent_developed_ui.ipynb

https://colab.research.google.com/github/craigjurs/GenAI-COP-MCP-and-Agents/blob/main/full_stack_engineering/arc_agent_developed_ui.ipynb

# MCP Demo Walkthrough

This walk-through explains how agents use tools in three phases:

1. **Native Function Calling**
2. **In-Memory MCP Server**
3. **External MCP Server (Stdio)**  
   *Note: Stdio MCP means the Model Context Protocol (MCP) tools are being served via a subprocess that communicates through standard input (stdin) and standard output (stdout).*

Each demo builds up the concept of structured tool usage by AI agents in increasingly modular and scalable ways.

---

## Demo 1: Native Function Calling

### Objective

- Build a weather agent that uses a native function to retrieve current conditions and 5-day forecasts for US cities.
- Use Pydantic models to define structured return types.

### Tool Design

- `PydanticWeatherTool` is a plain Python class.
- The function `get_weather_for_cities()` accepts city/state pairs and returns a structured `CityWeather` list.
- The output uses well-defined models: `CityWeather`, `CurrentConditions`, `DailyForecast`, etc.

### Agent Setup

- `AssistantAgent` is configured with an OpenAI-compatible tool schema (type: function).
- `UserProxyAgent` registers a function map linking tool name to native function.
- The assistant can now call this native Python method.

### Execution Flow

```python
user_proxy.register_function(
    function_map={"get_weather_for_cities": weather_tool.get_weather_for_cities}
)
```

- The LLM decides to invoke `get_weather_for_cities()`.
- Returns rich structured JSON back to the assistant for summarization.

### Key Point

> Native functions can be turned into callable tools using OpenAI-compatible schema + function registration.

---

## Demo 2: MCP In-Memory Server

### Objective

- Refactor the weather tool into an in-memory MCP server.
- Move from native Python binding to MCP tool architecture.

### Tool Design (MCP)

- Define an `@mcp.tool()` function inside a `FastMCP`-backed server.
- Signature and return types remain Pydantic-based.
- The MCP server serves tools that are now callable using the MCP protocol.

```python
mcp = FastMCP("WeatherToolSingle")

@mcp.tool()
async def get_weather_for_cities(...):
    ...
```

### Test via In-Memory Client

```python
client = Client(mcp)
async with client:
    await client.call_tool("get_weather_for_cities", ...)
```

### Key Point

> The MCP server/tool pattern brings tool introspection, logging, versioning, and standard interfaces while staying local and fast.

---

## Demo 3: External MCP Server via Stdio

### Objective

- Run a tool from an external repo using MCP + Stdio transport.
- No local import of business logic. Agent talks to a subprocess.

### Setup: Load Tools from GitHub

```python
params = StdioServerParams(
    command="uvx",
    args=["--from", "git+https://github.com/adhikasp/mcp-weather.git", "mcp-weather"],
    env={"ACCUWEATHER_API_KEY": os.environ["ACCUWEATHER_API_KEY"]}
)

tools = await mcp_server_tools(params)
```

- Downloads and launches the server tool in an isolated subprocess.
- Agent gets the schema via `tools = await mcp_server_tools(...)`.

### Tool Usage

```python
function_map = {adapter.name: make_adapter_func(adapter) for adapter in tools}

user_proxy.register_function(function_map=function_map)
```

- Agent can now call tools hosted in an external subprocess!

### Key Point

> Stdio MCP enables runtime tool loading from GitHub or packages, enabling agents to use third-party tools securely and flexibly.

---

### ⚠️ Important Warning on External MCP Tools

**Security Risk:** Running MCP servers from untrusted external repositories (like GitHub) can be extremely dangerous in production environments.  
Tools downloaded and executed via subprocess (e.g., `uvx --from git+...`) can execute arbitrary code and access local secrets or files.

- Never use third-party MCP tools in production without thorough review.
- Use signed packages and secure dependency management.
- Always run external tools inside sandboxed or containerized environments with minimal permissions.
- Implement strict network/firewall rules to isolate subprocess access.

---

# Automated Agent Workflows for Software Engineering

## Case Study: Blood Donor Eligibility App

### Purpose

This project showcases how we can use AI agents to autonomously design, build, test, and run software using a repeatable, inspectable, and fully sandboxed process.

> It’s not just about building one app, it's about creating reusable engineering workflows that:
> - Decompose complex tasks
> - Assign responsibilities to specialized agents
> - Validate and repair code in a closed loop
> - Run end-to-end in cloud notebooks like Google Colab

---

## Agent Roles & Responsibilities

We use Autogen to spin up a multi-agent team, where each agent is given a system prompt, coding privileges, and limited turns.  
They collaborate asynchronously just like a human team:

- `Project_Manager`: Orchestrates the pipeline and prompts agents
- `Engineering_Lead`: Writes the technical design document
- `Backend_Engineer`: Builds Python business logic
- `Test_Engineer`: Writes unittest-based test coverage
- `Frontend_Engineer`: Builds a UI using Gradio
- `Executor`: Securely runs shell/Python code inside a sandbox

---

## Workflow Overview

Each agent works off of prior outputs. The whole pipeline runs autonomously:

1. **Design** → technical spec created by `Engineering_Lead`
2. **Backend** → logic implemented by `Backend_Engineer`
3. **Test & Repair** → run tests, auto-repair backend if needed
4. **Frontend** → UI built by `Frontend_Engineer`
5. **Validation** → sandbox test of `app.py`

All files are saved to a working directory (`coding/`) and inspected between phases.

---

## Autonomous Test & Repair Loop

The most important automation is in Phase 3, where we validate the backend using real test runs:

```python
execution_result = local_code_executor.execute_code_blocks([
    CodeBlock(code=f"python -m unittest test_{module_name}", language="shell")
])
```

If tests fail:

- The output is used to auto-repair the backend logic or test cases
- The system retries up to N times
- No human intervention is needed unless all retries fail

---

## Sandboxed Execution in Colab

We use a secure executor to run all Python and shell commands in a temporary local environment:

```python
local_code_executor = LocalCommandLineCodeExecutor(
    work_dir=unified_work_dir,
    timeout=120,
)
```

This isolates execution, ensuring that:

- Broken code won’t crash the kernel
- Agents can safely compile, import, and test modules
- Validation is grounded in real runtime behavior

---

## Frontend Validation

Frontend UI code is validated by actually running `app.py`:

```python
validation_result = local_code_executor.execute_code_blocks([
    CodeBlock(code='python coding/app.py', language="shell")
])
```

It passes if:

- The exit code is `0`, or
- The generated file exists and is non-trivial (> 100 bytes)

This flexible check allows us to accept valid UIs even if Gradio just spins up a server without terminating.

---

## Files Generated Per Run

| File                        | Agent               |
|-----------------------------|---------------------|
| `donor_eligibility_design.md` | Engineering_Lead   |
| `donor_eligibility.py`       | Backend_Engineer    |
| `test_donor_eligibility.py`  | Test_Engineer       |
| `app.py`                     | Frontend_Engineer   |

---

## Final Outcome

- Turns requirements into running code  
- Validates everything before proceeding  
- Recovers from failures automatically  
- Can be re-used to generate other software – just takes some prompt and requirements tuning  


### 🔁 Execution Flow

```python
user_proxy.register_function(
    function_map={"get_weather_for_cities": weather_tool.get_weather_for_cities}
)
