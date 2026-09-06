from rag.pipeline import (
    run_rag_pipeline,
    conversation_memory,
)


def print_result(turn, trace):

    print("\n" + "=" * 80)
    print(f"CONVERSATION PIPELINE - TURN {turn}")
    print("=" * 80)

    print(
        f"Original query       : "
        f"{trace['original_query']}"
    )

    print(
        f"Contextualized query : "
        f"{trace['contextualized_query']}"
    )

    print(
        f"Was rewritten        : "
        f"{trace['contextualization']['was_rewritten']}"
    )

    classification = trace["classification"]

    print(
        f"Domain               : "
        f"{classification.get('domain')}"
    )

    print(
        f"Intent               : "
        f"{classification.get('intent')}"
    )

    print(
        f"Initial documents    : "
        f"{len(trace['initial_retrieval'])}"
    )

    if trace["initial_grading"]:

        print(
            f"Initial relevant     : "
            f"{trace['initial_grading'].get('relevant')}"
        )

        print(
            f"Initial confidence   : "
            f"{trace['initial_grading'].get('confidence')}"
        )

    print(
        f"Correction triggered: "
        f"{trace['correction_triggered']}"
    )

    print(
        f"Final query          : "
        f"{trace['final_query']}"
    )

    print(
        f"Status               : "
        f"{trace['status']}"
    )

    print("\nANSWER")
    print("-" * 80)

    print(trace["answer"])

    print("\nGROUNDED")
    print("-" * 80)

    print(trace["grounded"])

    print("\nSOURCES")
    print("-" * 80)

    for source in trace["sources"]:

        print(
            f"- {source['scheme_id']} | "
            f"{source['source_type']} | "
            f"Page {source['page']} | "
            f"{source['chunk_id']}"
        )


def main():

    conversation_id = "farmer_demo_001"

    # -------------------------------------------------
    # TURN 1
    # -------------------------------------------------

    query_1 = "Who is eligible for PM-KISAN?"

    trace_1 = run_rag_pipeline(
        query=query_1,
        role="farmer",
        conversation_id=conversation_id,
        top_k=5,
        min_confidence=0.65,
        max_retries=1,
    )

    print_result(
        turn=1,
        trace=trace_1,
    )

    # -------------------------------------------------
    # TURN 2
    # -------------------------------------------------

    query_2 = "How much do they get?"

    trace_2 = run_rag_pipeline(
        query=query_2,
        role="farmer",
        conversation_id=conversation_id,
        top_k=5,
        min_confidence=0.65,
        max_retries=1,
    )

    print_result(
        turn=2,
        trace=trace_2,
    )

    # -------------------------------------------------
    # MEMORY
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("FINAL CONVERSATION MEMORY")
    print("=" * 80)

    history = conversation_memory.get_history(
        conversation_id
    )

    for message in history:

        print(
            f"{message['role'].upper()}: "
            f"{message['content']}"
        )

    print("\nMessage count:")
    print(
        conversation_memory.message_count(
            conversation_id
        )
    )


if __name__ == "__main__":
    main()