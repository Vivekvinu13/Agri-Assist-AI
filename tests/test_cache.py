from rag.cache import (
    make_cache_key,
    set_cached_response,
    get_cached_response,
    delete_cached_response,
    cache_exists,
    clear_cache,
)


def main():
    clear_cache()

    query = "Who is eligible for PM-KISAN?"

    cache_key = make_cache_key(
        query=query,
        role="farmer",
        conversation_id="test",
    )

    test_response = {
        "answer": "Eligible farmer families can receive ₹6,000 per year.",
        "grounded": True,
        "sources": ["chunk_0051", "chunk_0056"],
    }

    print("Cache key:")
    print(cache_key)

    print("\nBefore storing:")
    print(get_cached_response(cache_key))

    set_cached_response(
        cache_key,
        test_response,
        ttl=3600,
    )

    print("\nAfter storing:")
    print(get_cached_response(cache_key))

    print("\nCache exists:")
    print(cache_exists(cache_key))

    delete_cached_response(cache_key)

    print("\nAfter deletion:")
    print(get_cached_response(cache_key))

    print("\nCache exists after deletion:")
    print(cache_exists(cache_key))


if __name__ == "__main__":
    main()