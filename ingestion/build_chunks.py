import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

INPUT_FILE = Path(
    "data/processed/unified_documents.json"
)

OUTPUT_FILE = Path(
    "data/processed/chunks.json"
)


# ---------------------------------------------------------
# Chunking configuration
# ---------------------------------------------------------

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ],
)


# ---------------------------------------------------------
# Load JSON
# ---------------------------------------------------------

def load_documents():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ---------------------------------------------------------
# Determine primary scheme
# ---------------------------------------------------------

def determine_primary_scheme(
    metadata,
    text
):
    """
    Some PDF pages contain information about
    multiple schemes, especially the crop insurance PDF.

    We try to identify the most specific scheme
    mentioned in the text.

    This is metadata enrichment, not an LLM guess.
    """

    scheme_ids = metadata.get(
        "scheme_ids",
        []
    )

    if not scheme_ids:

        return metadata.get(
            "scheme_id",
            "UNKNOWN"
        )

    if len(scheme_ids) == 1:

        return scheme_ids[0]

    text_upper = text.upper()

    # Specific scheme headings/phrases
    # are checked first.

    if (
        "PRADHAN MANTRI FASAL BIMA YOJANA"
        in text_upper
    ):
        return "PMFBY"

    if (
        "WEATHER BASED CROP INSURANCE"
        in text_upper
    ):
        return "WBCIS"

    if (
        "COCONUT PALM INSURANCE"
        in text_upper
    ):
        return "CPIS"

    if (
        "UNIFIED PACKAGE INSURANCE"
        in text_upper
    ):
        return "UPIS"

    # If the page discusses several schemes,
    # retain the first mapped scheme as the
    # primary value and keep all IDs in metadata.

    return scheme_ids[0]


# ---------------------------------------------------------
# Create chunks
# ---------------------------------------------------------

def build_chunks(documents):

    chunks = []

    chunk_counter = 1

    for document in documents:

        text = document.get(
            "page_content",
            ""
        ).strip()

        if not text:

            continue

        metadata = document.get(
            "metadata",
            {}
        )

        text_chunks = splitter.split_text(
            text
        )

        primary_scheme = (
            determine_primary_scheme(
                metadata,
                text
            )
        )

        for chunk_index, chunk_text in enumerate(
            text_chunks
        ):

            chunk = {
                "chunk_id": (
                    f"chunk_{chunk_counter:04d}"
                ),

                "page_content": chunk_text,

                "metadata": {
                    # Scheme information
                    "scheme_id": primary_scheme,

                    "scheme_ids": metadata.get(
                        "scheme_ids",
                        [primary_scheme]
                    ),

                    "scheme_name": metadata.get(
                        "scheme_name",
                        ""
                    ),

                    # Topic
                    "topic": metadata.get(
                        "topic",
                        "government_scheme"
                    ),

                    "category": metadata.get(
                        "category",
                        "Government Scheme"
                    ),

                    # Source provenance
                    "source_type": metadata.get(
                        "source_type",
                        ""
                    ),

                    "source": metadata.get(
                        "source",
                        ""
                    ),

                    "source_file": metadata.get(
                        "source_file",
                        ""
                    ),

                    "page": metadata.get(
                        "page"
                    ),

                    # Audience / routing metadata
                    "audience": metadata.get(
                        "audience",
                        [
                            "farmer",
                            "public"
                        ]
                    ),

                    "state": metadata.get(
                        "state",
                        ["all_india"]
                    ),

                    # Chunk information
                    "chunk_index": chunk_index,

                    "total_chunks": len(
                        text_chunks
                    ),
                },
            }

            chunks.append(chunk)

            chunk_counter += 1

    return chunks


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("BUILDING RAG CHUNKS")
    print("=" * 70)

    print(
        f"Input: {INPUT_FILE}"
    )

    print(
        f"Chunk size: {CHUNK_SIZE}"
    )

    print(
        f"Chunk overlap: {CHUNK_OVERLAP}"
    )

    print()

    documents = load_documents()

    print(
        f"Documents loaded: "
        f"{len(documents)}"
    )

    chunks = build_chunks(
        documents
    )

    # -----------------------------------------------------
    # Save chunks
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            indent=2,
            ensure_ascii=False
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("CHUNKING COMPLETE")
    print("=" * 70)

    print(
        f"Input documents: "
        f"{len(documents)}"
    )

    print(
        f"Total chunks: "
        f"{len(chunks)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print()

    # -----------------------------------------------------
    # Source distribution
    # -----------------------------------------------------

    source_counts = {}

    for chunk in chunks:

        source_type = chunk[
            "metadata"
        ]["source_type"]

        source_counts[source_type] = (
            source_counts.get(
                source_type,
                0
            ) + 1
        )

    print("Chunks by source:")

    for source, count in sorted(
        source_counts.items()
    ):

        print(
            f"  {source}: {count}"
        )

    print()

    # -----------------------------------------------------
    # Scheme distribution
    # -----------------------------------------------------

    scheme_counts = {}

    for chunk in chunks:

        scheme_id = chunk[
            "metadata"
        ]["scheme_id"]

        scheme_counts[scheme_id] = (
            scheme_counts.get(
                scheme_id,
                0
            ) + 1
        )

    print("Chunks by primary scheme:")

    for scheme_id, count in sorted(
        scheme_counts.items()
    ):

        print(
            f"  {scheme_id}: {count}"
        )

    print()

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    print("=" * 70)
    print("SAMPLE CHUNKS")
    print("=" * 70)

    for chunk in chunks[:3]:

        metadata = chunk[
            "metadata"
        ]

        print()
        print(
            f"Chunk: "
            f"{chunk['chunk_id']}"
        )

        print(
            f"Scheme: "
            f"{metadata['scheme_id']}"
        )

        print(
            f"Source: "
            f"{metadata['source_type']}"
        )

        print(
            f"Page: "
            f"{metadata['page']}"
        )

        print(
            f"Text: "
            f"{chunk['page_content'][:300]}..."
        )


if __name__ == "__main__":
    main()