from rag.corrective_rag import corrective_retrieve


def print_grading(label, grading):
    print(f"\n{label}")
    print("-" * 80)

    if grading is None:
        print("No grading result.")
        return

    print(
        f"Relevant   : "
        f"{grading.get('relevant')}"
    )

    print(
        f"Confidence : "
        f"{grading.get('confidence')}"
    )

    print(
        f"Reason     : "
        f"{grading.get('reason')}"
    )

    print(
        f"Useful chunks: "
        f"{grading.get('relevant_chunks')}"
    )


def main():

    test_cases = [
        (
            "farmer",
            "Who is eligible for PM-KISAN?",
        ),
        (
            "farmer",
            "What assistance is available for micro irrigation?",
        ),
        (
            "farmer",
            "What is the weather forecast tomorrow?",
        ),
    ]

    for role, query in test_cases:

        print("\n" + "=" * 80)
        print("CORRECTIVE RAG TEST")
        print("=" * 80)

        print(f"Role  : {role}")
        print(f"Query : {query}")

        try:

            trace = corrective_retrieve(
                query=query,
                role=role,
                top_k=5,
                min_confidence=0.65,
                max_retries=1,
            )

            classification = trace["classification"]

            print("\nQUERY CLASSIFICATION")
            print("-" * 80)

            print(
                f"Domain         : "
                f"{classification.get('domain')}"
            )

            print(
                f"Intent         : "
                f"{classification.get('intent')}"
            )

            print(
                f"Confidence     : "
                f"{classification.get('confidence')}"
            )

            print(
                f"Should retrieve: "
                f"{classification.get('should_retrieve')}"
            )

            print(
                f"Reason         : "
                f"{classification.get('reason')}"
            )

            print(
                f"\nInitial documents: "
                f"{len(trace['initial_retrieval'])}"
            )

            print_grading(
                "INITIAL GRADING",
                trace["initial_grading"],
            )

            print(
                f"\nCorrection triggered: "
                f"{trace['correction_triggered']}"
            )

            if trace["rewritten_query"]:

                print(
                    f"Rewritten query: "
                    f"{trace['rewritten_query']}"
                )

            if trace["retry_retrieval"]:

                print(
                    f"\nRetry documents: "
                    f"{len(trace['retry_retrieval'])}"
                )

                print_grading(
                    "RETRY GRADING",
                    trace["retry_grading"],
                )

            print("\nFINAL RESULT")
            print("-" * 80)

            print(
                f"Final query : "
                f"{trace['final_query']}"
            )

            print(
                f"Status      : "
                f"{trace['status']}"
            )

            print(
                f"Final docs  : "
                f"{len(trace['final_documents'])}"
            )

        except Exception as e:

            print("\nERROR")
            print(e)


if __name__ == "__main__":
    main()