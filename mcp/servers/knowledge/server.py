from fastapi import FastAPI

from mcp.servers.knowledge import tools


app = FastAPI(
    title="KARYA Knowledge MCP Server"
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "knowledge",
    }