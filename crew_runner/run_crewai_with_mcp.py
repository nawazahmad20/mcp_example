from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env when running locally (outside Docker)

from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter

from llm_factory import make_llm_from_env
from mcp_tool_schema_patch import patch_crewai_mcp_tool_schemas

MCP_URL = os.environ.get("MCP_URL", "http://mcp-dice:8000/mcp")

def before_hook(ctx):
    print(f"[TOOL:BEFORE] name={ctx.tool_name} input={ctx.tool_input}")
    return True

def after_hook(ctx):
    print(f"[TOOL:AFTER]  name={ctx.tool_name} result={ctx.tool_result}")
    if "roll_dice" in ctx.tool_name.lower():
        print("🎲🎲 CONFIRMED: roll_dice MCP tool was executed (not hallucinated).")
    return None

def main():
    # Server parameters for Streamable HTTP transport
    server_params = {
        "url": MCP_URL,
        "transport": "streamable-http"
    }

    try:
        llm = make_llm_from_env()

        # Connect to MCP server and get tools
        with MCPServerAdapter(server_params) as tools:
            print(f"[MCP:CONNECTED] url={MCP_URL}")
            print(f"[MCP:TOOLS] {[tool.name for tool in tools]}")
            
            # Patch MCP tool schemas for compatibility with both OpenAI and Anthropic
            patch_crewai_mcp_tool_schemas(tools)

            # Agent with MCP tools
            agent = Agent(
                role="Dice Operator",
                goal="Use MCP tools reliably and report results",
                backstory="You always call the tool for dice rolls; you never guess.",
                tools=tools,
                verbose=True,
                llm=llm,
                tool_call_hooks=[before_hook, after_hook],
            )

            task = Task(
                description="Roll 2 d20 using the roll_dice tool. Return the rolls and the total. Do not guess.",
                expected_output="A JSON-like object containing rolls and total.",
                agent=agent,
            )

            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )

            result = crew.kickoff()
            print("\n[CREW:RESULT]\n", result)

    except Exception as e:
        print(f"[ERROR] Error connecting to or using MCP server: {e}")
        print(f"[ERROR] Ensure the MCP server is running and accessible at {MCP_URL}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
