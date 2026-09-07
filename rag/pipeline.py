from rag.answer_generator import generate_answer
from rag.contextual_query import contextualize_query
from rag.conversation_memory import ConversationMemory
from rag.query_classifier import classify_query
from rag.query_rewriter import rewrite_query
from rag.retrieval_grader import grade_retrieval
from rag.retriever import retrieve

from rag.cache import (
    make_cache_key,
    get_cached_response,
    set_cached_response,
)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_TOP_K = 5
DEFAULT_MIN_CONFIDENCE = 0.65
DEFAULT_MAX_RETRIES = 1


conversation_memory = ConversationMemory()


# ============================================================
# CONVERSATIONAL MESSAGE HANDLING
# ============================================================

GREETING_RESPONSES = {
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "good morning",
    "good afternoon",
    "good evening",

}

THANKS_RESPONSES = {
    "thanks",
    "thankyou",
    "thank you",
    "thanks a lot",
    "thank you so much",
    "thank you very much",
    "many thanks",
}

SMALL_TALK_RESPONSES = {
    "how are you",
    "how are you?",
    "how are you doing",
    "how are you doing?",
    "what's up",
    "whats up",
}

FAREWELL_RESPONSES = {
    "bye",
    "goodbye",
    "good bye",
    "see you",
    "see you later",
    "goodnight",
    "good night",
}

ACKNOWLEDGEMENT_RESPONSES = {
    "ok",
    "okay",
    "got it",
    "great",
    "perfect",
    "alright",
    "all right",
}


def normalize_conversational_query(query: str) -> str:
    """
    Normalize punctuation/whitespace for simple conversational
    message detection without altering the original user query.
    """
    if not query:
        return ""

    normalized = " ".join(
        query.lower().strip().split()
    )

    normalized = normalized.rstrip("!.?")

    return normalized


def get_conversational_response(query: str):
    """
    Return a fixed conversational response for greetings,
    thanks, small talk, acknowledgements, and farewells.

    Returns None when the query should continue through
    the normal RAG pipeline.
    """
    normalized = normalize_conversational_query(query)

    if not normalized:
        return None

    if normalized in GREETING_RESPONSES:
        return (
            "Hello, I'm your Agri Assist chat bot, "
            "how can I help you?"
        )

    if normalized in THANKS_RESPONSES:
        return (
            "You're welcome! I'm happy to help. "
            "Ask me anything about agriculture schemes "
            "and farmer support."
        )

    if normalized in SMALL_TALK_RESPONSES:
        return (
            "I'm doing well and ready to help. "
            "What would you like to know about agriculture "
            "schemes or farmer support?"
        )

    if normalized in FAREWELL_RESPONSES:
        return (
            "Goodbye! I'm here whenever you need help "
            "with agriculture-related schemes and farmer support."
        )

    if normalized in ACKNOWLEDGEMENT_RESPONSES:
        return (
            "You're welcome! Let me know what you'd like "
            "to know about agriculture schemes or farmer support."
        )

    return None


# ============================================================
# MAIN RAG PIPELINE
# ============================================================

def run_rag_pipeline(
    query: str,
    role: str = "farmer",
    conversation_id: str = "default",
    top_k: int = DEFAULT_TOP_K,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    max_retries: int = DEFAULT_MAX_RETRIES,
    scheme_id: str | None = None,
):
    """
    Complete conversational RAG pipeline.

    Flow:

    1. Conversation history
    2. Contextual query rewriting
    3. Query classification
    4. Redis cache lookup
    5. Out-of-domain handling
    6. Initial retrieval
    7. Initial grading
    8. Corrective RAG
    9. Grounded answer generation
    10. Redis caching
    11. Conversation memory
    12. Return complete trace
    """

    # ========================================================
    # 1. VALIDATION
    # ========================================================

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    query = query.strip()

    # ========================================================
    # 2. CONVERSATIONAL MESSAGE HANDLING
    # ========================================================
    #
    # Handle greetings, thanks, small talk, acknowledgements,
    # and farewells before contextualization, classification,
    # Redis lookup, retrieval, grading, corrective RAG, or
    # answer generation.
    #
    # This prevents messages such as "thanks" from being sent
    # to FAISS and accidentally producing an unrelated scheme
    # answer.
    # ========================================================

    conversational_response = (
        get_conversational_response(query)
    )

    if conversational_response:

        answer = conversational_response

        conversation_memory.add_message(
            conversation_id,
            "user",
            query,
        )

        conversation_memory.add_message(
            conversation_id,
            "assistant",
            answer,
        )

        normalized_query = (
            normalize_conversational_query(query)
        )

        if normalized_query in GREETING_RESPONSES:
            conversational_intent = "greeting"
        elif normalized_query in THANKS_RESPONSES:
            conversational_intent = "thanks"
        elif normalized_query in SMALL_TALK_RESPONSES:
            conversational_intent = "small_talk"
        elif normalized_query in FAREWELL_RESPONSES:
            conversational_intent = "farewell"
        else:
            conversational_intent = "acknowledgement"

        return {
            "original_query": query,
            "contextualized_query": query,
            "conversation_id": conversation_id,
            "role": role,
            "scheme_id": scheme_id,
            "contextualization": {
                "original_query": query,
                "contextualized_query": query,
                "was_rewritten": False,
                "reason": (
                    "Conversational message detected."
                ),
            },
            "classification": {
                "domain": "conversation",
                "intent": conversational_intent,
                "confidence": 1.0,
                "should_retrieve": False,
            },
            "cache": {
                "hit": False,
                "key": None,
            },
            "initial_retrieval": [],
            "initial_grading": None,
            "correction_triggered": False,
            "rewritten_query": None,
            "retry_retrieval": [],
            "retry_grading": None,
            "final_query": query,
            "final_documents": [],
            "final_grading": None,
            "answer": answer,
            "grounded": True,
            "sources": [],
            "status": "conversation",
        }

    # ========================================================
    # 3. ROLE VALIDATION / NORMALIZATION
    # ========================================================

    role = (
        role
        .strip()
        .lower()
    )

    conversation_id = (
        conversation_id
        .strip()
    )

    if scheme_id:
        scheme_id = scheme_id.strip()


    # ========================================================
    # 4. CONVERSATION HISTORY
    # ========================================================

    history = (
        conversation_memory.get_recent_history(
            conversation_id,
            max_messages=10,
        )
        or []
    )


    # ========================================================
    # 5. CONTEXTUALIZE QUERY
    # ========================================================

    contextualization = contextualize_query(
        query,
        history,
    )

    contextualized_query = contextualization.get(
        "contextualized_query",
        query,
    )

    if not contextualized_query:
        contextualized_query = query


    # ========================================================
    # 6. SELECTED SCHEME CONTEXT
    # ========================================================

    retrieval_query = contextualized_query

    if scheme_id:

        retrieval_query = (
            f"Scheme: {scheme_id}. "
            f"Question: {contextualized_query}"
        )


    # ========================================================
    # 7. QUERY CLASSIFICATION
    # ========================================================

    classification = classify_query(
        retrieval_query
    )

    if classification is None:
        classification = {
            "domain": "other",
            "intent": "other",
            "confidence": 0.0,
            "should_retrieve": False,
        }


    # ========================================================
    # 8. REDIS CACHE LOOKUP
    # ========================================================

    cache_key = make_cache_key(
        query=contextualized_query,
        role=role,
        conversation_id=conversation_id,
        scheme_id=scheme_id,
    )

    cached_response = get_cached_response(
        cache_key
    )


    if cached_response is not None:

        answer = cached_response.get(
            "answer",
            "I could not generate a reliable answer.",
        )

        grounded = cached_response.get(
            "grounded",
            False,
        )

        sources = cached_response.get(
            "sources",
            [],
        )

        if sources is None:
            sources = []


        # ----------------------------------------------------
        # Save conversation
        # ----------------------------------------------------

        conversation_memory.add_message(
            conversation_id,
            "user",
            query,
        )

        conversation_memory.add_message(
            conversation_id,
            "assistant",
            answer,
        )


        return {
            "original_query": query,

            "contextualized_query": (
                contextualized_query
            ),

            "conversation_id": conversation_id,

            "role": role,

            "scheme_id": scheme_id,

            "contextualization": (
                contextualization
            ),

            "classification": (
                classification
            ),

            "cache": {
                "hit": True,
                "key": cache_key,
            },

            "initial_retrieval": [],

            "initial_grading": None,

            "correction_triggered": False,

            "rewritten_query": None,

            "retry_retrieval": [],

            "retry_grading": None,

            "final_query": contextualized_query,

            "final_documents": [],

            "final_grading": None,

            "answer": answer,

            "grounded": grounded,

            "sources": sources,

            "status": "cached",
        }


    # ========================================================
    # 9. OUT-OF-DOMAIN HANDLING
    # ========================================================

    if not classification.get(
        "should_retrieve",
        False,
    ):

        answer = (
            "I can help with agriculture-related "
            "government schemes, eligibility, benefits, "
            "subsidies, insurance, credit, irrigation, "
            "and related farmer assistance. "
            "Please ask an agriculture-related question."
        )


        conversation_memory.add_message(
            conversation_id,
            "user",
            query,
        )

        conversation_memory.add_message(
            conversation_id,
            "assistant",
            answer,
        )


        return {
            "original_query": query,

            "contextualized_query": (
                contextualized_query
            ),

            "conversation_id": conversation_id,

            "role": role,

            "scheme_id": scheme_id,

            "contextualization": (
                contextualization
            ),

            "classification": (
                classification
            ),

            "cache": {
                "hit": False,
                "key": cache_key,
            },

            "initial_retrieval": [],

            "initial_grading": None,

            "correction_triggered": False,

            "rewritten_query": None,

            "retry_retrieval": [],

            "retry_grading": None,

            "final_query": contextualized_query,

            "final_documents": [],

            "final_grading": None,

            "answer": answer,

            "grounded": False,

            "sources": [],

            "status": "out_of_domain",
        }


    # ========================================================
    # 10. INITIAL RETRIEVAL
    # ========================================================

    initial_retrieval = retrieve(
        retrieval_query,
        role=role,
        top_k=top_k,
        scheme_id=scheme_id,
    )

    # IMPORTANT:
    # Never allow None to enter the pipeline.

    if initial_retrieval is None:
        initial_retrieval = []


    # ========================================================
    # 11. INITIAL GRADING
    # ========================================================

    if initial_retrieval:

        initial_grading = grade_retrieval(
            contextualized_query,
            initial_retrieval,
        )

    else:

        initial_grading = {
            "relevant": False,
            "confidence": 0.0,
            "reason": (
                "No documents were retrieved."
            ),
            "relevant_chunks": [],
        }


    # IMPORTANT:
    # Never allow None grading.

    if initial_grading is None:

        initial_grading = {
            "relevant": False,
            "confidence": 0.0,
            "reason": (
                "Retrieval grading did not "
                "return a result."
            ),
            "relevant_chunks": [],
        }


    # ========================================================
    # 12. INITIAL GRADING VALUES
    # ========================================================

    initial_relevant = initial_grading.get(
        "relevant",
        False,
    )

    initial_confidence = initial_grading.get(
        "confidence",
        0.0,
    )

    accepted_initial = (
        initial_relevant
        and initial_confidence >= min_confidence
    )


    # ========================================================
    # 13. CORRECTIVE RAG
    # ========================================================

    correction_triggered = False

    rewritten_query = None

    retry_retrieval = []

    retry_grading = None


    final_query = contextualized_query

    final_documents = initial_retrieval

    final_grading = initial_grading

    status = "accepted"


    # --------------------------------------------------------
    # Correction required
    # --------------------------------------------------------

    if (
        not accepted_initial
        and max_retries > 0
    ):

        correction_triggered = True


        # ----------------------------------------------------
        # Rewrite query
        # ----------------------------------------------------

        rewritten_query = rewrite_query(
            contextualized_query,
            initial_retrieval,
            initial_grading,
        )


        # ----------------------------------------------------
        # Safety fallback
        # ----------------------------------------------------

        if not rewritten_query:

            rewritten_query = (
                contextualized_query
            )


        retry_query = rewritten_query


        # ----------------------------------------------------
        # Add scheme context
        # ----------------------------------------------------

        if scheme_id:

            retry_query = (
                f"Scheme: {scheme_id}. "
                f"Question: {rewritten_query}"
            )


        # ----------------------------------------------------
        # Retry retrieval
        # ----------------------------------------------------

        retry_retrieval = retrieve(
            retry_query,
            role=role,
            top_k=top_k,
            scheme_id=scheme_id,
        )


        if retry_retrieval is None:

            retry_retrieval = []


        # ----------------------------------------------------
        # Retry grading
        # ----------------------------------------------------

        if retry_retrieval:

            retry_grading = grade_retrieval(
                rewritten_query,
                retry_retrieval,
            )

        else:

            retry_grading = {
                "relevant": False,
                "confidence": 0.0,
                "reason": (
                    "No documents were retrieved "
                    "after query correction."
                ),
                "relevant_chunks": [],
            }


        if retry_grading is None:

            retry_grading = {
                "relevant": False,
                "confidence": 0.0,
                "reason": (
                    "Retry grading did not "
                    "return a result."
                ),
                "relevant_chunks": [],
            }


        retry_relevant = retry_grading.get(
            "relevant",
            False,
        )

        retry_confidence = retry_grading.get(
            "confidence",
            0.0,
        )


        accepted_retry = (
            retry_relevant
            and retry_confidence >= min_confidence
        )


        # ----------------------------------------------------
        # Retry succeeded
        # ----------------------------------------------------

        if accepted_retry:

            final_query = rewritten_query

            final_documents = retry_retrieval

            final_grading = retry_grading

            status = "corrected"


        # ----------------------------------------------------
        # Retry failed
        # ----------------------------------------------------

        else:

            status = "insufficient_evidence"


    # --------------------------------------------------------
    # No retry available
    # --------------------------------------------------------

    elif not accepted_initial:

        status = "insufficient_evidence"


    # ========================================================
    # 14. FINAL SAFETY CHECK
    # ========================================================

    if final_documents is None:

        final_documents = []


    if final_grading is None:

        final_grading = {
            "relevant": False,
            "confidence": 0.0,
            "reason": (
                "No valid grading result."
            ),
            "relevant_chunks": [],
        }


    # ========================================================
    # 15. ANSWER GENERATION
    # ========================================================

    if (
        status in {
            "accepted",
            "corrected",
        }
        and final_grading.get(
            "relevant",
            False,
        )
        and final_grading.get(
            "confidence",
            0.0,
        ) >= min_confidence
    ):

        answer_result = generate_answer(
            final_query,
            final_documents,
            final_grading,
            role=role,
        )


        answer = answer_result.get(
            "answer",
            "I could not generate a reliable answer.",
        )

        grounded = answer_result.get(
            "grounded",
            False,
        )

        sources = answer_result.get(
            "sources",
            [],
        )


        # ----------------------------------------------------
        # Cache only grounded answers
        # ----------------------------------------------------

        if grounded:

            set_cached_response(
                cache_key,
                {
                    "answer": answer,
                    "grounded": grounded,
                    "sources": sources,
                },
            )


    else:

        answer = (
            "I could not find enough reliable information "
            "in the available agriculture sources to answer "
            "this question confidently."
        )

        grounded = False

        sources = []


    # ========================================================
    # 16. SAVE CONVERSATION
    # ========================================================

    conversation_memory.add_message(
        conversation_id,
        "user",
        query,
    )

    conversation_memory.add_message(
        conversation_id,
        "assistant",
        answer,
    )


    # ========================================================
    # 17. RETURN COMPLETE TRACE
    # ========================================================

    return {

        "original_query": query,

        "contextualized_query": (
            contextualized_query
        ),

        "conversation_id": conversation_id,

        "role": role,

        "scheme_id": scheme_id,

        "contextualization": (
            contextualization
        ),

        "classification": (
            classification
        ),

        "cache": {
            "hit": False,
            "key": cache_key,
        },

        "initial_retrieval": (
            initial_retrieval
        ),

        "initial_grading": (
            initial_grading
        ),

        "correction_triggered": (
            correction_triggered
        ),

        "rewritten_query": (
            rewritten_query
        ),

        "retry_retrieval": (
            retry_retrieval
        ),

        "retry_grading": (
            retry_grading
        ),

        "final_query": (
            final_query
        ),

        "final_documents": (
            final_documents
        ),

        "final_grading": (
            final_grading
        ),

        "answer": answer,

        "grounded": grounded,

        "sources": sources,

        "status": status,
    }