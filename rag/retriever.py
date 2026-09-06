import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

VECTORSTORE_FOLDER = Path("vectorstores")

ROLES = {
    "farmer",
    "public",
    "government",
    "agency",
}

EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)


# ============================================================
# EMBEDDINGS
# ============================================================

def get_embeddings():

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY was not found. "
            "Check your .env file."
        )

    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=api_key,
    )


# ============================================================
# LOAD VECTOR STORE
# ============================================================

def load_vectorstore(role: str):

    role = role.lower().strip()

    if role not in ROLES:
        raise ValueError(
            f"Invalid role '{role}'. "
            f"Choose one of: {sorted(ROLES)}"
        )

    vectorstore_path = (
        VECTORSTORE_FOLDER / role
    )

    if not vectorstore_path.exists():

        raise FileNotFoundError(
            f"Vector store not found: "
            f"{vectorstore_path}"
        )

    embeddings = get_embeddings()

    vectorstore = FAISS.load_local(
        str(vectorstore_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vectorstore


# ============================================================
# RETRIEVE
# ============================================================

def retrieve(
    query: str,
    role: str = "farmer",
    top_k: int = 5,
    scheme_id: str = None,
):

    if not query or not query.strip():

        raise ValueError(
            "Query cannot be empty."
        )

    if top_k < 1:

        raise ValueError(
            "top_k must be at least 1."
        )

    # --------------------------------------------------------
    # Load role-specific vector store
    # --------------------------------------------------------

    vectorstore = load_vectorstore(
        role
    )

    # --------------------------------------------------------
    # Retrieve a larger candidate set when filtering
    # --------------------------------------------------------

    if scheme_id:

        search_k = max(
            top_k * 5,
            20,
        )

    else:

        search_k = top_k

    # --------------------------------------------------------
    # Similarity search
    # --------------------------------------------------------

    results = vectorstore.similarity_search_with_score(
        query,
        k=search_k,
    )

    # --------------------------------------------------------
    # Always initialize as a LIST
    # --------------------------------------------------------

    retrieved = []

    # --------------------------------------------------------
    # Process results
    # --------------------------------------------------------

    for document, score in results:

        metadata = document.metadata

        document_scheme_id = metadata.get(
            "scheme_id"
        )

        # ----------------------------------------------------
        # Scheme filtering
        # ----------------------------------------------------

        if scheme_id:

            if document_scheme_id != scheme_id:

                continue

        # ----------------------------------------------------
        # Add result
        # ----------------------------------------------------

        retrieved.append(
            {
                "chunk_id": metadata.get(
                    "chunk_id",
                    metadata.get(
                        "id",
                        "N/A",
                    ),
                ),

                "document": document,

                "score": float(score),

                "metadata": metadata,
            }
        )

        # ----------------------------------------------------
        # Stop once we have enough matching documents
        # ----------------------------------------------------

        if len(retrieved) >= top_k:

            break

    # --------------------------------------------------------
    # IMPORTANT:
    # Always return a list.
    #
    # Never return None.
    # --------------------------------------------------------

    return retrieved