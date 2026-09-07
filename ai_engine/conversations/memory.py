from dataclasses import dataclass, field
from typing import Literal


MessageRole = Literal["system", "user", "assistant", "tool"]


@dataclass
class ConversationMessage:
    """A single message stored in KARYA conversation memory."""

    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise ValueError("Message content must be a string.")

        self.content = self.content.strip()

        if not self.content:
            raise ValueError("Message content cannot be empty.")


@dataclass
class ConversationMemory:
    """
    In-memory conversation history for KARYA.

    This class intentionally stores only the current conversation.
    Persistent database storage will be added later.
    """

    max_messages: int = 50
    messages: list[ConversationMessage] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if self.max_messages <= 0:
            raise ValueError(
                "max_messages must be greater than zero."
            )

    def add_message(
        self,
        role: MessageRole,
        content: str,
    ) -> ConversationMessage:
        """Add a message to the conversation."""

        message = ConversationMessage(
            role=role,
            content=content,
        )

        self.messages.append(message)

        self._enforce_limit()

        return message

    def add_user_message(
        self,
        content: str,
    ) -> ConversationMessage:
        """Add a user message."""

        return self.add_message(
            role="user",
            content=content,
        )

    def add_assistant_message(
        self,
        content: str,
    ) -> ConversationMessage:
        """Add an assistant message."""

        return self.add_message(
            role="assistant",
            content=content,
        )

    def add_system_message(
        self,
        content: str,
    ) -> ConversationMessage:
        """Add a system message."""

        return self.add_message(
            role="system",
            content=content,
        )

    def add_tool_message(
        self,
        content: str,
    ) -> ConversationMessage:
        """Add a tool result message."""

        return self.add_message(
            role="tool",
            content=content,
        )

    def get_messages(self) -> list[ConversationMessage]:
        """Return a copy of the stored conversation messages."""

        return list(self.messages)

    def get_recent_messages(
        self,
        limit: int,
    ) -> list[ConversationMessage]:
        """Return the most recent messages."""

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        return list(self.messages[-limit:])

    def message_count(self) -> int:
        """Return the number of stored messages."""

        return len(self.messages)

    def is_empty(self) -> bool:
        """Return True when no messages are stored."""

        return not self.messages

    def clear(self) -> None:
        """Clear the entire conversation."""

        self.messages.clear()

    def _enforce_limit(self) -> None:
        """Keep only the newest max_messages messages."""

        overflow = len(self.messages) - self.max_messages

        if overflow > 0:
            del self.messages[:overflow]