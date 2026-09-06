from rag.cache import clear_cache
from rag.pipeline import run_rag_pipeline


def print_result(label, trace):
    print("\n" + "=" * 80)
    print(label)
    print("=" * 80)

    print(f"Query        : {trace['original_query']}")
    print(f"Cache hit    : {trace['cache']['hit']}")
    print(f"Status       : {trace['status']}")
    print(f"Grounded     : {trace['grounded']}")

    if not trace["cache"]["hit"]:
        print(
            f"Initial docs : "
            f"{len(trace['initial_retrieval'])}"
        )

    print("\nANSWER")
    print("-" * 80)
    print(trace["answer"])

    print("\nSOURCES")
    print("-" * 80)

    for source in trace.get("sources", []):
        print(
            f"- {source.get('scheme_id', 'N/A')} | "
            f"{source.get('source_type', 'N/A')} | "
            f"Page {source.get('page', 'N/A')} | "
            f"{source.get('chunk_id', 'N/A')}"
        )


def main():
    # ---------------------------------------------------------
    # 1. Start with a clean Redis cache
    # ---------------------------------------------------------
    print("=" * 80)
    print("PIPELINE REDIS CACHE TEST")
    print("=" * 80)

    print("\nClearing Redis cache...")
    clear_cache()
    print("Redis cache cleared.")

    query = "Who is eligible for PM-KISAN?"

    # ---------------------------------------------------------
    # 2. First request
    # ---------------------------------------------------------
    trace_1 = run_rag_pipeline(
        query=query,
        role="farmer",
        conversation_id="cache_test",
    )

    print_result(
        "FIRST REQUEST - EXPECT CACHE MISS",
        trace_1,
    )

    # ---------------------------------------------------------
    # 3. Second identical request
    # ---------------------------------------------------------
    trace_2 = run_rag_pipeline(
        query=query,
        role="farmer",
        conversation_id="cache_test",
    )

    print_result(
        "SECOND REQUEST - EXPECT CACHE HIT",
        trace_2,
    )

    # ---------------------------------------------------------
    # 4. Validate results
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    first_request_is_miss = (
        trace_1["cache"]["hit"] is False
    )

    second_request_is_hit = (
        trace_2["cache"]["hit"] is True
    )

    first_request_grounded = (
        trace_1["grounded"] is True
    )

    second_request_grounded = (
        trace_2["grounded"] is True
    )

    print(
        f"First request cache miss : "
        f"{first_request_is_miss}"
    )

    print(
        f"Second request cache hit  : "
        f"{second_request_is_hit}"
    )

    print(
        f"First answer grounded     : "
        f"{first_request_grounded}"
    )

    print(
        f"Cached answer grounded    : "
        f"{second_request_grounded}"
    )

    # ---------------------------------------------------------
    # 5. Final result
    # ---------------------------------------------------------
    if (
        first_request_is_miss
        and second_request_is_hit
        and first_request_grounded
        and second_request_grounded
    ):
        print("\nSUCCESS: Redis pipeline caching works!")
    else:
        print("\nFAILED: Redis pipeline caching needs investigation.")


if __name__ == "__main__":
    main()