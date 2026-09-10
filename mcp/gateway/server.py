
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mcp.approval.api import router as approval_router
from mcp.gateway.registry import registry
from mcp.gateway.router import router

# Import tool modules so their tools register automatically.
from mcp.servers.analytics import tools as analytics_tools
from mcp.servers.database import tools as database_tools
from mcp.servers.filesystem import tools as filesystem_tools
from mcp.servers.industrial import tools as industrial_tools
from mcp.servers.knowledge import tools as knowledge_tools
from mcp.servers.system import tools as system_tools


app = FastAPI(
    title="KARYA MCP Gateway",
    version="1.0.0",
)


class ExecuteRequest(BaseModel):
    server: str
    tool: str
    arguments: dict
    user_id: str
    role: str
    work_id: str
    task_id: str


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "karya-mcp-gateway",
    }


@app.get("/tools")
async def list_tools():
    return {
        "tools": registry.list_tools()
    }


@app.post("/execute")
async def execute(request: ExecuteRequest):
    try:
        result = await router.execute(
            server=request.server,
            tool=request.tool,
            arguments=request.arguments,
            user_id=request.user_id,
            role=request.role,
            work_id=request.work_id,
            task_id=request.task_id,
        )

        return {
            "success": True,
            "server": request.server,
            "tool": request.tool,
            "result": result,
        }

    except HTTPException:
        raise

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"MCP gateway error: {str(exc)}",
        ) from exc



app.include_router(approval_router)