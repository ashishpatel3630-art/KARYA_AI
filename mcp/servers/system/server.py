from fastapi import FastAPI


app = FastAPI(
    title="KARYA System MCP Server"
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "system",
    }