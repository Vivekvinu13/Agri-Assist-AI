from rag.retriever import retrieve
from rag.retrieval_grader import grade_retrieval
from rag.query_rewriter import rewrite_query


def main():

    role = "farmer"

    query = "Tell me about help for water."

    print("=" * 80)
    print("QUERY REWRITER TEST")
    print("=" * 80)

    print(f"\nOriginal query:")
    print(query)

    # -----------------------------------------------------
    # First retrieval
    # -----------------------------------------------------

    retrieved = retrieve(
        query=query,
        role=role,
        top_k=5,
    )

    print(
        f"\nInitial documents retrieved: "
        f"{len(retrieved)}"
    )

    # -----------------------------------------------------
    # Grade retrieval
    # -----------------------------------------------------

    grading = grade_retrieval(
        query=query,
        retrieved_documents=retrieved,
    )

    print("\nInitial retrieval grading:")
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

    # -----------------------------------------------------
    # Rewrite
    # -----------------------------------------------------

    rewritten = rewrite_query(
        original_query=query,
        retrieved_documents=retrieved,
        grading_result=grading,
    )

    print("\nRewritten query:")
    print(
        rewritten.get(
            "rewritten_query",
            query,
        )
    )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()