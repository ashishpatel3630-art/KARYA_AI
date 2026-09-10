import platform
import sys

from mcp.gateway.registry import registry


def status() -> dict:

    return {
        "system": platform.system(),
        "release": platform.release(),
        "python": sys.version,
        "service": "KARYA",
        "network_mode": "isolated",
    }


def ping() -> dict:

    return {
        "status": "pong"
    }


registry.register(
    name="status",
    server="system",
    description="Get KARYA system status",
    handler=status,
)

registry.register(
    name="ping",
    server="system",
    description="Ping KARYA system",
    handler=ping,
)