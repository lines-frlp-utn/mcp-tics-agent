import os

from mcp.server.fastmcp import FastMCP


# Create a FastMCP instance with the specified host and
# port, allowing connections from other Docker containers
mcp = FastMCP(
    "MCP Server - LINES",
    host=os.environ.get("MCP_HOST", "0.0.0.0"),
    port=int(os.environ.get("MCP_PORT", "8000")),
)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"