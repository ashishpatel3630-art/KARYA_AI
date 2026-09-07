import pytest

from agents.agent import KaryaAgent
from agents.loop import AgentLoop
from agents.policies import AgentPolicy
from agents.state import AgentState
from tools.calculator import CalculatorTool
from tools.registry import ToolRegistry


# =============================================================
# BASIC AGENT TESTS
# =============================================================


def test_calculator_agent():
    agent = KaryaAgent()

    state = agent.run(
        "Calculate 100 + 400"
    )

    assert state.completed is True
    assert state.error is None
    assert state.plan
    assert state.tool_results

    assert (
        state.tool_results[0]["tool"]
        == "calculator"
    )


def test_file_reader_agent():
    agent = KaryaAgent()

    state = agent.run(
        "Read file rag/test_ingestion_document.pdf"
    )

    assert state.completed is True
    assert state.error is None
    assert state.tool_results

    assert (
        state.tool_results[0]["tool"]
        == "file_reader"
    )


def test_search_agent():
    agent = KaryaAgent()

    state = agent.run(
        "Search compressor C-101"
    )

    assert state.completed is True
    assert state.error is None
    assert state.tool_results

    assert (
        state.tool_results[0]["tool"]
        == "search"
    )


def test_agent_rejects_empty_input():
    agent = KaryaAgent()

    with pytest.raises(ValueError):
        agent.run("")


def test_agent_rejects_whitespace_input():
    agent = KaryaAgent()

    with pytest.raises(ValueError):
        agent.run("   ")


# =============================================================
# MULTI-STEP AGENT
# =============================================================


def test_multi_step_agent():
    agent = KaryaAgent()

    state = agent.run(
        "Find the temperature of Compressor C-101 "
        "and calculate how much it exceeds 75 C."
    )

    assert state.completed is True
    assert state.error is None

    assert len(state.plan) == 2
    assert len(state.tool_results) == 2

    assert (
        state.plan[0]["tool"]
        == "search"
    )

    assert (
        state.plan[1]["tool"]
        == "calculator"
    )


# =============================================================
# STATE TESTS
# =============================================================


def test_agent_state_helpers():
    state = AgentState(
        user_input="Calculate 10 + 20"
    )

    assert state.has_plan() is False
    assert state.has_results() is False
    assert state.has_error() is False
    assert state.remaining_steps() == 0
    assert state.current_plan_step() is None


def test_agent_state_plan_helpers():
    state = AgentState(
        user_input="Calculate 10 + 20",
        plan=[
            {
                "action": "Calculate 10 + 20",
                "tool": "calculator",
                "arguments": {
                    "expression": "10 + 20"
                },
            },
            {
                "action": "Calculate 30 * 2",
                "tool": "calculator",
                "arguments": {
                    "expression": "30 * 2"
                },
            },
        ],
    )

    assert state.has_plan() is True
    assert state.remaining_steps() == 2

    assert (
        state.current_plan_step()["tool"]
        == "calculator"
    )

    state.current_step = 1

    assert state.remaining_steps() == 1

    assert (
        state.current_plan_step()["arguments"][
            "expression"
        ]
        == "30 * 2"
    )


def test_agent_state_reset():
    state = AgentState(
        user_input="Calculate 10 + 20",
        plan=[
            {
                "action": "Calculate 10 + 20",
                "tool": "calculator",
                "arguments": {
                    "expression": "10 + 20"
                },
            }
        ],
        current_step=1,
        tool_calls=[
            {
                "tool": "calculator"
            }
        ],
        tool_results=[
            {
                "step": 1,
                "result": "30"
            }
        ],
        final_answer="30",
        completed=True,
        error=None,
    )

    state.reset_execution()

    assert state.current_step == 0
    assert state.tool_calls == []
    assert state.tool_results == []
    assert state.final_answer is None
    assert state.completed is False
    assert state.error is None


# =============================================================
# CALCULATOR DEPENDENCY TESTS
# =============================================================


def test_previous_result_requires_previous_execution():
    agent = KaryaAgent()

    state = AgentState(
        user_input="Calculate something"
    )

    with pytest.raises(ValueError):
        agent.loop.executor._get_previous_result(
            state
        )


def test_numeric_value_extraction_temperature():
    agent = KaryaAgent()

    result = agent.loop.executor._extract_numeric_value(
        "Operating temperature: 92 C"
    )

    assert result == "92"


def test_numeric_value_extraction_decimal_temperature():
    agent = KaryaAgent()

    result = agent.loop.executor._extract_numeric_value(
        "The temperature is 87.5 °C"
    )

    assert result == "87.5"


def test_numeric_value_extraction_pressure():
    agent = KaryaAgent()

    result = agent.loop.executor._extract_numeric_value(
        "Pressure: 18 bar"
    )

    assert result == "18"


def test_numeric_value_extraction_rpm():
    agent = KaryaAgent()

    result = agent.loop.executor._extract_numeric_value(
        "Pump speed: 1500 RPM"
    )

    assert result == "1500"


def test_numeric_value_extraction_voltage():
    agent = KaryaAgent()

    result = agent.loop.executor._extract_numeric_value(
        "Voltage: 12.5 V"
    )

    assert result == "12.5"


def test_numeric_value_extraction_percentage():
    agent = KaryaAgent()

    result = agent.loop.executor._extract_numeric_value(
        "Load: 75%"
    )

    assert result == "75"


def test_numeric_value_extraction_no_value():
    agent = KaryaAgent()

    with pytest.raises(ValueError):
        agent.loop.executor._extract_numeric_value(
            "No numeric measurement available."
        )


def test_numeric_value_extraction_ambiguous():
    agent = KaryaAgent()

    with pytest.raises(ValueError):
        agent.loop.executor._extract_numeric_value(
            "Page 2, chunk 4, similarity 0.82"
        )


# =============================================================
# EXECUTOR DEPENDENCY TESTS
# =============================================================


def test_previous_result_resolution():
    agent = KaryaAgent()

    state = AgentState(
        user_input="test"
    )

    state.tool_results.append(
        {
            "step": 1,
            "action": "Read temperature",
            "tool": "search",
            "result": "Temperature: 92 C",
        }
    )

    arguments = {
        "expression": "$PREVIOUS_RESULT - 75"
    }

    resolved = (
        agent.loop.executor._resolve_tool_arguments(
            state=state,
            tool_name="calculator",
            arguments=arguments,
        )
    )

    assert (
        resolved["expression"]
        == "92 - 75"
    )


def test_previous_result_not_mutating_original_arguments():
    agent = KaryaAgent()

    state = AgentState(
        user_input="test"
    )

    state.tool_results.append(
        {
            "step": 1,
            "action": "Read temperature",
            "tool": "search",
            "result": "Temperature: 92 C",
        }
    )

    arguments = {
        "expression": "$PREVIOUS_RESULT - 75"
    }

    original_expression = arguments[
        "expression"
    ]

    agent.loop.executor._resolve_tool_arguments(
        state=state,
        tool_name="calculator",
        arguments=arguments,
    )

    assert (
        arguments["expression"]
        == original_expression
    )


# =============================================================
# EXECUTOR FAILURE TESTS
# =============================================================


def test_unknown_tool_is_rejected():
    agent = KaryaAgent()

    state = AgentState(
        user_input="test"
    )

    step = {
        "action": "Execute unknown tool",
        "tool": "does_not_exist",
        "arguments": {},
    }

    with pytest.raises(ValueError):
        agent.loop.executor.execute_step(
            state=state,
            step=step,
        )


def test_invalid_step_is_rejected():
    agent = KaryaAgent()

    state = AgentState(
        user_input="test"
    )

    with pytest.raises(ValueError):
        agent.loop.executor.execute_step(
            state=state,
            step="invalid",
        )


def test_empty_action_is_rejected():
    agent = KaryaAgent()

    state = AgentState(
        user_input="test"
    )

    step = {
        "action": "",
        "tool": None,
        "arguments": {},
    }

    with pytest.raises(ValueError):
        agent.loop.executor.execute_step(
            state=state,
            step=step,
        )


# =============================================================
# LOOP TESTS
# =============================================================


def test_loop_returns_error_state_on_execution_failure():
    agent = KaryaAgent()

    state = agent.run(
        "Read file /definitely/not/a/real/file.pdf"
    )

    assert state.completed is False
    assert state.error is not None


def test_loop_final_answer_exists():
    agent = KaryaAgent()

    state = agent.run(
        "Calculate 20 + 30"
    )

    assert state.completed is True
    assert state.final_answer is not None
    assert state.final_answer.strip()


# =============================================================
# POLICY TESTS
# =============================================================


def test_agent_policy_rejects_zero_plan_steps():
    with pytest.raises(ValueError):
        AgentLoop(
            policy=AgentPolicy(
                max_plan_steps=0
            )
        )


def test_agent_policy_rejects_zero_tool_calls():
    with pytest.raises(ValueError):
        AgentLoop(
            policy=AgentPolicy(
                max_tool_calls=0
            )
        )


def test_agent_policy_rejects_zero_result_length():
    with pytest.raises(ValueError):
        AgentLoop(
            policy=AgentPolicy(
                max_result_length=0
            )
        )


# =============================================================
# CALCULATOR SECURITY
# =============================================================


def test_calculator_rejects_python_code():
    calculator = CalculatorTool()

    with pytest.raises(ValueError):
        calculator.execute(
            "__import__('os').system('whoami')"
        )


def test_calculator_rejects_function_calls():
    calculator = CalculatorTool()

    with pytest.raises(ValueError):
        calculator.execute(
            "abs(-10)"
        )


def test_calculator_rejects_boolean_expression():
    calculator = CalculatorTool()

    with pytest.raises(ValueError):
        calculator.execute(
            "True"
        )


# =============================================================
# REGISTRY TESTS
# =============================================================


def test_default_registry_contains_required_tools():
    agent = KaryaAgent()

    tools = (
        agent.loop.executor.tool_registry.list_tools()
    )

    assert "calculator" in tools
    assert "file_reader" in tools
    assert "search" in tools


def test_registry_unknown_tool():
    registry = ToolRegistry()

    assert (
        registry.exists(
            "does_not_exist"
        )
        is False
    )