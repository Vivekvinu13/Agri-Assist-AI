from rag.retriever import retrieve
from rag.retrieval_grader import grade_retrieval
from rag.answer_generator import generate_answer


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
        print("ANSWER GENERATOR TEST")
        print("=" * 80)

        print(f"Role  : {role}")
        print(f"Query : {query}")

        # -------------------------------------------------
        # RETRIEVAL
        # -------------------------------------------------

        results = retrieve(
            query=query,
            role=role,
            top_k=5,
        )

        print(
            f"\nRetrieved documents: "
            f"{len(results)}"
        )

        # -------------------------------------------------
        # RETRIEVAL GRADING
        # -------------------------------------------------

        grading = grade_retrieval(
            query=query,
            retrieved_documents=results,
        )

        print("\nRETRIEVAL GRADING")
        print("-" * 80)

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

        # -------------------------------------------------
        # ANSWER GENERATION
        # -------------------------------------------------

        result = generate_answer(
            query=query,
            retrieved_documents=results,
            grading_result=grading,
        )

        print("\nGENERATED ANSWER")
        print("-" * 80)

        print(result["answer"])

        # -------------------------------------------------
        # GROUNDING
        # -------------------------------------------------

        print("\nGROUNDED")
        print("-" * 80)

        print(result["grounded"])

        # -------------------------------------------------
        # PROVENANCE
        # -------------------------------------------------

        print(
            f"\nSources used: "
            f"{len(result['sources'])}"
        )

        print("\nSOURCES")
        print("-" * 80)

        if not result["sources"]:
            print("No sources used.")

        else:

            for source in result["sources"]:

                print(
                    f"- {source['scheme_id']} | "
                    f"{source['source_type']} | "
                    f"{source['source_file']} | "
                    f"Page {source['page']} | "
                    f"{source['chunk_id']}"
                )


if __name__ == "__main__":
    main()