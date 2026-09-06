import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    "gpt-4o-mini",
)


# =========================================================
# ROLE-SPECIFIC INSTRUCTIONS
# =========================================================

ROLE_INSTRUCTIONS = {
    "farmer": """
You are answering a farmer.

Use simple, clear and practical language.

Prioritize:
- Eligibility
- Benefits
- Financial assistance
- Subsidies
- Insurance
- Credit
- Irrigation support
- Application-related guidance

Avoid technical government terminology when simpler
language is possible.

Explain the information in a way that is easy for a
farmer to understand.
""",

    "public": """
You are answering a member of the public.

Provide clear general information about agriculture
government schemes.

Prioritize:
- What the scheme is
- Who can benefit
- Main benefits
- Financial assistance
- Basic access or application information

Use clear language and avoid unnecessary technical detail.
""",

    "government": """
You are answering a government user.

Provide a more structured and administrative explanation.

Prioritize:
- Scheme provisions
- Eligibility categories
- Beneficiary categories
- Financial assistance
- Implementation-related information
- Important scheme conditions

Use precise terminology from the retrieved evidence.

Do not invent implementation details that are not present
in the evidence.
""",

    "agency": """
You are answering an agriculture-support agency or
organization.

Provide practical information that can help the agency
understand and support farmers.

Prioritize:
- Scheme eligibility
- Farmer benefits
- Financial assistance
- Scheme provisions
- Assistance available to farmers
- Relevant application or access information

Use clear but professional language.

Do not invent operational procedures.
""",
}


# =========================================================
# LLM
# =========================================================

def get_llm():
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


# =========================================================
# CONTEXT BUILDER
# =========================================================

def build_context(retrieved_documents):
    """
    Build grounded context using only the useful
    retrieved chunks.
    """

    context_parts = []

    for index, item in enumerate(
        retrieved_documents,
        start=1,
    ):
        document = item["document"]
        metadata = document.metadata

        chunk_id = metadata.get(
            "chunk_id",
            metadata.get("id", "N/A"),
        )

        scheme_id = metadata.get(
            "scheme_id",
            "N/A",
        )

        source_type = metadata.get(
            "source_type",
            "N/A",
        )

        source_file = metadata.get(
            "source_file",
            "",
        )

        page = metadata.get(
            "page",
            None,
        )

        content = document.page_content.strip()

        context_parts.append(
            f"""
SOURCE {index}
Chunk ID: {chunk_id}
Scheme ID: {scheme_id}
Source type: {source_type}
Source file: {source_file}
Page: {page}

CONTENT:
{content}
"""
        )

    return "\n".join(context_parts)


# =========================================================
# PROVENANCE BUILDER
# =========================================================

def build_sources(retrieved_documents):
    """
    Build provenance information only from chunks that
    were actually used to generate the answer.
    """

    sources = []

    for item in retrieved_documents:

        metadata = item["document"].metadata

        sources.append(
            {
                "chunk_id": metadata.get(
                    "chunk_id",
                    metadata.get("id", "N/A"),
                ),

                "scheme_id": metadata.get(
                    "scheme_id",
                    "",
                ),

                "scheme_name": metadata.get(
                    "scheme_name",
                    "",
                ),

                "source_type": metadata.get(
                    "source_type",
                    "",
                ),

                "source_file": metadata.get(
                    "source_file",
                    "",
                ),

                "page": metadata.get(
                    "page",
                    None,
                ),
            }
        )

    return sources


# =========================================================
# ANSWER GENERATION
# =========================================================

def generate_answer(
    query: str,
    retrieved_documents: list,
    grading_result: dict,
    role: str = "farmer",
):
    """
    Generate a strictly grounded answer.

    The role changes how the answer is presented,
    but never changes the facts available to the model.
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    # -----------------------------------------------------
    # No retrieved documents
    # -----------------------------------------------------

    if not retrieved_documents:

        return {
            "answer": (
                "I could not find enough reliable "
                "information to answer this question."
            ),
            "grounded": False,
            "sources": [],
        }

    role = role.lower().strip()

    if role not in ROLE_INSTRUCTIONS:
        role = "farmer"

    # =====================================================
    # READ RETRIEVAL GRADING
    # =====================================================

    relevant = grading_result.get(
        "relevant",
        False,
    )

    confidence = grading_result.get(
        "confidence",
        0.0,
    )

    relevant_chunks = grading_result.get(
        "relevant_chunks",
        [],
    )

    # =====================================================
    # IMPORTANT GROUNDING CHECK
    # =====================================================

    # If the grader says the retrieval is not relevant,
    # NEVER generate an answer from the retrieved documents.

    if not relevant:

        return {
            "answer": (
                "I could not find enough reliable "
                "information to answer this question."
            ),
            "grounded": False,
            "sources": [],
        }

    # =====================================================
    # FIND USEFUL CHUNKS
    # =====================================================

    useful_documents = []

    relevant_ids = set()

    for chunk in relevant_chunks:

        if isinstance(chunk, str):

            relevant_ids.add(chunk)

        elif isinstance(chunk, dict):

            chunk_id = chunk.get(
                "chunk_id"
            )

            if chunk_id:
                relevant_ids.add(
                    chunk_id
                )

    # -----------------------------------------------------
    # Match graded chunks against retrieved documents
    # -----------------------------------------------------

    for item in retrieved_documents:

        chunk_id = item.get(
            "chunk_id"
        )

        if chunk_id in relevant_ids:

            useful_documents.append(item)

    # =====================================================
    # SAFETY CHECK
    # =====================================================

    # If grading says relevant but did not identify
    # any specific useful chunks, do not blindly use
    # all retrieved documents.

    if not useful_documents:

        return {
            "answer": (
                "I could not find enough reliable "
                "information to answer this question."
            ),
            "grounded": False,
            "sources": [],
        }

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context = build_context(
        useful_documents
    )

    # =====================================================
    # ROLE INSTRUCTIONS
    # =====================================================

    role_instruction = ROLE_INSTRUCTIONS[
        role
    ]

    # =====================================================
    # GROUNDED PROMPT
    # =====================================================

    prompt = f"""
You are Agri Assist AI, an agriculture government
scheme assistant.

Your answer MUST be grounded ONLY in the evidence
provided below.

Do not use outside knowledge.

Do not invent:
- eligibility rules
- subsidy amounts
- application procedures
- dates
- benefits
- government requirements
- scheme conditions

If the evidence does not contain enough information
to answer the question, say that the available
information is insufficient.

{role_instruction}

USER QUESTION:
{query}

RETRIEVED EVIDENCE:
{context}

ANSWERING RULES:

1. Answer the user's question directly.

2. Use simple and natural language.

3. Do not mention:
   - vector databases
   - FAISS
   - embeddings
   - retrieval
   - chunks
   - grading
   - RAG
   - internal system processes

4. Do not expose technical source metadata.

5. Do not make claims that are not supported by
   the retrieved evidence.

6. If important eligibility exclusions or conditions
   are present in the evidence, mention them when
   relevant.

7. If the user asks about an amount, clearly state
   the amount and payment structure if available.

8. Keep the response reasonably concise.

9. Do not start with:
   "According to the retrieved documents..."

10. Do not add a sources section.

11. Do not tell the user that they can apply unless
    the evidence specifically supports application
    information.

12. Do not provide recommendations or facts from
    outside the supplied evidence.

Return ONLY the final answer text.
"""

    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    llm = get_llm()

    response = llm.invoke(prompt)

    answer = response.content.strip()

    # =====================================================
    # EMPTY RESPONSE SAFETY
    # =====================================================

    if not answer:

        return {
            "answer": (
                "I could not generate a reliable "
                "answer from the available information."
            ),
            "grounded": False,
            "sources": [],
        }

    # =====================================================
    # PROVENANCE
    # =====================================================

    sources = build_sources(
        useful_documents
    )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    return {
        "answer": answer,
        "grounded": True,
        "sources": sources,
    }