from rag.pipeline import run_rag_pipeline


def main():
    print("=" * 80)
    print("PROVENANCE TEST")
    print("=" * 80)

    query = "Who is eligible for PM-KISAN?"

    trace = run_rag_pipeline(
        query=query,
        role="farmer",
        conversation_id="provenance_test",
    )

    print("\nANSWER")
    print("-" * 80)
    print(trace["answer"])

    print("\nGROUNDED")
    print("-" * 80)
    print(trace["grounded"])

    print("\nPROVENANCE / SOURCES")
    print("-" * 80)

    sources = trace.get("sources", [])

    if not sources:
        print("No sources returned.")
        return

    for index, source in enumerate(sources, start=1):
        print(f"\nSource {index}")

        if isinstance(source, dict):
            for key, value in source.items():
                print(f"{key:15}: {value}")
        else:
            print(source)

    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    print(f"Sources returned : {len(sources)}")
    print(f"Grounded         : {trace['grounded']}")

    required_fields = [
        "scheme_id",
        "source_type",
        "page",
        "chunk_id",
    ]

    valid_sources = True

    for source in sources:
        if not isinstance(source, dict):
            valid_sources = False
            break

        for field in required_fields:
            if field not in source:
                print(
                    f"Missing field '{field}' "
                    f"in source: {source}"
                )
                valid_sources = False

    if trace["grounded"] and sources and valid_sources:
        print("\nSUCCESS: Provenance information is valid!")
    else:
        print("\nFAILED: Provenance information needs investigation.")


if __name__ == "__main__":
    main()