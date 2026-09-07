from collections.abc import Iterator

from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from .context import ConversationContext
from .manager import ConversationManager


class ConversationService:
    """
    High-level conversational service for KARYA.

    Responsibilities:
    - Accept user messages.
    - Maintain conversation history.
    - Send conversation context to the local LLM.
    - Store assistant responses.
    - Support both normal and streaming responses.

    This service does not directly communicate with Ollama.
    LLMService handles the local LLM runtime.
    """

    def __init__(
        self,
        conversation_manager: ConversationManager | None = None,
        llm_service: LLMService | None = None,
    ):
        self.conversation_manager = (
            conversation_manager
            or ConversationManager()
        )

        self.llm_service = (
            llm_service
            or LLMService()
        )

    def chat(
        self,
        user_input: str,
    ) -> str:
        """
        Send a user message and return a complete AI response.
        """

        self._validate_user_input(user_input)

        user_input = user_input.strip()

        self.conversation_manager.add_user_message(
            user_input
        )

        context = (
            self.conversation_manager.build_context()
        )

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role=message["role"],
                    content=message["content"],
                )
                for message in context.to_llm_messages()
            ]
        )

        response = self.llm_service.chat(request)

        assistant_response = response.content.strip()

        if not assistant_response:
            raise ValueError(
                "Conversation received an empty assistant response."
            )

        self.conversation_manager.add_assistant_message(
            assistant_response
        )

        return assistant_response

    def stream(
        self,
        user_input: str,
    ) -> Iterator[str]:
        """
        Stream an AI response while maintaining conversation history.

        The assistant response is accumulated internally and stored
        in conversation memory after streaming completes.
        """

        self._validate_user_input(user_input)

        user_input = user_input.strip()

        self.conversation_manager.add_user_message(
            user_input
        )

        context = (
            self.conversation_manager.build_context()
        )

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role=message["role"],
                    content=message["content"],
                )
                for message in context.to_llm_messages()
            ]
        )

        chunks: list[str] = []

        try:
            for chunk in self.llm_service.stream(request):
                if not chunk:
                    continue

                chunks.append(chunk)

                yield chunk

        except Exception:
            # Remove the user message if streaming fails before
            # an assistant response can be completed.
            self._remove_last_user_message()

            raise

        assistant_response = "".join(chunks).strip()

        if not assistant_response:
            self._remove_last_user_message()

            raise ValueError(
                "Conversation received an empty streamed response."
            )

        self.conversation_manager.add_assistant_message(
            assistant_response
        )

    def get_context(self) -> ConversationContext:
        """Return the current conversation context."""

        return self.conversation_manager.build_context()

    def get_context_text(self) -> str:
        """Return the current conversation as formatted text."""

        return self.conversation_manager.get_context_text()

    def get_messages(self) -> list:
        """Return all messages currently stored in the conversation."""

        return self.conversation_manager.get_messages()

    def message_count(self) -> int:
        """Return the number of messages in the conversation."""

        return self.conversation_manager.message_count()

    def clear(self) -> None:
        """Clear the current conversation."""

        self.conversation_manager.clear()

    def _validate_user_input(
        self,
        user_input: str,
    ) -> None:
        if not isinstance(user_input, str):
            raise TypeError(
                "User input must be a string."
            )

        if not user_input.strip():
            raise ValueError(
                "User input cannot be empty."
            )

    def _remove_last_user_message(self) -> None:
        """
        Remove the latest user message when a generation fails.

        This prevents an incomplete conversation state where a user
        message exists without a corresponding assistant response.
        """

        messages = self.conversation_manager.memory.messages

        if (
            messages
            and messages[-1].role == "user"
        ):
            messages.pop()
