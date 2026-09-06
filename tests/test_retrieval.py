from rag.retriever import retrieve


def print_results(role, query, results):
    print("\n" + "=" * 80)
    print(f"ROLE   : {role}")
    print(f"QUERY  : {query}")
    print(f"RESULTS: {len(results)}")
    print("=" * 80)

    for i, result in enumerate(results, start=1):

        document = result["document"]
        score = result["score"]
        metadata = result["metadata"]

        print(f"\n--- RESULT {i} ---")
        print(f"Score       : {score:.4f}")
        print(
            f"Scheme      : "
            f"{metadata.get('scheme_name', 'N/A')}"
        )
        print(
            f"Scheme ID   : "
            f"{metadata.get('scheme_id', 'N/A')}"
        )
        print(
            f"Source      : "
            f"{metadata.get('source_type', 'N/A')}"
        )
        print(
            f"Source File : "
            f"{metadata.get('source_file', 'N/A')}"
        )
        print(
            f"Page        : "
            f"{metadata.get('page', 'N/A')}"
        )
        print(
            f"Topic       : "
            f"{metadata.get('topic', 'N/A')}"
        )

        print("\nText:")
        print(document.page_content[:1200])


def main():

    test_cases = [
        (
            "farmer",
            "Who is eligible for PM-KISAN?"
        ),
        (
            "farmer",
            "What benefits are provided under crop insurance?"
        ),
        (
            "farmer",
            "What is Kisan Credit Card and who can use it?"
        ),
        (
            "public",
            "What government schemes are available for farmers?"
        ),
        (
            "government",
            "What are the eligibility conditions for PM-KISAN?"
        ),
        (
            "agency",
            "What assistance is available for micro irrigation?"
        ),
    ]

    for role, query in test_cases:

        try:
            results = retrieve(
                query=query,
                role=role,
                top_k=5,
            )

            print_results(
                role,
                query,
                results,
            )

        except Exception as e:
            print("\nERROR")
            print(f"Role  : {role}")
            print(f"Query : {query}")
            print(f"Error : {e}")


if __name__ == "__main__":
    main()