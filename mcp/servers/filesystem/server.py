from fastapi import FastAPI


app = FastAPI(
    title="KARYA Filesystem MCP Server"
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "filesystem",
    }