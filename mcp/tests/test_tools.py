from mcp.servers.industrial.tools import get_asset
from mcp.servers.analytics.tools import calculate


def test_get_asset():

    result = get_asset("C-101")

    assert result["asset_id"] == "C-101"
    assert result["temperature"] == 92


def test_average():

    result = calculate(
        operation="average",
        values=[10, 20, 30],
    )

    assert result["result"] == 20


def test_sum():

    result = calculate(
        operation="sum",
        values=[1, 2, 3],
    )

    assert result["result"] == 6