from fastapi import FastAPI


app = FastAPI(
    title="KARYA Database MCP Server"
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "database",
    }