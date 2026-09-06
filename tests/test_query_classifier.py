from rag.query_classifier import classify_query


def main():

    test_cases = [
        "Who is eligible for PM-KISAN?",
        "What assistance is available for micro irrigation?",
        "What is the weather forecast tomorrow?",
        "How can I apply for crop insurance?",
        "What is the capital of France?",
        "Tell me a joke.",
    ]

    for query in test_cases:

        print("\n" + "=" * 80)
        print("QUERY CLASSIFIER TEST")
        print("=" * 80)

        print(f"Query: {query}")

        try:

            result = classify_query(query)

            print(
                f"\nDomain         : "
                f"{result['domain']}"
            )

            print(
                f"Intent         : "
                f"{result['intent']}"
            )

            print(
                f"Confidence     : "
                f"{result['confidence']}"
            )

            print(
                f"Should retrieve: "
                f"{result['should_retrieve']}"
            )

            print(
                f"Reason         : "
                f"{result['reason']}"
            )

        except Exception as e:

            print("\nERROR")
            print(e)


if __name__ == "__main__":
    main()