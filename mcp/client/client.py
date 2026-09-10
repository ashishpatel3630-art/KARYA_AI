from typing import Any

import httpx


class MCPClient:

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8100",
    ) -> None:

        self.base_url = base_url.rstrip("/")

    async def list_tools(self) -> dict:

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/tools"
            )

            response.raise_for_status()

            return response.json()

    async def execute(
        self,
        *,
        server: str,
        tool: str,
        arguments: dict[str, Any] | None = None,
        user_id: str = "system",
        role: str = "viewer",
    ) -> dict:

        payload = {
            "server": server,
            "tool": tool,
            "arguments": arguments or {},
            "user_id": user_id,
            "role": role,
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{self.base_url}/execute",
                json=payload,
            )

            response.raise_for_status()

            return response.json()