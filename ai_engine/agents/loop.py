
from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from .executor import AgentExecutor
from .planner import AgentPlanner
from .state import AgentState


class AgentLoop:
    """Controls the planning, execution, and final synthesis lifecycle."""

    def __init__(
        self,
        planner: AgentPlanner | None = None,
        executor: AgentExecutor | None = None,
        llm_service: LLMService | None = None,
    ):
        self.llm_service = llm_service or LLMService()

        self.planner = planner or AgentPlanner(
            llm_service=self.llm_service
        )

        self.executor = executor or AgentExecutor(
            llm_service=self.llm_service,
            tool_registry=self.planner.tool_registry,
        )

    def run(self, user_input: str) -> AgentState:
        """Plan, execute, and synthesize a final answer."""

        if not user_input or not user_input.strip():
            raise ValueError(
                "User input cannot be empty."
            )

        state = AgentState(
            user_input=user_input.strip()
        )

        try:
            # 1. CREATE PLAN
            state = self.planner.plan_task(state)

            # 2. EXECUTE PLAN
            while not state.completed:
                state = self.executor.execute_current_step(
                    state
                )

            # 3. SYNTHESIZE FINAL ANSWER
            state.final_answer = self._synthesize_final_answer(
                state
            )

            return state

        except Exception as exc:
            state.error = str(exc)
            state.completed = False

            return state

    def _synthesize_final_answer(
        self,
        state: AgentState,
    ) -> str:
        """Generate a concise final answer using verified results."""

        if not state.tool_results:
            return (
                "The agent completed without producing "
                "any execution results."
            )

        verified_results = []

        for item in state.tool_results:
            verified_results.append(
                {
                    "step": item["step"],
                    "action": item["action"],
                    "tool": item.get("tool"),
                    "result": item["result"],
                }
            )

        prompt = f"""
You are the final answer component of KARYA,
a sovereign industrial AI system.

Answer the user's request using ONLY the verified
execution results provided below.

USER REQUEST:
{state.user_input}

VERIFIED EXECUTION RESULTS:
{verified_results}

STRICT RULES:

- Treat the execution results as ground truth.
- Do not change, recalculate, or contradict verified tool results.
- Do not invent facts.
- Do not invent additional calculations.
- Do not claim that external systems were accessed.
- Do not mention internal planning unless useful.
- Do not expose raw internal agent state.
- Give the user a concise and direct answer.
- If a tool result is numeric, preserve the exact verified value.
- If the available results are insufficient, clearly say so.

Return only the final answer text.
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

        response = self.llm_service.chat(request)

        final_answer = response.content.strip()

        if not final_answer:
            raise ValueError(
                "Final answer synthesis returned an empty response."
            )

        return final_answer