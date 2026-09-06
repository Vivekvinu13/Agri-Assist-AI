from rag.retriever import retrieve
from rag.retrieval_grader import grade_retrieval


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
            "What benefits are provided under crop insurance?",
        ),
        (
            "farmer",
            "What is the weather forecast tomorrow?",
        ),
    ]

    for role, query in test_cases:

        print("\n" + "=" * 80)
        print(f"ROLE  : {role}")
        print(f"QUERY : {query}")
        print("=" * 80)

        retrieved = retrieve(
            query=query,
            role=role,
            top_k=5,
        )

        print(
            f"\nRetrieved documents: "
            f"{len(retrieved)}"
        )

        grading = grade_retrieval(
            query=query,
            retrieved_documents=retrieved,
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


if __name__ == "__main__":
    main()