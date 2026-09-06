import os
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    "gpt-4o-mini",
)


def get_llm():
    """Create the LLM used for query rewriting."""

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


def rewrite_query(
    original_query: str,
    retrieved_documents: list,
    grading_result: dict,
):
    """
    Rewrite a weak retrieval query using the evidence
    returned by the first retrieval attempt.
    """

    if not original_query.strip():
        raise ValueError("Original query cannot be empty.")

    reason = grading_result.get(
        "reason",
        "Retrieved evidence was insufficient.",
    )

    context_parts = []

    for i, result in enumerate(
        retrieved_documents,
        start=1,
    ):
        document = result["document"]
        metadata = result["metadata"]

        context_parts.append(
            f"""
DOCUMENT {i}

Scheme:
{metadata.get("scheme_id", "N/A")}

Topic:
{metadata.get("topic", "N/A")}

Content:
{document.page_content}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are the query correction component of Agri Assist AI,
a RAG system for Indian agricultural government schemes.

The original user question was:

{original_query}

The first retrieval attempt was judged weak.

Retrieval grader reason:

{reason}

Retrieved evidence:

{context}

Rewrite the user's question so that it is more likely to
retrieve the correct agricultural government-scheme
information.

Rules:

1. Preserve the user's original intent.
2. Do not invent facts.
3. Do not answer the question.
4. Add useful terminology only when supported by the
   original question or retrieved evidence.
5. Keep the rewritten query concise.
6. The query should remain a natural search question.

Return ONLY valid JSON:

{{
    "rewritten_query": "..."
}}
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    content = response.content.strip()

    if content.startswith("```"):
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        result = json.loads(content)

    except json.JSONDecodeError:

        return {
            "rewritten_query": original_query,
        }

    rewritten_query = result.get(
        "rewritten_query",
        original_query,
    )

    if not rewritten_query.strip():
        rewritten_query = original_query

    return {
        "rewritten_query": rewritten_query.strip(),
    }