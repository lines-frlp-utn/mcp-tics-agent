from mcp.server.fastmcp import FastMCP

from config import conf
from utils.imap_folders import (
    create_folder as create_folder_util,
    move_email as move_email_util
)
from utils.imap_reader import (
    decodificate_header as decodificate_header_util,
    extract_body as extract_body_util,
    parse_message as parse_message_util,
    read as read_util,
    read_unread_items as read_unread_items_util,
    read_all as read_all_util,
)


# Create a FastMCP instance with the specified host and
# port, allowing connections from other Docker containers
mcp = FastMCP(
    name="MCP Server - Outlook",
    host=conf.MCP_HOST_OUTLOOK,
    port=conf.MCP_PORT_OUTLOOK
)


@mcp.tool()
def create_folder(folder_name: str) -> None:
    """Create a folder."""
    create_folder_util(folder_name=folder_name)

@mcp.tool()
def move_email_to_folder(uid: str, folder_source: str, folder_destination: str) -> bool:
    """Move an email to a different folder."""
    return move_email_util(uid=uid, folder_source=folder_source, folder_destination=folder_destination)

@mcp.tool()
def decodificate_header(value: str | None) -> str:
    """Decodificate an email header."""
    return decodificate_header_util(value=value)

@mcp.tool()
def extract_body(message) -> str:   
    """Extract the body of an email message."""
    return extract_body_util(message=message)

@mcp.tool()
def parse_message(message) -> dict:
    """Parse an email message into a dictionary."""
    return parse_message_util(message=message)

@mcp.tool()
def read(folder: str, uid: str) -> dict:
    """Read an email message by folder and UID."""
    return read_util(folder=folder, uid=uid)

@mcp.tool()
def read_unread_items(folder: str) -> list[dict]:
    """Read all unread email messages in a folder."""
    return read_unread_items_util(folder=folder)

@mcp.tool()
def read_all(folder: str) -> list[dict]:
    """Read all email messages in a folder."""
    return read_all_util(folder=folder)