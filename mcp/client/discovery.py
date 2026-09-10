from mcp.client.client import MCPClient


class MCPDiscovery:

    def __init__(
        self,
        client: MCPClient,
    ) -> None:

        self.client = client

    async def discover(self) -> list[dict]:

        response = await self.client.list_tools()

        return response.get(
            "tools",
            []
        )

    async def find(
        self,
        name: str,
    ) -> list[dict]:

        tools = await self.discover()

        return [
            tool
            for tool in tools
            if name.lower()
            in tool["name"].lower()
            or name.lower()
            in tool["description"].lower()
        ]