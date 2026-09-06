import json
from pathlib import Path


SCHEMES_FILE = Path(
    "data/processed/schemes.json"
)

PDF_DOCUMENTS_FILE = Path(
    "data/processed/pdf_documents.json"
)

OUTPUT_FILE = Path(
    "data/processed/unified_documents.json"
)


# ---------------------------------------------------------
# Additional schemes found in Vikaspedia PDFs
# ---------------------------------------------------------

ADDITIONAL_SCHEMES = {
    "WBCIS": {
        "scheme_name": "Weather Based Crop Insurance Scheme",
        "category": "Crop Insurance",
        "topic": "crop_insurance",
        "target_audience": ["farmer", "public"],
    },

    "CPIS": {
        "scheme_name": "Coconut Palm Insurance Scheme",
        "category": "Crop Insurance",
        "topic": "crop_insurance",
        "target_audience": ["farmer", "public"],
    },

    "UPIS": {
        "scheme_name": "Unified Package Insurance Scheme",
        "category": "Insurance",
        "topic": "crop_insurance",
        "target_audience": ["farmer", "public"],
    },

    "PM_KISAN_MAAN_DHAN": {
        "scheme_name": "PM Kisan Maandhan Yojana",
        "category": "Pension",
        "topic": "pension",
        "target_audience": ["farmer", "public"],
    },

    "DAIRY_INTEREST_SUBVENTION": {
        "scheme_name": "Interest Subvention for Dairy Sector",
        "category": "Dairy",
        "topic": "dairy",
        "target_audience": [
            "farmer",
            "agency",
            "public",
        ],
    },
}


def load_json(path):
    """Load a JSON file."""

    if not path.exists():

        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def create_bighaat_documents(schemes):
    """
    Convert scheme records from schemes.json
    into unified document records.
    """

    documents = []

    for scheme in schemes:

        text_parts = []

        if scheme.get("scheme_name"):
            text_parts.append(
                f"Scheme: {scheme['scheme_name']}"
            )

        if scheme.get("description"):
            text_parts.append(
                f"Description: {scheme['description']}"
            )

        if scheme.get("benefits"):

            benefits = "\n".join(
                f"- {benefit}"
                for benefit in scheme["benefits"]
            )

            text_parts.append(
                f"Benefits:\n{benefits}"
            )

        if scheme.get("eligibility"):

            text_parts.append(
                f"Eligibility: "
                f"{scheme['eligibility']}"
            )

        if scheme.get("application_process"):

            application = "\n".join(
                f"- {step}"
                for step in scheme[
                    "application_process"
                ]
            )

            text_parts.append(
                f"Application Process:\n"
                f"{application}"
            )

        if scheme.get("documents_required"):

            documents_required = "\n".join(
                f"- {doc}"
                for doc in scheme[
                    "documents_required"
                ]
            )

            text_parts.append(
                f"Documents Required:\n"
                f"{documents_required}"
            )

        document = {
            "document_type": "scheme_record",

            "page_content": "\n\n".join(
                text_parts
            ),

            "metadata": {
                "scheme_id": scheme[
                    "scheme_id"
                ],

                "scheme_name": scheme[
                    "scheme_name"
                ],

                "category": scheme.get(
                    "category",
                    "Government Scheme"
                ),

                "topic": scheme.get(
                    "category",
                    "government_scheme"
                ),

                "source_type": "bighaat",

                "source": scheme.get(
                    "source_url",
                    ""
                ),

                "source_file": "",

                "page": None,

                "audience": scheme.get(
                    "target_audience",
                    ["farmer", "public"]
                ),

                "state": scheme.get(
                    "states",
                    ["all_india"]
                ),

                "year": scheme.get(
                    "year",
                    "2026"
                ),
            },
        }

        documents.append(document)

    return documents


def create_pdf_documents(pdf_documents):
    """
    Convert PDF page records into unified
    document records.
    """

    documents = []

    for pdf_document in pdf_documents:

        metadata = pdf_document[
            "metadata"
        ]

        document = {
            "document_type": "pdf_page",

            "page_content": pdf_document[
                "page_content"
            ],

            "metadata": {
                "scheme_ids": metadata[
                    "scheme_ids"
                ],

                "source_type": "vikaspedia_pdf",

                "source": "Vikaspedia",

                "source_file": metadata[
                    "source_file"
                ],

                "page": metadata[
                    "page"
                ],

                "topic": metadata[
                    "topic"
                ],

                "audience": metadata[
                    "audience"
                ],

                "state": metadata[
                    "state"
                ],
            },
        }

        documents.append(document)

    return documents


def create_additional_scheme_records(
    pdf_documents
):
    """
    Create lightweight scheme records for schemes
    that appear only in PDFs and not in BigHaat.
    """

    documents = []

    existing_scheme_ids = set()

    for document in pdf_documents:

        for scheme_id in document[
            "metadata"
        ]["scheme_ids"]:

            existing_scheme_ids.add(
                scheme_id
            )

    for scheme_id, info in (
        ADDITIONAL_SCHEMES.items()
    ):

        if scheme_id not in existing_scheme_ids:
            continue

        document = {
            "document_type": "scheme_catalog",

            "page_content": (
                f"Scheme: "
                f"{info['scheme_name']}\n"
                f"Category: "
                f"{info['category']}\n"
                f"Topic: "
                f"{info['topic']}"
            ),

            "metadata": {
                "scheme_id": scheme_id,

                "scheme_name": info[
                    "scheme_name"
                ],

                "category": info[
                    "category"
                ],

                "topic": info[
                    "topic"
                ],

                "source_type": (
                    "vikaspedia_pdf"
                ),

                "source": "Vikaspedia",

                "source_file": "",

                "page": None,

                "audience": info[
                    "target_audience"
                ],

                "state": [
                    "all_india"
                ],
            },
        }

        documents.append(document)

    return documents


def main():

    print("=" * 70)
    print("BUILDING UNIFIED KNOWLEDGE DATASET")
    print("=" * 70)

    # -----------------------------------------------------
    # Load source datasets
    # -----------------------------------------------------

    schemes = load_json(
        SCHEMES_FILE
    )

    pdf_documents = load_json(
        PDF_DOCUMENTS_FILE
    )

    print(
        f"BigHaat scheme records: "
        f"{len(schemes)}"
    )

    print(
        f"PDF page documents: "
        f"{len(pdf_documents)}"
    )

    # -----------------------------------------------------
    # Convert BigHaat records
    # -----------------------------------------------------

    bighaat_documents = (
        create_bighaat_documents(
            schemes
        )
    )

    # -----------------------------------------------------
    # Convert PDF records
    # -----------------------------------------------------

    pdf_docs = create_pdf_documents(
        pdf_documents
    )

    # -----------------------------------------------------
    # Add PDF-only scheme records
    # -----------------------------------------------------

    additional_documents = (
        create_additional_scheme_records(
            pdf_documents
        )
    )

    # -----------------------------------------------------
    # Combine everything
    # -----------------------------------------------------

    unified_documents = (
        bighaat_documents
        + additional_documents
        + pdf_docs
    )

    # -----------------------------------------------------
    # Save
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
            unified_documents,
            f,
            indent=2,
            ensure_ascii=False
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("UNIFIED DATASET COMPLETE")
    print("=" * 70)

    print(
        f"BigHaat documents: "
        f"{len(bighaat_documents)}"
    )

    print(
        f"PDF-only scheme records: "
        f"{len(additional_documents)}"
    )

    print(
        f"PDF page documents: "
        f"{len(pdf_docs)}"
    )

    print(
        f"Total unified documents: "
        f"{len(unified_documents)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print()

    # -----------------------------------------------------
    # Source summary
    # -----------------------------------------------------

    source_counts = {}

    for document in unified_documents:

        source_type = document[
            "metadata"
        ]["source_type"]

        source_counts[source_type] = (
            source_counts.get(
                source_type,
                0
            ) + 1
        )

    print("Source distribution:")

    for source, count in sorted(
        source_counts.items()
    ):

        print(
            f"  {source}: {count}"
        )

    print()

    # -----------------------------------------------------
    # Scheme summary
    # -----------------------------------------------------

    scheme_ids = set()

    for document in unified_documents:

        metadata = document[
            "metadata"
        ]

        if "scheme_id" in metadata:

            scheme_ids.add(
                metadata["scheme_id"]
            )

        if "scheme_ids" in metadata:

            scheme_ids.update(
                metadata["scheme_ids"]
            )

    print(
        f"Unique scheme IDs: "
        f"{len(scheme_ids)}"
    )

    for scheme_id in sorted(
        scheme_ids
    ):

        print(
            f"  - {scheme_id}"
        )


if __name__ == "__main__":
    main()