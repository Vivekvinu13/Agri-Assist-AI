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
    """Create the LLM used to grade retrieved evidence."""

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


def grade_retrieval(
    query: str,
    retrieved_documents: list,
):
    """
    Evaluate whether retrieved documents contain
    enough relevant information to answer a query.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not retrieved_documents:
        return {
            "relevant": False,
            "confidence": 0.0,
            "reason": "No documents were retrieved.",
            "relevant_chunks": [],
        }

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

Chunk ID:
{result.get("chunk_id", "N/A")}

Scheme:
{metadata.get("scheme_id", "N/A")}

Source:
{metadata.get("source_type", "N/A")}

Page:
{metadata.get("page", "N/A")}

Content:
{document.page_content}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a retrieval quality evaluator for an agricultural
government-scheme RAG system called Agri Assist AI.

USER QUESTION:
{query}

RETRIEVED DOCUMENTS:
{context}

Evaluate whether the retrieved documents contain enough
relevant information to answer the user's question.

Rules:

1. Mark relevant=true only if at least one retrieved
   document contains information directly useful for
   answering the question.

2. Judge only the relevance of the retrieved evidence.
   Do not add outside knowledge.

3. If the documents are unrelated to the question,
   mark relevant=false.

4. If the documents contain only partial information,
   you may mark relevant=true with lower confidence.

5. Identify which retrieved chunks are useful.

Return ONLY valid JSON:

{{
    "relevant": true,
    "confidence": 0.0,
    "reason": "short explanation",
    "relevant_chunks": ["chunk_id_1", "chunk_id_2"]
}}

Confidence must be between 0 and 1.
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
            "relevant": False,
            "confidence": 0.0,
            "reason": (
                "Retrieval grader returned invalid JSON."
            ),
            "relevant_chunks": [],
        }

    return result