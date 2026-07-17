from server import mcp

def main():
    # Initialize and run the server
    mcp.run(transport="stdio")
    
    print("MCP Server initialized!")

if __name__ == "__main__":
    main()
