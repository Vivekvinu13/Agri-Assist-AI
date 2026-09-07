import re


PROMPT_INJECTION_PATTERNS = [
    r"ignore (all|any|the) previous instructions",
    r"ignore your instructions",
    r"reveal (the )?(system|developer) prompt",
    r"show me your prompt",
    r"disregard the instructions",
    r"override your instructions",
]


def validate_input(query: str) -> tuple[bool, str]:
    """
    Validate the user's input before it enters the RAG pipeline.
    Returns:
        (True, "") when allowed
        (False, message) when blocked
    """

    if not isinstance(query, str):
        return False, "Please enter your question as text."

    query = query.strip()

    if not query:
        return False, "Please enter a question."

    if len(query) > 1000:
        return (
            False,
            "Your question is too long. Please keep it under 1000 characters.",
        )

    lowered = query.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return (
                False,
                "I can help with agriculture-related questions, "
                "but I cannot follow requests to override my instructions.",
            )

    return True, ""