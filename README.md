# CrewAI + MCP Integration Example

A practical demonstration of integrating [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers with [CrewAI](https://www.crewai.com/) agents using Docker.

## What This Does

- 🎲 **MCP Server**: FastMCP dice rolling service with HTTP transport
- 🤖 **CrewAI Agent**: Uses MCP tools via `MCPServerAdapter`
- 🔄 **Multi-LLM**: Works with Anthropic Claude or OpenAI
- 🐳 **Docker Ready**: Complete containerized setup

## Architecture

```
┌─────────────────────────────────┐
│      CrewAI Agent               │
│   + MCP Tools Adapter           │
│   + LLM (Claude/GPT)            │
└────────────┬────────────────────┘
             │ HTTP/MCP
             ▼
┌─────────────────────────────────┐
│      FastMCP Server             │
│   • roll_dice(n, sides)         │
│   • server_info()               │
└─────────────────────────────────┘
```

## Quick Start

### 1. Setup Environment

Create `.env` file:

```bash
# Using Anthropic (recommended)
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
# OR using OpenAI
USE_OPENAI=true
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
```

### 2. Run

```bash
docker-compose up --build
```

That's it! The agent will roll 2 d20 dice using the MCP server.

## Project Structure

```
.
├── docker-compose.yml              # Orchestration
├── .env                            # API keys
├── mcp_server/
│   ├── server.py                   # FastMCP dice service
│   ├── Dockerfile
│   └── requirements.txt
└── crew_runner/
    ├── run_crewai_with_mcp.py      # Main example
    ├── llm_factory.py              # LLM setup
    ├── mcp_tool_schema_patch.py    # Schema fixes
    ├── Dockerfile
    └── requirements.txt
```

## How It Works

### 1. MCP Server Exposes Tools

```python
@mcp.tool()
def roll_dice(n: int = 1, sides: int = 6) -> dict:
    rolls = [random.randint(1, sides) for _ in range(n)]
    return {"rolls": rolls, "total": sum(rolls)}
```

### 2. CrewAI Agent Uses Tools

```python
server_params = {
    "url": "http://mcp-dice:8000/mcp",
    "transport": "streamable-http"
}

with MCPServerAdapter(server_params) as tools:
    patch_crewai_mcp_tool_schemas(tools)  # Fix schema compatibility
    
    agent = Agent(
        role="Dice Operator",
        tools=tools,
        llm=llm
    )
```

### 3. Schema Patching

The `patch_crewai_mcp_tool_schemas()` function converts CrewAI's dynamic schemas to proper Pydantic models, ensuring compatibility with both Anthropic and OpenAI.

## Expected Output

```
🤖 [LLM] provider=anthropic model=claude-sonnet-4-5-20250929 key_loaded=True

================================================================================
🔗 [MCP:CONNECTED] url=http://mcp-dice:8000/mcp
🛠️  [MCP:TOOLS] ['roll_dice', 'server_info']
================================================================================

🔧 [PATCH] Fixing MCP tool schemas for LLM compatibility...
   ✓ Fixed schema for tool: roll_dice
   ✓ Fixed schema for tool: server_info

🔧 Tool Execution Started (#1)
Tool: roll_dice
Args: {'n': '2', 'sides': '20'}

🎲🎲 [MCP SERVER] roll_dice EXECUTED: n=2, sides=20, result={'rolls': [14, 6], 'total': 20}

✅ Tool Execution Completed (#1)
Output: {"rolls":[14,6],"total":20}

================================================================================
✅ [CREW:RESULT]
================================================================================
{"rolls": [14, 6], "total": 20}
================================================================================
```

**Key Point:** The `🎲🎲 [MCP SERVER]` message comes from the MCP server itself, proving the tool was actually executed (not hallucinated by the LLM).

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Required (default) |
| `ANTHROPIC_MODEL` | Model name | `claude-sonnet-4-5-20250929` |
| `USE_OPENAI` | Switch to OpenAI | `false` |
| `OPENAI_API_KEY` | OpenAI API key | Required if `USE_OPENAI=true` |
| `OPENAI_MODEL` | Model name | `gpt-4o-mini` |

### MCP Tools

#### `roll_dice(n, sides)`
- **n**: Number of dice (1-100)
- **sides**: Sides per die (2-1000)
- **Returns**: `{"rolls": [...], "total": int}`

#### `server_info()`
- **Returns**: `{"name": str, "version": str, "uptime_seconds": int}`

## Running Without Docker

**Terminal 1 - MCP Server:**
```bash
cd mcp_server
pip install -r requirements.txt
python server.py
```

**Terminal 2 - CrewAI Client:**
```bash
cd crew_runner
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
export MCP_URL=http://127.0.0.1:9000/mcp
python run_crewai_with_mcp.py
```

## Troubleshooting

### "Error connecting to MCP server"
- Check if MCP server is running: `curl http://localhost:9000/mcp`
- Verify docker-compose services are up: `docker-compose ps`

### "API key not found"
- Create `.env` file in project root with your API key
- Or export environment variable: `export ANTHROPIC_API_KEY=...`

### "Schema validation errors"
- The `patch_crewai_mcp_tool_schemas()` should fix these automatically
- Check logs for `[PATCH]` messages to confirm patching succeeded

### Output buffering in Docker
- Already configured with `PYTHONUNBUFFERED=1` and `python -u`
- If issues persist, rebuild: `docker-compose up --build --force-recreate`

## Key Concepts

### Why Schema Patching?
CrewAI's `MCPServerAdapter` generates schemas that some LLM providers reject. The patcher converts them to standard Pydantic models.

### Why Server-Side Logging?
The `🎲🎲 [MCP SERVER]` messages prove tools are actually executed on the server, not hallucinated by the LLM. This is crucial for validating MCP integrations.

### Why Docker?
- Consistent environments
- Easy multi-service orchestration
- Network isolation
- No dependency conflicts

## Learning Resources

- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP docs
- [FastMCP](https://gofastmcp.com/getting-started/welcome) - Simple MCP server framework
- [CrewAI](https://docs.crewai.com/) - AI agent framework


## License

Educational example - use freely and modify as needed.
