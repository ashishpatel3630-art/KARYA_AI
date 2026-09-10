from mcp.gateway.registry import registry


ASSETS = {
    "C-101": {
        "asset_id": "C-101",
        "name": "Compressor C-101",
        "type": "compressor",
        "status": "running",
        "temperature": 92,
        "temperature_unit": "C",
    },
    "P-101": {
        "asset_id": "P-101",
        "name": "Pump P-101",
        "type": "pump",
        "status": "running",
    },
}


def get_asset(asset_id: str) -> dict:

    asset = ASSETS.get(asset_id)

    if asset is None:
        raise ValueError(
            f"Industrial asset not found: {asset_id}"
        )

    return asset


def list_assets() -> dict:

    return {
        "assets": list(ASSETS.values())
    }


def get_asset_status(asset_id: str) -> dict:

    asset = get_asset(asset_id)

    return {
        "asset_id": asset_id,
        "status": asset["status"],
    }


registry.register(
    name="get_asset",
    server="industrial",
    description="Retrieve industrial asset information",
    handler=get_asset,
)

registry.register(
    name="list_assets",
    server="industrial",
    description="List registered industrial assets",
    handler=list_assets,
)

registry.register(
    name="get_asset_status",
    server="industrial",
    description="Get industrial asset status",
    handler=get_asset_status,
)