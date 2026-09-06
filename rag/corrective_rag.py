from rag.query_classifier import classify_query
from rag.retriever import retrieve
from rag.retrieval_grader import grade_retrieval
from rag.query_rewriter import rewrite_query


DEFAULT_TOP_K = 5
DEFAULT_MIN_CONFIDENCE = 0.65
DEFAULT_MAX_RETRIES = 1


def corrective_retrieve(
    query: str,
    role: str = "farmer",
    top_k: int = DEFAULT_TOP_K,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    max_retries: int = DEFAULT_MAX_RETRIES,
):
    """
    Run the complete Corrective RAG retrieval pipeline.

    Pipeline:

        Query
          ↓
        Domain Classification
          ↓
        Agriculture?
          ↓
        Retrieval
          ↓
        Retrieval Grading
          ↓
        Accept OR Rewrite + Retry
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if max_retries < 0:
        raise ValueError("max_retries cannot be negative.")

    # ---------------------------------------------------------
    # 1. QUERY CLASSIFICATION
    # ---------------------------------------------------------

    classification = classify_query(query)

    trace = {
        "original_query": query,
        "role": role,

        "classification": classification,

        "top_k": top_k,
        "min_confidence": min_confidence,
        "max_retries": max_retries,

        "initial_retrieval": [],
        "initial_grading": None,

        "correction_triggered": False,
        "rewritten_query": None,

        "retry_retrieval": [],
        "retry_grading": None,

        "final_query": query,
        "final_documents": [],
        "final_grading": None,

        "status": None,
    }

    # ---------------------------------------------------------
    # 2. DOMAIN CHECK
    # ---------------------------------------------------------

    if not classification.get("should_retrieve", False):

        trace["status"] = "out_of_domain"

        return trace

    # ---------------------------------------------------------
    # 3. INITIAL RETRIEVAL
    # ---------------------------------------------------------

    initial_documents = retrieve(
        query=query,
        role=role,
        top_k=top_k,
    )

    trace["initial_retrieval"] = initial_documents

    # ---------------------------------------------------------
    # 4. INITIAL RETRIEVAL GRADING
    # ---------------------------------------------------------

    initial_grading = grade_retrieval(
        query=query,
        retrieved_documents=initial_documents,
    )

    trace["initial_grading"] = initial_grading

    initial_relevant = initial_grading.get(
        "relevant",
        False,
    )

    initial_confidence = float(
        initial_grading.get(
            "confidence",
            0.0,
        )
    )

    initial_is_good = (
        initial_relevant
        and initial_confidence >= min_confidence
    )

    # ---------------------------------------------------------
    # 5. ACCEPT GOOD RETRIEVAL
    # ---------------------------------------------------------

    if initial_is_good:

        trace["final_query"] = query
        trace["final_documents"] = initial_documents
        trace["final_grading"] = initial_grading
        trace["status"] = "accepted"

        return trace

    # ---------------------------------------------------------
    # 6. NO RETRY REQUESTED
    # ---------------------------------------------------------

    if max_retries == 0:

        trace["status"] = "insufficient_evidence"

        trace["final_query"] = query
        trace["final_documents"] = initial_documents
        trace["final_grading"] = initial_grading

        return trace

    # ---------------------------------------------------------
    # 7. CORRECTIVE RAG
    # ---------------------------------------------------------

    trace["correction_triggered"] = True

    rewritten = rewrite_query(
        original_query=query,
        retrieved_documents=initial_documents,
        grading_result=initial_grading,
    )

    rewritten_query = rewritten.get(
        "rewritten_query",
        query,
    )

    trace["rewritten_query"] = rewritten_query
    trace["final_query"] = rewritten_query

    # ---------------------------------------------------------
    # 8. RETRY RETRIEVAL
    # ---------------------------------------------------------

    retry_documents = retrieve(
        query=rewritten_query,
        role=role,
        top_k=top_k,
    )

    trace["retry_retrieval"] = retry_documents

    # ---------------------------------------------------------
    # 9. RETRY GRADING
    # ---------------------------------------------------------

    retry_grading = grade_retrieval(
        query=rewritten_query,
        retrieved_documents=retry_documents,
    )

    trace["retry_grading"] = retry_grading

    retry_relevant = retry_grading.get(
        "relevant",
        False,
    )

    retry_confidence = float(
        retry_grading.get(
            "confidence",
            0.0,
        )
    )

    retry_is_good = (
        retry_relevant
        and retry_confidence >= min_confidence
    )

    # ---------------------------------------------------------
    # 10. FINAL DECISION
    # ---------------------------------------------------------

    trace["final_documents"] = retry_documents
    trace["final_grading"] = retry_grading

    if retry_is_good:

        trace["status"] = "corrected"

    else:

        trace["status"] = "insufficient_evidence"

    return trace