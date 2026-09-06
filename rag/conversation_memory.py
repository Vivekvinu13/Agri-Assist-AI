from typing import Dict, List


class ConversationMemory:
    """
    Simple in-memory conversation history for Agri Assist AI.

    Each conversation is identified by a conversation_id.
    """

    def __init__(self):
        self._conversations: Dict[str, List[dict]] = {}

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):
        """Add a message to a conversation."""

        if not conversation_id or not conversation_id.strip():
            raise ValueError(
                "conversation_id cannot be empty."
            )

        if role not in {
            "user",
            "assistant",
        }:
            raise ValueError(
                "role must be 'user' or 'assistant'."
            )

        if not content or not content.strip():
            raise ValueError(
                "content cannot be empty."
            )

        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        self._conversations[conversation_id].append(
            {
                "role": role,
                "content": content.strip(),
            }
        )

    def get_history(
        self,
        conversation_id: str,
    ) -> List[dict]:
        """Return the conversation history."""

        return self._conversations.get(
            conversation_id,
            [],
        )

    def get_recent_history(
        self,
        conversation_id: str,
        max_messages: int = 10,
    ) -> List[dict]:
        """Return the most recent messages."""

        if max_messages < 1:
            raise ValueError(
                "max_messages must be at least 1."
            )

        history = self.get_history(
            conversation_id
        )

        return history[-max_messages:]

    def clear(
        self,
        conversation_id: str,
    ):
        """Clear a conversation."""

        self._conversations.pop(
            conversation_id,
            None,
        )

    def clear_all(self):
        """Clear all conversations."""

        self._conversations.clear()

    def has_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        """Check whether a conversation exists."""

        return conversation_id in self._conversations

    def message_count(
        self,
        conversation_id: str,
    ) -> int:
        """Return the number of messages."""

        return len(
            self.get_history(
                conversation_id
            )
        )