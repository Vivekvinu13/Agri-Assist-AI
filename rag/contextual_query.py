import os
import json
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    "gpt-4o-mini",
)


# Words/phrases that commonly indicate that the current
# question depends on previous conversation context.
FOLLOW_UP_PATTERNS = [
    r"\bthey\b",
    r"\bthem\b",
    r"\btheir\b",
    r"\bhe\b",
    r"\bshe\b",
    r"\bhis\b",
    r"\bher\b",
    r"\bit\b",
    r"\bits\b",
    r"\bthis\b",
    r"\bthat\b",
    r"\bthese\b",
    r"\bthose\b",
    r"\babove\b",
    r"\bhow much\b",
    r"\bhow many\b",
    r"\bwhat about\b",
    r"\bwhat are its\b",
    r"\bwhat is its\b",
    r"\bhow can i\b",
    r"\bhow do i\b",
    r"\bcan i apply\b",
]


def get_llm():
    """Create the LLM used for contextual query generation."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY was not found. "
            "Check your .env file."
        )

    return ChatOpenAI(
        model=MODEL,
        temperature=0,
        api_key=api_key,
    )


def _needs_contextualization(query: str) -> bool:
    """
    Determine whether a query contains language that is
    likely to depend on previous conversation context.

    This is intentionally deterministic so that clearly
    standalone queries are not unnecessarily rewritten.
    """

    query_lower = query.lower().strip()

    for pattern in FOLLOW_UP_PATTERNS:

        if re.search(
            pattern,
            query_lower,
        ):
            return True

    return False


def contextualize_query(
    query: str,
    conversation_history: list,
):
    """
    Convert a conversational follow-up into a standalone
    query using previous conversation history.

    Clearly standalone queries are returned unchanged.

    Example:

        Previous:
        User: Who is eligible for PM-KISAN?

        Current:
        User: How much do they get?

        Result:
        How much do eligible farmer families get
        under PM-KISAN?
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    query = query.strip()

    # ---------------------------------------------------------
    # NO HISTORY
    # ---------------------------------------------------------

    if not conversation_history:

        return {
            "original_query": query,
            "contextualized_query": query,
            "was_rewritten": False,
            "reason": (
                "No conversation history available."
            ),
        }

    # ---------------------------------------------------------
    # DETERMINISTIC STANDALONE CHECK
    # ---------------------------------------------------------

    if not _needs_contextualization(query):

        return {
            "original_query": query,
            "contextualized_query": query,
            "was_rewritten": False,
            "reason": (
                "The query does not contain an obvious "
                "reference to previous conversation."
            ),
        }

    # ---------------------------------------------------------
    # BUILD CONVERSATION HISTORY
    # ---------------------------------------------------------

    history_parts = []

    for message in conversation_history:

        role = message.get(
            "role",
            "unknown",
        )

        content = message.get(
            "content",
            "",
        )

        if content and content.strip():

            history_parts.append(
                f"{role.upper()}: {content.strip()}"
            )

    history = "\n".join(history_parts)

    # ---------------------------------------------------------
    # LLM PROMPT
    # ---------------------------------------------------------

    prompt = f"""
You are the conversational query understanding component
of Agri Assist AI.

Agri Assist AI answers questions about Indian agricultural
government schemes and farmer support.

CONVERSATION HISTORY:

{history}

CURRENT USER QUERY:

{query}

The current query appears to depend on previous
conversation context.

Rewrite it into a clear, standalone question.

RULES:

1. Preserve the user's exact intent.

2. Use conversation history only to resolve references.

3. Resolve words such as:
   - they
   - them
   - their
   - it
   - this
   - that
   - above
   - how much
   - how many
   - what about

4. Do not answer the question.

5. Do not invent facts.

6. Do not introduce a different scheme or topic.

7. Keep the rewritten query concise.

8. The rewritten query must be suitable for
   agricultural RAG retrieval.

Return ONLY valid JSON:

{{
    "contextualized_query": "...",
    "was_rewritten": true,
    "reason": "short explanation"
}}
"""

    # ---------------------------------------------------------
    # CALL LLM
    # ---------------------------------------------------------

    llm = get_llm()

    response = llm.invoke(prompt)

    content = response.content.strip()

    # ---------------------------------------------------------
    # REMOVE MARKDOWN CODE FENCES
    # ---------------------------------------------------------

    if content.startswith("```"):

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    # ---------------------------------------------------------
    # PARSE JSON
    # ---------------------------------------------------------

    try:

        result = json.loads(content)

    except json.JSONDecodeError:

        return {
            "original_query": query,
            "contextualized_query": query,
            "was_rewritten": False,
            "reason": (
                "Contextualizer returned invalid JSON. "
                "The original query was preserved."
            ),
        }

    # ---------------------------------------------------------
    # EXTRACT RESULT
    # ---------------------------------------------------------

    contextualized_query = result.get(
        "contextualized_query",
        query,
    )

    if not isinstance(
        contextualized_query,
        str,
    ):
        contextualized_query = query

    contextualized_query = (
        contextualized_query.strip()
    )

    # ---------------------------------------------------------
    # SAFETY FALLBACK
    # ---------------------------------------------------------

    if not contextualized_query:

        contextualized_query = query

    was_rewritten = bool(
        result.get(
            "was_rewritten",
            False,
        )
    )

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    return {
        "original_query": query,
        "contextualized_query": contextualized_query,
        "was_rewritten": was_rewritten,
        "reason": result.get(
            "reason",
            "No reason provided.",
        ),
    }