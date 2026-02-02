import random
import time
from fastmcp import FastMCP

START_TS = time.time()
VERSION = "0.1.0"

mcp = FastMCP("dice-service")

@mcp.tool()
def roll_dice(n: int = 1, sides: int = 6) -> dict:
    """
    Roll n dice, each with sides number of sides.
    Returns a dict: {"rolls": [...], "total": int}
    
    Args:
        n: Number of dice to roll (1-100)
        sides: Number of sides per die (2-1000)
    """
    if not (1 <= n <= 100):
        raise ValueError("n must be between 1 and 100")
    if not (2 <= sides <= 1000):
        raise ValueError("sides must be between 2 and 1000")
    
    rolls = [random.randint(1, sides) for _ in range(n)]
    return {"rolls": rolls, "total": sum(rolls)}

@mcp.tool()
def server_info() -> dict:
    """
    Get server information.
    Returns server name, version, and uptime in seconds.
    """
    return {
        "name": "dice-service",
        "version": VERSION,
        "uptime_seconds": int(time.time() - START_TS),
    }

if __name__ == "__main__":
    # Choose ONE of the following `mcp.run(...)` lines:
    # - Local dev (binds to localhost only):
    # mcp.run(transport="http", host="127.0.0.1", port=9000)
    #
    # - Docker (binds to all interfaces so port mapping works):
    mcp.run(transport="http", host="0.0.0.0", port=8000)
    #
    # FastMCP HTTP transport exposes the MCP endpoint at /mcp by default.
