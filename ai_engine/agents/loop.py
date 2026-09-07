from __future__ import annotations

from typing import Any

from .executor import AgentExecutor
from .planner import AgentPlanner
from .policies import (
    DEFAULT_AGENT_POLICY,
    AgentPolicy,
    validate_policy,
)
from .state import AgentState
from rag.schemas import deduplicate_citations


class AgentLoop:
    """
    Main execution loop for KARYA agents.

    Responsibilities:

    1. Create an execution plan.
    2. Validate the plan.
    3. Execute steps sequentially.
    4. Preserve verified execution results.
    5. Stop immediately on execution failure.
    6. Produce a grounded final answer.
    7. Never add unsupported claims to verified results.
    """

    MAX_STEPS = 20

    def __init__(
        self,
        planner: AgentPlanner | None = None,
        executor: AgentExecutor | None = None,
        policy: AgentPolicy | None = None,
    ) -> None:
        self.policy = policy or DEFAULT_AGENT_POLICY
        validate_policy(self.policy)
        self.planner = planner or AgentPlanner()
        self.executor = executor or AgentExecutor()

    # =============================================================
    # MAIN LOOP
    # =============================================================

    def run(
        self,
        user_input: str,
    ) -> AgentState:
        """
        Execute a complete agent workflow.

        Flow:

            User Input
                ↓
            Planner
                ↓
            Plan Validation
                ↓
            Step Execution
                ↓
            Verified Results
                ↓
            Final Answer
        """

        if not isinstance(
            user_input,
            str,
        ):
            raise ValueError(
                "Agent input must be a string."
            )

        user_input = user_input.strip()

        if not user_input:
            raise ValueError(
                "Agent input cannot be empty."
            )

        state = AgentState(
            user_input=user_input
        )

        try:
            # -----------------------------------------------------
            # CREATE PLAN
            # -----------------------------------------------------

            plan = self.planner.plan_task(
                state
            )

            if not isinstance(
                plan,
                list,
            ):
                raise ValueError(
                    "Planner must return a list of plan steps."
                )

            state.plan = plan

            if not state.plan:
                raise ValueError(
                    "Planner returned an empty plan."
                )

            # -----------------------------------------------------
            # VALIDATE PLAN
            # -----------------------------------------------------

            self._validate_plan_limits(
                state
            )

            self._validate_plan_dependencies(
                state
            )

            # -----------------------------------------------------
            # EXECUTE PLAN
            # -----------------------------------------------------

            while (
                state.current_step
                < len(state.plan)
            ):
                self.executor.execute_current_step(
                    state
                )

            # -----------------------------------------------------
            # FINAL ANSWER
            # -----------------------------------------------------

            self._set_final_answer(
                state
            )

            state.completed = True

            return state

        except Exception as exc:
            state.error = str(exc)
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
        Prevent runaway agent plans.
        """

        max_steps = min(
            self.MAX_STEPS,
            self.policy.max_plan_steps,
        )

        if len(state.plan) > max_steps:
            raise ValueError(
                f"Agent plan exceeds the maximum allowed "
                f"step count of {max_steps}."
            )

    def _validate_plan_dependencies(
        self,
        state: AgentState,
    ) -> None:
        """
        Validate that every declared dependency refers
        to a real earlier step.
        """

        step_ids: set[str] = set()

        for index, step in enumerate(
            state.plan
        ):
            if not isinstance(
                step,
                dict,
            ):
                raise ValueError(
                    f"Plan step {index + 1} is invalid."
                )

            step_id = step.get(
                "step_id",
                f"step_{index + 1}",
            )

            if not isinstance(
                step_id,
                str,
            ):
                raise ValueError(
                    f"Plan step {index + 1} has an invalid step_id."
                )

            step_id = step_id.strip()

            if not step_id:
                raise ValueError(
                    f"Plan step {index + 1} has an empty step_id."
                )

            if step_id in step_ids:
                raise ValueError(
                    f"Duplicate plan step_id: {step_id}"
                )

            step_ids.add(
                step_id
            )

        # Dependencies must point to existing steps.
        # They may only point to steps before the current step.
        for index, step in enumerate(
            state.plan
        ):
            dependencies = step.get(
                "depends_on",
                [],
            )

            if dependencies is None:
                dependencies = []

            if not isinstance(
                dependencies,
                list,
            ):
                raise ValueError(
                    f"Plan step {index + 1} dependencies "
                    "must be a list."
                )

            current_step_id = step.get(
                "step_id",
                f"step_{index + 1}",
            )

            for dependency in dependencies:
                if not isinstance(
                    dependency,
                    str,
                ):
                    raise ValueError(
                        f"Dependency in {current_step_id} "
                        "must be a string."
                    )

                dependency = dependency.strip()

                if dependency not in step_ids:
                    raise ValueError(
                        f"Plan step {current_step_id} "
                        f"depends on unknown step '{dependency}'."
                    )

                if dependency == current_step_id:
                    raise ValueError(
                        f"Plan step {current_step_id} "
                        "cannot depend on itself."
                    )

                dependency_index = self._find_step_index(
                    state.plan,
                    dependency,
                )

                if dependency_index >= index:
                    raise ValueError(
                        f"Plan step {current_step_id} "
                        f"depends on step '{dependency}' "
                        "which has not executed yet."
                    )

    # =============================================================
    # STEP LOOKUP
    # =============================================================

    def _find_step_index(
        self,
        plan: list[dict[str, Any]],
        step_id: str,
    ) -> int:
        """
        Return the zero-based index of a plan step.
        """

        for index, step in enumerate(
            plan
        ):
            if (
                isinstance(step, dict)
                and step.get(
                    "step_id",
                    f"step_{index + 1}",
                )
                == step_id
            ):
                return index

        return -1

    # =============================================================
    # FINAL ANSWER
    # =============================================================

    def _set_final_answer(
        self,
        state: AgentState,
    ) -> None:
        """
        Set the final answer from the last successful
        execution step.

        KARYA intentionally does NOT perform another LLM
        synthesis here.

        Reason:

        The final execution step has already been instructed
        to produce the grounded recommendation. Running another
        LLM after that can introduce unsupported claims.

        Therefore:

            verified step result
                    ↓
            clean final answer
        """

        last_result = self._get_last_result(
            state
        )

        if last_result is None:
            raise ValueError(
                "Agent completed without a verified execution result."
            )

        cleaned = self._clean_final_result(
            last_result
        )

        if not cleaned:
            raise ValueError(
                "Agent completed with an empty final answer."
            )

        state.final_answer = cleaned

        citations = deduplicate_citations(state.citations)
        if citations:
            sources = "\n".join(
                citation.user_facing_label(index)
                for index, citation in enumerate(citations, start=1)
            )
            state.final_answer = f"{state.final_answer}\n\nSources:\n{sources}"

    # =============================================================
    # LAST RESULT
    # =============================================================

    def _get_last_result(
        self,
        state: AgentState,
    ) -> str | None:
        """
        Return the result from the last successfully
        executed plan step.
        """

        if not state.tool_results:
            return None

        for record in reversed(
            state.tool_results
        ):
            if not isinstance(
                record,
                dict,
            ):
                continue

            result = record.get(
                "result"
            )

            if result is None:
                continue

            result_text = str(
                result
            ).strip()

            if result_text:
                return result_text

        return None

    # =============================================================
    # FINAL RESULT CLEANUP
    # =============================================================

    def _clean_final_result(
        self,
        result: str,
    ) -> str:
        """
        Clean harmless execution-wrapper text from the
        final LLM result.

        This method does NOT rewrite the actual content.

        It only removes common wrappers such as:

            EXECUTION STEP:

            EXECUTION STEP COMPLETE:

            RECOMMENDATION:

        The underlying verified content is preserved.
        """

        if not isinstance(
            result,
            str,
        ):
            result = str(
                result
            )

        cleaned = result.strip()

        if not cleaned:
            return ""

        # ---------------------------------------------------------
        # Remove leading execution wrapper.
        # ---------------------------------------------------------

        prefixes = (
            "EXECUTION STEP COMPLETE:",
            "EXECUTION STEP:",
        )

        changed = True

        while changed:
            changed = False

            for prefix in prefixes:
                if cleaned.upper().startswith(
                    prefix
                ):
                    cleaned = cleaned[
                        len(prefix):
                    ].strip()

                    changed = True
                    break

        # ---------------------------------------------------------
        # If the result contains a leading "RECOMMENDATION:"
        # marker, remove only the marker.
        #
        # Do NOT remove the actual recommendation.
        # ---------------------------------------------------------

        if cleaned.upper().startswith(
            "RECOMMENDATION:"
        ):
            cleaned = cleaned[
                len("RECOMMENDATION:"):
            ].strip()

        # ---------------------------------------------------------
        # Remove unnecessary surrounding quotation marks
        # only when the ENTIRE answer is quoted.
        # ---------------------------------------------------------

        if (
            len(cleaned) >= 2
            and cleaned.startswith('"')
            and cleaned.endswith('"')
        ):
            cleaned = cleaned[1:-1].strip()

        if (
            len(cleaned) >= 2
            and cleaned.startswith("'")
            and cleaned.endswith("'")
        ):
            cleaned = cleaned[1:-1].strip()

        return cleaned

    # =============================================================
    # VERIFIED RESULTS
    # =============================================================

    def _build_verified_results(
        self,
        state: AgentState,
    ) -> list[dict[str, Any]]:
        """
        Return normalized verified execution results.

        Supports the current executor schema:

            {
                "step": 1,
                "step_id": "step_1",
                "result": "..."
            }

        and the older schema:

            {
                "step": 1,
                "step_id": "step_1",
                "success": True,
                "output": "..."
            }
        """

        verified: list[dict[str, Any]] = []

        for record in state.tool_results:

            if not isinstance(
                record,
                dict,
            ):
                continue

            result = record.get(
                "result"
            )

            # Backward compatibility.
            if result is None:
                success = record.get(
                    "success"
                )

                output = record.get(
                    "output"
                )

                error = record.get(
                    "error"
                )

                if success is False:
                    continue

                if output is not None:
                    result = output

                elif error is not None:
                    continue

            if result is None:
                continue

            result_text = str(
                result
            ).strip()

            if not result_text:
                continue

            verified.append(
                {
                    "step": record.get(
                        "step"
                    ),
                    "step_id": record.get(
                        "step_id"
                    ),
                    "action": record.get(
                        "action"
                    ),
                    "tool": record.get(
                        "tool"
                    ),
                    "result": result_text,
                }
            )

        return verified

    # =============================================================
    # FALLBACK SYNTHESIS
    # =============================================================

    def _synthesize_final_answer(
        self,
        state: AgentState,
    ) -> str:
        """
        Legacy fallback synthesis.

        Normally this method is NOT used.

        KARYA prefers the last verified execution result
        because an additional LLM call can introduce
        unsupported information.

        This method is retained for compatibility with
        existing code/tests that may call it directly.
        """

        verified_results = (
            self._build_verified_results(
                state
            )
        )

        if not verified_results:
            raise ValueError(
                "No verified execution results are available "
                "for final synthesis."
            )

        sections: list[str] = []

        for item in verified_results:
            sections.append(
                f"STEP {item.get('step', '?')} "
                f"({item.get('step_id', 'unknown')})\n"
                f"{item.get('result', '')}"
            )

        return "\n\n".join(
            sections
        )
