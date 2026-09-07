from dataclasses import dataclass


@dataclass(frozen=True)
class AgentPolicy:
    """
    Defines execution limits for the KARYA agent.
    """

    max_plan_steps: int = 6
    max_tool_calls: int = 20
    max_result_length: int = 20_000
    allow_llm_steps: bool = True
    allow_tool_execution: bool = True


DEFAULT_AGENT_POLICY = AgentPolicy()


def validate_policy(
    policy: AgentPolicy,
) -> None:
    """
    Validate an agent policy before execution.
    """

    if policy.max_plan_steps <= 0:
        raise ValueError(
            "max_plan_steps must be greater than zero."
        )

    if policy.max_tool_calls <= 0:
        raise ValueError(
            "max_tool_calls must be greater than zero."
        )

    if policy.max_result_length <= 0:
        raise ValueError(
            "max_result_length must be greater than zero."
        )