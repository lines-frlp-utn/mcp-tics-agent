from mcp.server.fastmcp import FastMCP

from config import conf


# Create a FastMCP instance with the specified host and
# port, allowing connections from other Docker containers
mcp = FastMCP(
    name="MCP Server - Outlook",
    host=conf.MCP_HOST_OUTLOOK,
    port=conf.MCP_PORT_OUTLOOK
)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"