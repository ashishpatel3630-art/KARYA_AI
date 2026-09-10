from dataclasses import dataclass, field
import os


@dataclass(frozen=True)
class MCPSettings:
    app_name: str = "KARYA MCP Gateway"
    environment: str = os.getenv("ENVIRONMENT", "development")

    gateway_host: str = os.getenv("MCP_GATEWAY_HOST", "127.0.0.1")
    gateway_port: int = int(os.getenv("MCP_GATEWAY_PORT", "8100"))

    audit_enabled: bool = os.getenv(
        "MCP_AUDIT_ENABLED", "true"
    ).lower() == "true"

    allowed_roots: list[str] = field(
        default_factory=lambda: [
            os.getenv("KARYA_DATA_DIR", "./data")
        ]
    )


settings = MCPSettings()