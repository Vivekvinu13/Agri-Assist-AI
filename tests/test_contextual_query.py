from rag.conversation_memory import ConversationMemory
from rag.contextual_query import contextualize_query


def main():

    memory = ConversationMemory()

    conversation_id = "test_farmer_001"

    # -------------------------------------------------
    # FIRST EXCHANGE
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
    # FOLLOW-UP QUESTION
    # -------------------------------------------------

    follow_up_query = "How much do they get?"

    history = memory.get_recent_history(
        conversation_id,
        max_messages=10,
    )

    result = contextualize_query(
        query=follow_up_query,
        conversation_history=history,
    )

    # -------------------------------------------------
    # PRINT RESULT
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("CONTEXTUAL QUERY TEST")
    print("=" * 80)

    print(
        f"Original query:\n"
        f"{result['original_query']}"
    )

    print(
        f"\nContextualized query:\n"
        f"{result['contextualized_query']}"
    )

    print(
        f"\nWas rewritten:\n"
        f"{result['was_rewritten']}"
    )

    print(
        f"\nReason:\n"
        f"{result['reason']}"
    )

    # -------------------------------------------------
    # SECOND TEST
    # -------------------------------------------------

    standalone_query = (
        "What assistance is available for micro irrigation?"
    )

    result_2 = contextualize_query(
        query=standalone_query,
        conversation_history=history,
    )

    print("\n" + "=" * 80)
    print("STANDALONE QUERY TEST")
    print("=" * 80)

    print(
        f"Original query:\n"
        f"{result_2['original_query']}"
    )

    print(
        f"\nContextualized query:\n"
        f"{result_2['contextualized_query']}"
    )

    print(
        f"\nWas rewritten:\n"
        f"{result_2['was_rewritten']}"
    )

    print(
        f"\nReason:\n"
        f"{result_2['reason']}"
    )


if __name__ == "__main__":
    main()