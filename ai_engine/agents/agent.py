from .loop import AgentLoop
from .state import AgentState


class KaryaAgent:
    """
    High-level public interface for the KARYA agent.

    Other parts of the application should preferably
    interact with KaryaAgent instead of directly
    controlling the planner or executor.
    """

    def __init__(
        self,
        loop: AgentLoop | None = None,
    ):
        self.loop = loop or AgentLoop()

    def run(
        self,
        user_input: str,
    ) -> AgentState:
        """
        Execute a user request through the complete
        KARYA agent lifecycle.
        """

        return self.loop.run(
            user_input
        )

    def ask(
        self,
        user_input: str,
    ) -> str:
        """
        Execute a user request and return only the
        final answer.

        Raises RuntimeError when agent execution fails.
        """

        state = self.run(
            user_input
        )

        if state.error:
            raise RuntimeError(
                state.error
            )

        if not state.completed:
            raise RuntimeError(
                "Agent execution did not complete."
            )

        if not state.final_answer:
            raise RuntimeError(
                "Agent completed without a final answer."
            )

        return state.final_answer