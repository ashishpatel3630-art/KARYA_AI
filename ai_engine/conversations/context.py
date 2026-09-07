from dataclasses import dataclass
from typing import Any

from .memory import ConversationMemory, ConversationMessage


@dataclass(frozen=True)
class ConversationContext:
    """
    Structured context prepared for KARYA's local LLM.

    The context contains only conversation information that
    has already been stored in memory.
    """

    messages: list[ConversationMessage]
    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.messages, list):
            raise ValueError("messages must be a list.")

        if not isinstance(self.text, str):
            raise ValueError("text must be a string.")

    def is_empty(self) -> bool:
        """Return True when no conversation context exists."""

        return not self.messages

    def message_count(self) -> int:
        """Return the number of messages in this context."""

        return len(self.messages)

    def to_llm_messages(self) -> list[dict[str, str]]:
        """
        Convert conversation messages into a format compatible
        with the KARYA LLM service.
        """

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in self.messages
        ]


class ConversationContextBuilder:
    """
    Build structured LLM context from ConversationMemory.
    """

    def __init__(
        self,
        max_context_messages: int = 20,
        max_context_characters: int = 20_000,
    ):
        if max_context_messages <= 0:
            raise ValueError(
                "max_context_messages must be greater than zero."
            )

        if max_context_characters <= 0:
            raise ValueError(
                "max_context_characters must be greater than zero."
            )

        self.max_context_messages = max_context_messages
        self.max_context_characters = max_context_characters

    def build(
        self,
        memory: ConversationMemory,
    ) -> ConversationContext:
        """Build context from the most recent conversation messages."""

        if not isinstance(memory, ConversationMemory):
            raise TypeError(
                "memory must be a ConversationMemory instance."
            )

        messages = memory.get_recent_messages(
            self.max_context_messages
        )

        messages = self._trim_to_character_limit(messages)

        text = self._format_messages(messages)

        return ConversationContext(
            messages=messages,
            text=text,
        )

    def _trim_to_character_limit(
        self,
        messages: list[ConversationMessage],
    ) -> list[ConversationMessage]:
        """Keep the newest messages within the character budget."""

        selected: list[ConversationMessage] = []
        total_characters = 0

        for message in reversed(messages):
            message_size = len(message.content)

            if (
                selected
                and total_characters + message_size
                > self.max_context_characters
            ):
                break

            selected.append(message)
            total_characters += message_size

        selected.reverse()

        return selected

    def _format_messages(
        self,
        messages: list[ConversationMessage],
    ) -> str:
        """Create a readable context string for LLM prompts."""

        if not messages:
            return ""

        formatted: list[str] = []

        for message in messages:
            role = message.role.upper()

            formatted.append(
                f"{role}:\n{message.content}"
            )

        return "\n\n".join(formatted)

    def build_prompt_context(
        self,
        memory: ConversationMemory,
    ) -> str:
        """
        Return only the formatted conversation text.

        Useful when constructing an LLM prompt.
        """

        return self.build(memory).text