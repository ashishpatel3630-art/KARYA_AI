from __future__ import annotations

from agents.executor import AgentExecutor
from agents.state import AgentState
from tools.permissions import PermissionLevel
from tools.registry import ToolRegistry


def build_executor() -> AgentExecutor:
    """
    Build an AgentExecutor using the real KARYA ToolRegistry.
    """

    registry = ToolRegistry()

    # Python execution is deny-by-default.
    # Explicitly grant EXECUTE permission for this integration test.
    python_tool = registry.get("python")

    if python_tool.permissions is None:
        raise RuntimeError(
            "PythonTool permission manager is not configured."
        )

    python_tool.permissions.grant(
        PermissionLevel.EXECUTE
    )

    return AgentExecutor(
        tool_registry=registry
    )


def test_calculator_tool_integration() -> None:
    """
    Test:

        AgentExecutor
            ↓
        ToolRegistry
            ↓
        CalculatorTool
            ↓
        ToolResult
    """

    executor = build_executor()

    state = AgentState(
        user_input="Calculate 25 * 4 + 10"
    )

    output = executor.execute_step(
        state=state,
        step={
            "action": "calculate the requested expression",
            "tool": "calculator",
            "arguments": {
                "expression": "25 * 4 + 10"
            },
        },
    )

    print("\n=== CALCULATOR INTEGRATION ===")
    print("Output:", output)
    print("Tool calls:", state.tool_calls)

    assert output == "110"

    assert len(state.tool_calls) == 1

    tool_call = state.tool_calls[0]

    assert tool_call["tool"] == "calculator"
    assert tool_call["success"] is True
    assert tool_call["output"] == 110
    assert tool_call["error"] is None


def test_python_tool_integration() -> None:
    """
    Test:

        AgentExecutor
            ↓
        ToolRegistry
            ↓
        PythonTool
            ↓
        Sandbox
            ↓
        ToolResult
    """

    executor = build_executor()

    state = AgentState(
        user_input="Use Python to calculate 25 * 4"
    )

    output = executor.execute_step(
        state=state,
        step={
            "action": "execute Python calculation",
            "tool": "python",
            "arguments": {
                "code": "print(25 * 4)"
            },
        },
    )

    print("\n=== PYTHON INTEGRATION ===")
    print("Output:", output)
    print("Tool calls:", state.tool_calls)

    assert output == "100"

    assert len(state.tool_calls) == 1

    tool_call = state.tool_calls[0]

    assert tool_call["tool"] == "python"
    assert tool_call["success"] is True
    assert tool_call["output"] == "100\n"
    assert tool_call["error"] is None


def test_python_permission_denied() -> None:
    """
    Verify Python execution remains deny-by-default.
    """

    registry = ToolRegistry()

    executor = AgentExecutor(
        tool_registry=registry
    )

    state = AgentState(
        user_input="Execute Python"
    )

    try:
        executor.execute_step(
            state=state,
            step={
                "action": "execute Python code",
                "tool": "python",
                "arguments": {
                    "code": "print(2 + 2)"
                },
            },
        )

    except ValueError as exc:

        print("\n=== PYTHON PERMISSION TEST ===")
        print("Expected failure:", exc)

        assert "Permission denied" in str(exc)

    else:
        raise AssertionError(
            "Python execution should have been denied."
        )


def test_file_reader_tool_integration() -> None:
    """
    Verify FileReaderTool can be executed through
    AgentExecutor -> ToolRegistry.
    """

    executor = build_executor()

    state = AgentState(
        user_input="Read the test ingestion document."
    )

    output = executor.execute_step(
        state=state,
        step={
            "action": "read the test document",
            "tool": "file_reader",
            "arguments": {
                "file_path": "rag/test_ingestion_document.pdf"
            },
        },
    )

    print("\n=== FILE READER INTEGRATION ===")
    print("Output:")
    print(output)
    print("Tool calls:", state.tool_calls)

    assert output
    assert "Compressor C-101" in output

    assert len(state.tool_calls) == 1

    tool_call = state.tool_calls[0]

    assert tool_call["tool"] == "file_reader"
    assert tool_call["success"] is True
    assert tool_call["error"] is None


def test_search_tool_integration() -> None:
    """
    Verify SearchTool can be executed through
    AgentExecutor -> ToolRegistry.
    """

    executor = build_executor()

    state = AgentState(
        user_input="Find the test ingestion document."
    )

    output = executor.execute_step(
        state=state,
        step={
            "action": "search for the test document",
            "tool": "search",
            "arguments": {
                "directory": ".",
                "query": "test_ingestion_document",
                "max_results": 10,
            },
        },
    )

    print("\n=== SEARCH INTEGRATION ===")
    print("Output:", output)
    print("Tool calls:", state.tool_calls)

    assert "test_ingestion_document.pdf" in output

    assert len(state.tool_calls) == 1

    tool_call = state.tool_calls[0]

    assert tool_call["tool"] == "search"
    assert tool_call["success"] is True
    assert tool_call["error"] is None


if __name__ == "__main__":

    test_calculator_tool_integration()

    test_python_tool_integration()

    test_python_permission_denied()

    test_file_reader_tool_integration()

    test_search_tool_integration()

    print("\n==========================================")
    print("AGENT → TOOL REGISTRY INTEGRATION PASSED")
    print("==========================================")