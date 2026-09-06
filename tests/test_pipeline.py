from rag.pipeline import run_rag_pipeline


def print_sources(sources):

    if not sources:
        print("No sources.")

        return

    for source in sources:

        print(
            f"- {source['scheme_id']} | "
            f"{source['source_type']} | "
            f"{source['source_file']} | "
            f"Page {source['page']} | "
            f"{source['chunk_id']}"
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
        (
            "farmer",
            "Tell me about help for water.",
        ),
    ]

    for role, query in test_cases:

        print("\n" + "=" * 80)
        print("FULL RAG PIPELINE TEST")
        print("=" * 80)

        print(f"Role  : {role}")
        print(f"Query : {query}")

        try:

            trace = run_rag_pipeline(
                query=query,
                role=role,
                top_k=5,
                min_confidence=0.65,
                max_retries=1,
            )

            # -------------------------------------------------
            # CLASSIFICATION
            # -------------------------------------------------

            classification = trace[
                "classification"
            ]

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

            # -------------------------------------------------
            # INITIAL RETRIEVAL
            # -------------------------------------------------

            print("\nINITIAL RETRIEVAL")
            print("-" * 80)

            print(
                f"Documents: "
                f"{len(trace['initial_retrieval'])}"
            )

            # -------------------------------------------------
            # INITIAL GRADING
            # -------------------------------------------------

            print("\nINITIAL GRADING")
            print("-" * 80)

            initial_grading = trace[
                "initial_grading"
            ]

            if initial_grading:

                print(
                    f"Relevant   : "
                    f"{initial_grading.get('relevant')}"
                )

                print(
                    f"Confidence : "
                    f"{initial_grading.get('confidence')}"
                )

                print(
                    f"Useful chunks: "
                    f"{initial_grading.get('relevant_chunks')}"
                )

            else:

                print("No grading performed.")

            # -------------------------------------------------
            # CORRECTION
            # -------------------------------------------------

            print("\nCORRECTIVE RAG")
            print("-" * 80)

            print(
                f"Triggered: "
                f"{trace['correction_triggered']}"
            )

            if trace["rewritten_query"]:

                print(
                    f"Rewritten query: "
                    f"{trace['rewritten_query']}"
                )

            print(
                f"Retry documents: "
                f"{len(trace['retry_retrieval'])}"
            )

            # -------------------------------------------------
            # FINAL
            # -------------------------------------------------

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

            # -------------------------------------------------
            # ANSWER
            # -------------------------------------------------

            print("\nGENERATED ANSWER")
            print("-" * 80)

            print(trace["answer"])

            # -------------------------------------------------
            # GROUNDING
            # -------------------------------------------------

            print("\nGROUNDED")
            print("-" * 80)

            print(trace["grounded"])

            # -------------------------------------------------
            # SOURCES
            # -------------------------------------------------

            print("\nPROVENANCE")
            print("-" * 80)

            print(
                f"Sources used: "
                f"{len(trace['sources'])}"
            )

            print_sources(
                trace["sources"]
            )

        except Exception as e:

            print("\nERROR")
            print("-" * 80)
            print(e)


if __name__ == "__main__":
    main()