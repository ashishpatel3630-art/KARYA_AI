from fastapi import FastAPI


app = FastAPI(
    title="KARYA Industrial MCP Server"
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "industrial",
    }