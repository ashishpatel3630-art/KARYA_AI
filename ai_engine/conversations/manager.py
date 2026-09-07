from dataclasses import dataclass

from .context import ConversationContext, ConversationContextBuilder
from .memory import ConversationMemory


@dataclass(frozen=True)
class ConversationConfig:
    """Configuration for KARYA conversation management."""

    max_messages: int = 50
    max_context_messages: int = 20
    max_context_characters: int = 20_000

    def __post_init__(self) -> None:
        if self.max_messages <= 0:
            raise ValueError(
                "max_messages must be greater than zero."
            )

        if self.max_context_messages <= 0:
            raise ValueError(
                "max_context_messages must be greater than zero."
            )

        if self.max_context_characters <= 0:
            raise ValueError(
                "max_context_characters must be greater than zero."
            )


class ConversationManager:
    """
    High-level conversation manager for KARYA.

    Responsibilities:

    - Manage conversation memory.
    - Add user/assistant/system/tool messages.
    - Build LLM-ready conversation context.
    - Enforce memory and context limits.
    - Clear the current conversation.

    Persistent database storage will be connected later.
    """

    def __init__(
        self,
        config: ConversationConfig | None = None,
        memory: ConversationMemory | None = None,
        context_builder: ConversationContextBuilder | None = None,
    ):
        self.config = config or ConversationConfig()

        self.memory = memory or ConversationMemory(
            max_messages=self.config.max_messages
        )

        self.context_builder = (
            context_builder
            or ConversationContextBuilder(
                max_context_messages=(
                    self.config.max_context_messages
                ),
                max_context_characters=(
                    self.config.max_context_characters
                ),
            )
        )

    def add_user_message(self, content: str) -> None:
        """Add a user message."""

        self.memory.add_user_message(content)

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message."""

        self.memory.add_assistant_message(content)

    def add_system_message(self, content: str) -> None:
        """Add a system message."""

        self.memory.add_system_message(content)

    def add_tool_message(self, content: str) -> None:
        """Add a tool result message."""

        self.memory.add_tool_message(content)

    def build_context(self) -> ConversationContext:
        """Build the current LLM-ready conversation context."""

        return self.context_builder.build(
            self.memory
        )

    def get_context_text(self) -> str:
        """Return the current conversation as formatted text."""

        return self.build_context().text

    def get_llm_messages(self) -> list[dict[str, str]]:
        """Return conversation messages in LLM-compatible format."""

        return self.build_context().to_llm_messages()

    def get_messages(self):
        """Return all stored conversation messages."""

        return self.memory.get_messages()

    def get_recent_messages(self, limit: int):
        """Return the most recent conversation messages."""

        return self.memory.get_recent_messages(limit)

    def message_count(self) -> int:
        """Return the number of messages currently stored."""

        return self.memory.message_count()

    def is_empty(self) -> bool:
        """Return True when the conversation has no messages."""

        return self.memory.is_empty()

    def clear(self) -> None:
        """Clear the current conversation."""

        self.memory.clear()