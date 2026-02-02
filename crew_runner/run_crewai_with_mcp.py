from __future__ import annotations

import os
import sys
import logging
from dotenv import load_dotenv

# Enable logging to see hook output
logging.basicConfig(level=logging.INFO, format='%(message)s')

load_dotenv()  # loads .env when running locally (outside Docker)

from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter

from llm_factory import make_llm_from_env
from mcp_tool_schema_patch import patch_crewai_mcp_tool_schemas

MCP_URL = os.environ.get("MCP_URL", "http://mcp-dice:8000/mcp")

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
            print(f"\n\n{'='*80}")
            print(f"🔗 [MCP:CONNECTED] url={MCP_URL}")
            print(f"🛠️  [MCP:TOOLS] {[tool.name for tool in tools]}")
            print(f"{'='*80}\n")
            
            # Patch MCP tool schemas for compatibility with both
            # OpenAI and Anthropic
            patch_crewai_mcp_tool_schemas(tools)

            # Agent with MCP tools
            agent = Agent(
                role="Dice Operator",
                goal="Use MCP tools reliably and report results",
                backstory=(
                    "You always call the tool for dice rolls; "
                    "you never guess."
                ),
                tools=tools,
                verbose=True,
                llm=llm,
            )

            task = Task(
                description=(
                    "Roll 2 d20 using the roll_dice tool. "
                    "Return the rolls and the total. Do not guess."
                ),
                expected_output=(
                    "A JSON-like object containing rolls and total."
                ),
                agent=agent,
            )

            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
                tracing=True,
            )

            result = crew.kickoff()
            print(f"\n\n{'='*80}")
            print(f"✅ [CREW:RESULT]")
            print(f"{'='*80}")
            print(result)
            print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n\n{'='*80}")
        print(f"❌ [ERROR] Error connecting to or using MCP server: {e}")
        print(f"❌ [ERROR] Ensure the MCP server is running and accessible at {MCP_URL}")
        print(f"{'='*80}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
