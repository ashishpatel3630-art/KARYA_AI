from typing import Any

from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from .executor import AgentExecutor
from .planner import AgentPlanner
from .policies import (
    AgentPolicy,
    DEFAULT_AGENT_POLICY,
    validate_policy,
)
from .state import AgentState


class AgentLoop:
    """
    Main orchestration loop for the KARYA agent.

    Lifecycle:

        User Request
             ↓
        Planning
             ↓
        Step Execution
             ↓
        Verified Results
             ↓
        Final Synthesis
             ↓
        Final Answer
    """

    def __init__(
        self,
        planner: AgentPlanner | None = None,
        executor: AgentExecutor | None = None,
        llm_service: LLMService | None = None,
        policy: AgentPolicy | None = None,
    ):
        self.llm_service = (
            llm_service or LLMService()
        )

        self.policy = (
            policy or DEFAULT_AGENT_POLICY
        )

        validate_policy(
            self.policy
        )

        self.planner = (
            planner
            or AgentPlanner(
                llm_service=self.llm_service
            )
        )

        self.executor = (
            executor
            or AgentExecutor(
                llm_service=self.llm_service,
                tool_registry=self.planner.tool_registry,
            )
        )

    # =============================================================
    # PUBLIC API
    # =============================================================

    def run(
        self,
        user_input: str,
    ) -> AgentState:
        """
        Execute a complete KARYA agent task.

        The method always returns AgentState for execution
        failures so callers can inspect the error safely.
        """

        if not user_input or not user_input.strip():
            raise ValueError(
                "User input cannot be empty."
            )

        state = AgentState(
            user_input=user_input.strip()
        )

        try:
            # -----------------------------------------------------
            # 1. PLAN
            # -----------------------------------------------------

            state = self.planner.plan_task(
                state
            )

            self._validate_plan_limits(
                state
            )

            # -----------------------------------------------------
            # 2. EXECUTE
            # -----------------------------------------------------

            while not state.completed:

                self._validate_execution_limits(
                    state
                )

                state = (
                    self.executor.execute_current_step(
                        state
                    )
                )

            # -----------------------------------------------------
            # 3. FINAL SYNTHESIS
            # -----------------------------------------------------

            state.final_answer = (
                self._synthesize_final_answer(
                    state
                )
            )

            state.completed = True

            return state

        except Exception as exc:

            state.error = str(
                exc
            )

            state.completed = False

            return state

    # =============================================================
    # PLAN VALIDATION
    # =============================================================

    def _validate_plan_limits(
        self,
        state: AgentState,
    ) -> None:
        """
        Validate that the generated plan respects
        the configured execution policy.
        """

        if not state.plan:
            raise ValueError(
                "Agent planner returned an empty plan."
            )

        if len(state.plan) > (
            self.policy.max_plan_steps
        ):
            raise ValueError(
                "Agent plan exceeds the maximum "
                "allowed number of steps."
            )

        for index, step in enumerate(
            state.plan,
            start=1,
        ):

            if not isinstance(
                step,
                dict,
            ):
                raise ValueError(
                    f"Plan step {index} is invalid."
                )

            action = step.get(
                "action"
            )

            if not isinstance(
                action,
                str,
            ) or not action.strip():

                raise ValueError(
                    f"Plan step {index} "
                    "contains an invalid action."
                )

    # =============================================================
    # EXECUTION LIMITS
    # =============================================================

    def _validate_execution_limits(
        self,
        state: AgentState,
    ) -> None:
        """
        Prevent runaway agent execution.
        """

        if (
            len(state.tool_calls)
            >= self.policy.max_tool_calls
        ):
            raise RuntimeError(
                "Agent exceeded the maximum "
                "allowed number of tool calls."
            )

        if state.current_step >= len(
            state.plan
        ):
            state.completed = True
            return

        if state.current_step < 0:
            raise RuntimeError(
                "Agent execution state is invalid."
            )

    # =============================================================
    # FINAL SYNTHESIS
    # =============================================================

    def _synthesize_final_answer(
        self,
        state: AgentState,
    ) -> str:
        """
        Generate the final user-facing answer.

        The LLM is allowed to synthesize wording,
        but not invent or modify verified results.
        """

        if not state.tool_results:
            return (
                "The agent completed without producing "
                "any execution results."
            )

        verified_results = (
            self._build_verified_results(
                state
            )
        )

        prompt = f"""
You are the final answer component of KARYA,
a sovereign industrial AI system.

Answer the user's request using ONLY the verified
execution results below.

USER REQUEST:
{state.user_input}

VERIFIED EXECUTION RESULTS:
{verified_results}

STRICT RULES:

1. Treat verified execution results as ground truth.

2. Do not invent facts.

3. Do not modify verified numeric values.

4. Do not perform new calculations.

5. Do not contradict tool results.

6. Do not claim access to external systems.

7. Do not claim access to sensors.

8. Do not claim access to databases unless a real
   tool provided that information.

9. Do not claim access to files unless a real
   tool provided that information.

10. Do not claim network access.

11. Do not expose internal agent state.

12. Do not describe hidden reasoning.

13. Give the user a direct and concise answer.

14. If the verified results are insufficient,
    clearly state that the information is insufficient.

15. Preserve important units and source information.

Return ONLY the final answer text.
""".strip()

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are a precise final-answer "
                        "synthesis engine. "
                        "Use only verified execution results."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=prompt,
                ),
            ],
            temperature=0.0,
        )

        response = self.llm_service.chat(
            request
        )

        final_answer = (
            response.content.strip()
        )

        if not final_answer:
            raise ValueError(
                "Final answer synthesis returned "
                "an empty response."
            )

        if len(final_answer) > (
            self.policy.max_result_length
        ):
            final_answer = (
                final_answer[
                    : self.policy.max_result_length
                ].rstrip()
            )

        return final_answer

    # =============================================================
    # VERIFIED RESULT FORMATTING
    # =============================================================

    def _build_verified_results(
        self,
        state: AgentState,
    ) -> list[dict[str, Any]]:
        """
        Build a clean representation of verified results
        for final synthesis.
        """

        verified_results = []

        for item in state.tool_results:

            if not isinstance(
                item,
                dict,
            ):
                continue

            verified_results.append(
                {
                    "step": item.get(
                        "step"
                    ),
                    "action": item.get(
                        "action"
                    ),
                    "tool": item.get(
                        "tool"
                    ),
                    "result": item.get(
                        "result"
                    ),
                }
            )

        return verified_results