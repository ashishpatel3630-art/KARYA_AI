from mcp.gateway.registry import registry


def calculate(
    operation: str,
    values: list[float],
) -> dict:

    if not values:
        raise ValueError(
            "values cannot be empty"
        )

    if operation == "average":
        result = sum(values) / len(values)

    elif operation == "sum":
        result = sum(values)

    elif operation == "minimum":
        result = min(values)

    elif operation == "maximum":
        result = max(values)

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    return {
        "operation": operation,
        "values": values,
        "result": result,
    }


registry.register(
    name="calculate",
    server="analytics",
    description="Run analytics calculations",
    handler=calculate,
)