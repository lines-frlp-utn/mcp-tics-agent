from mcp.server.fastmcp import FastMCP

from config import conf
from utils.imap_connection import imap_session
from utils.imap_folders import (
    create_folder as create_folder_util,
    move_email as move_email_util
)
from utils.imap_reader import (
    read_by_uid as read_by_uid_util,
    search as search_emails_util,
)


# Create a FastMCP instance with the specified host and
# port, allowing connections from other Docker containers
mcp = FastMCP(
    name="MCP Server - Outlook",
    host=conf.MCP_HOST_OUTLOOK,
    port=conf.MCP_PORT_OUTLOOK
)


# Folder management tools
@mcp.tool()
def create_folder(folder_name: str) -> None:
    """Create a folder."""
    with imap_session() as client:
        create_folder_util(client, folder_name=folder_name)

@mcp.tool()
def move_email_to_folder(uid: str, folder_source: str, folder_destination: str) -> bool:
    """Move an email to a different folder."""
    with imap_session() as client:
        return move_email_util(client, uid=uid, folder_source=folder_source, folder_destination=folder_destination)

# Email reading tools
@mcp.tool()
def read(folder: str, uid: str) -> dict:
    """Read an email message by folder and UID."""
    with imap_session() as client:
        return read_by_uid_util(client, folder=folder, uid=uid)

@mcp.tool()
def search_emails(folder: str, criterion: str, limit: int) -> list[dict]:
    """Search emails in a folder matching an IMAP search criterion (e.g. 'UNSEEN', 'ALL'), up to a limit."""
    with imap_session() as client:
        return search_emails_util(client, folder=folder, criterion=criterion, limit=limit)

@mcp.tool()
def read_unread_items(folder: str = "INBOX", limit: int = 10) -> list[dict]:
    """Read the unread email messages in a folder."""
    with imap_session() as client:
        return search_emails_util(client, criterion="UNSEEN", folder=folder, limit=limit)

@mcp.tool()
def read_all(folder: str = "INBOX", limit: int = 10) -> list[dict]:
    """Read all email messages in a folder."""
    with imap_session() as client:
        return search_emails_util(client, criterion="ALL", folder=folder, limit=limit)
