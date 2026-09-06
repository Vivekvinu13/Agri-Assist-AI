from rag.conversation_memory import ConversationMemory


def main():

    memory = ConversationMemory()

    conversation_id = "test_farmer_001"

    # -------------------------------------------------
    # ADD FIRST EXCHANGE
    # -------------------------------------------------

    memory.add_message(
        conversation_id=conversation_id,
        role="user",
        content="Who is eligible for PM-KISAN?",
    )

    memory.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=(
            "PM-KISAN provides support to eligible "
            "landholding farmer families, subject to "
            "the scheme's exclusions."
        ),
    )

    # -------------------------------------------------
    # ADD SECOND USER MESSAGE
    # -------------------------------------------------

    memory.add_message(
        conversation_id=conversation_id,
        role="user",
        content="How much do they get?",
    )

    # -------------------------------------------------
    # PRINT FULL HISTORY
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("CONVERSATION MEMORY TEST")
    print("=" * 80)

    print(
        f"Conversation ID: "
        f"{conversation_id}"
    )

    print(
        f"Message count: "
        f"{memory.message_count(conversation_id)}"
    )

    print("\nFULL HISTORY")
    print("-" * 80)

    for message in memory.get_history(
        conversation_id
    ):

        print(
            f"{message['role'].upper()}: "
            f"{message['content']}"
        )

    # -------------------------------------------------
    # RECENT HISTORY
    # -------------------------------------------------

    print("\nRECENT HISTORY")
    print("-" * 80)

    recent = memory.get_recent_history(
        conversation_id,
        max_messages=2,
    )

    for message in recent:

        print(
            f"{message['role'].upper()}: "
            f"{message['content']}"
        )

    # -------------------------------------------------
    # CHECK CONVERSATION
    # -------------------------------------------------

    print("\nCONVERSATION EXISTS")
    print("-" * 80)

    print(
        memory.has_conversation(
            conversation_id
        )
    )

    # -------------------------------------------------
    # CLEAR CONVERSATION
    # -------------------------------------------------

    memory.clear(conversation_id)

    print("\nAFTER CLEAR")
    print("-" * 80)

    print(
        f"Message count: "
        f"{memory.message_count(conversation_id)}"
    )

    print(
        f"Conversation exists: "
        f"{memory.has_conversation(conversation_id)}"
    )


if __name__ == "__main__":
    main()