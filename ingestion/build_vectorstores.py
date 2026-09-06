import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

INPUT_FILE = Path(
    "data/processed/chunks.json"
)

VECTORSTORE_FOLDER = Path(
    "vectorstores"
)


# ---------------------------------------------------------
# Roles
# ---------------------------------------------------------

ROLES = [
    "farmer",
    "public",
    "government",
    "agency",
]


# ---------------------------------------------------------
# Embedding model
# ---------------------------------------------------------

EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small"
)


# ---------------------------------------------------------
# Load chunks
# ---------------------------------------------------------

def load_chunks():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Chunks file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ---------------------------------------------------------
# Convert JSON chunk → LangChain Document
# ---------------------------------------------------------

def convert_to_documents(chunks):

    documents = []

    for chunk in chunks:

        metadata = chunk.get(
            "metadata",
            {}
        ).copy()

        # Add our internal chunk ID
        metadata["chunk_id"] = chunk.get(
            "chunk_id"
        )

        document = Document(
            page_content=chunk[
                "page_content"
            ],
            metadata=metadata
        )

        documents.append(document)

    return documents


# ---------------------------------------------------------
# Filter documents by role
# ---------------------------------------------------------

def filter_by_role(
    documents,
    role
):

    filtered = []

    for document in documents:

        audience = document.metadata.get(
            "audience",
            []
        )

        if role in audience:

            filtered.append(document)

    return filtered


# ---------------------------------------------------------
# Build FAISS index
# ---------------------------------------------------------

def build_vectorstore(
    documents,
    role,
    embeddings
):

    if not documents:

        print(
            f"WARNING: No documents found "
            f"for role '{role}'"
        )

        return

    print(
        f"Building FAISS index for: "
        f"{role}"
    )

    print(
        f"Documents/chunks: "
        f"{len(documents)}"
    )

    vectorstore = FAISS.from_documents(
        documents,
        embeddings
    )

    output_folder = (
        VECTORSTORE_FOLDER / role
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    vectorstore.save_local(
        str(output_folder)
    )

    print(
        f"Saved: {output_folder}"
    )

    print()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("BUILDING ROLE-SPECIFIC FAISS VECTOR STORES")
    print("=" * 70)

    chunks = load_chunks()

    print(
        f"Chunks loaded: {len(chunks)}"
    )

    print(
        f"Embedding model: {EMBEDDING_MODEL}"
    )

    print()

    # -----------------------------------------------------
    # Create embeddings
    # -----------------------------------------------------

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    documents = convert_to_documents(
        chunks
    )

    # -----------------------------------------------------
    # Build one FAISS index per role
    # -----------------------------------------------------

    for role in ROLES:

        role_documents = filter_by_role(
            documents,
            role
        )

        build_vectorstore(
            role_documents,
            role,
            embeddings
        )

    print("=" * 70)
    print("VECTOR STORE BUILD COMPLETE")
    print("=" * 70)

    print()

    print(
        "Created role-specific indexes:"
    )

    for role in ROLES:

        folder = (
            VECTORSTORE_FOLDER / role
        )

        if folder.exists():

            print(
                f"  ✓ {role}: {folder}"
            )

        else:

            print(
                f"  ✗ {role}: NOT CREATED"
            )


if __name__ == "__main__":
    main()