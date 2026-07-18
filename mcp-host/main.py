from fastapi import FastAPI

from client import call_lines_tool

app = FastAPI()


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/demo/lines/add")
async def demo_lines_add(a: int, b: int) -> dict[str, int] | None:
    """Smoke-test: llama la tool `add` del MCP Server LINES a traves del cliente embebido."""
    return await call_lines_tool("add", {"a": a, "b": b})
