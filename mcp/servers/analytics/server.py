from fastapi import FastAPI


app = FastAPI(
    title="KARYA Analytics MCP Server"
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "analytics",
    }