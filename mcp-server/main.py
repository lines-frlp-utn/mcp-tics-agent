from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server import mcp


# Generate the FastAPI app from the FastMCP instance
mcp_app = mcp.streamable_http_app()

# Create the FastAPI app and integrate the lifespan of the FastMCP sub-app
app = FastAPI(lifespan=lambda _app: mcp.session_manager.run())

# Habilitate CORS explicitly to allow the Inspector to connect without issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development purposes; adjust in production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint for Docker/compose
@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Mount the FastMCP sub-application
app.mount("/", mcp_app)
