import json
import os

import redis
from dotenv import load_dotenv


load_dotenv()


REDIS_HOST = os.getenv(
    "REDIS_HOST",
    "localhost",
)

REDIS_PORT = int(
    os.getenv(
        "REDIS_PORT",
        "6379",
    )
)

REDIS_DB = int(
    os.getenv(
        "REDIS_DB",
        "0",
    )
)

DEFAULT_TTL = int(
    os.getenv(
        "REDIS_CACHE_TTL",
        "3600",
    )
)


def get_redis_client():
    """Create and return a Redis client."""

    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )

    client.ping()

    return client


def make_cache_key(
    query: str,
    role: str = "farmer",
    conversation_id: str = "default",
    scheme_id: str | None = None,
) -> str:
    """
    Create a deterministic cache key.

    The selected scheme is part of the key so that
    scheme-specific answers never collide with broad
    all-scheme answers.
    """

    query = query.strip()
    role = role.strip().lower()
    conversation_id = conversation_id.strip()

    scheme_part = (
        scheme_id.strip()
        if scheme_id
        else "all_schemes"
    )

    return (
        f"rag:{role}:"
        f"{conversation_id}:"
        f"{scheme_part}:"
        f"{query}"
    )


def get_cached_response(cache_key: str):
    """Return cached response, or None if not found."""

    client = get_redis_client()

    cached = client.get(cache_key)

    if cached is None:
        return None

    return json.loads(cached)


def set_cached_response(
    cache_key: str,
    response: dict,
    ttl: int = DEFAULT_TTL,
):
    """Store a RAG response in Redis."""

    client = get_redis_client()

    client.setex(
        cache_key,
        ttl,
        json.dumps(response),
    )


def delete_cached_response(cache_key: str):
    """Delete one cached response."""

    client = get_redis_client()

    client.delete(cache_key)


def clear_cache():
    """Clear the Redis database used by the application."""

    client = get_redis_client()

    client.flushdb()


def cache_exists(cache_key: str) -> bool:
    """Check whether a cache key exists."""

    client = get_redis_client()

    return bool(
        client.exists(cache_key)
    )