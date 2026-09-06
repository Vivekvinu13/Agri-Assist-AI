import json
from pathlib import Path

import fitz
import pytesseract
from PIL import Image


PDF_FOLDER = Path("data/pdfs")
OUTPUT_FILE = Path("data/processed/pdf_documents.json")


# ---------------------------------------------------------
# PDF → scheme mapping
# ---------------------------------------------------------

PDF_SCHEME_MAP = {
    "Credit facility for farmers.pdf": {
        "scheme_ids": ["KCC"],
        "topic": "credit",
    },

    "Crop insurance schemes.pdf": {
        "scheme_ids": [
            "PMFBY",
            "WBCIS",
            "CPIS",
            "UPIS",
        ],
        "topic": "crop_insurance",
    },

    "Interest subvention for dairy sector.pdf": {
        "scheme_ids": [
            "DAIRY_INTEREST_SUBVENTION"
        ],
        "topic": "dairy",
    },

    "PM Kisan Maan Dhan Yojana.pdf": {
        "scheme_ids": [
            "PM_KISAN_MAAN_DHAN"
        ],
        "topic": "pension",
    },

    "Pradhan Mantri Kisan Samman Nidhi.pdf": {
        "scheme_ids": [
            "PM_KISAN"
        ],
        "topic": "income_support",
    },

    "Pradhan Mantri Krishi Sinchai Yojana.pdf": {
        "scheme_ids": [
            "PM_KRISHI_SINCHAI"
        ],
        "topic": "irrigation",
    },
}


# ---------------------------------------------------------
# Clean text
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean common PDF/OCR extraction problems.
    """

    text = text.replace("\x00", " ")

    text = " ".join(text.split())

    return text.strip()


# ---------------------------------------------------------
# Determine whether extracted text is meaningful
# ---------------------------------------------------------

def is_meaningful_text(text):
    """
    Check whether normal PDF text extraction produced
    enough useful content.

    Very short extraction such as:
        vikaspedia.in

    is treated as unusable and triggers OCR.
    """

    if not text:
        return False

    cleaned = clean_text(text)

    if len(cleaned) < 100:
        return False

    # A page containing only the website watermark
    # is not useful for RAG.
    if cleaned.lower() in {
        "vikaspedia.in",
        "www.vikaspedia.in",
    }:
        return False

    return True


# ---------------------------------------------------------
# OCR fallback
# ---------------------------------------------------------

def ocr_page(page):
    """
    Render a PDF page as an image and run OCR.
    """

    print("    Running OCR...")

    # Render page at a higher resolution for better OCR.
    matrix = fitz.Matrix(2.5, 2.5)

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False,
    )

    image = Image.frombytes(
        "RGB",
        [pixmap.width, pixmap.height],
        pixmap.samples,
    )

    text = pytesseract.image_to_string(
        image,
        config="--psm 6",
    )

    return clean_text(text)


# ---------------------------------------------------------
# Extract PDF pages
# ---------------------------------------------------------

def extract_pdf(pdf_path):
    """
    Extract one document per PDF page.

    Uses normal PDF text extraction first.
    Falls back to OCR when extracted text is not useful.
    """

    documents = []

    pdf = fitz.open(pdf_path)

    mapping = PDF_SCHEME_MAP.get(
        pdf_path.name
    )

    if mapping is None:

        print(
            f"WARNING: No scheme mapping found "
            f"for {pdf_path.name}"
        )

        pdf.close()

        return documents

    for page_number, page in enumerate(
        pdf,
        start=1
    ):

        print(
            f"  Page {page_number}: "
            f"extracting text..."
        )

        # -------------------------------------------------
        # First attempt: normal PDF text extraction
        # -------------------------------------------------

        text = page.get_text()

        text = clean_text(text)

        extraction_method = "text"

        # -------------------------------------------------
        # Second attempt: OCR
        # -------------------------------------------------

        if not is_meaningful_text(text):

            print(
                f"    Normal extraction insufficient."
            )

            text = ocr_page(page)

            extraction_method = "ocr"

        # -------------------------------------------------
        # Skip if OCR also failed
        # -------------------------------------------------

        if not text:

            print(
                f"    WARNING: No usable text "
                f"on page {page_number}"
            )

            continue

        if len(text) < 50:

            print(
                f"    WARNING: Very little text "
                f"after OCR: {len(text)} characters"
            )

        document = {
            "page_content": text,

            "metadata": {
                "source_type": "vikaspedia_pdf",
                "source_file": pdf_path.name,
                "page": page_number,
                "scheme_ids": mapping["scheme_ids"],
                "topic": mapping["topic"],
                "audience": [
                    "farmer",
                    "public",
                    "government",
                    "agency",
                ],
                "state": "all_india",
                "extraction_method": extraction_method,
            },
        }

        documents.append(document)

        print(
            f"    Method: {extraction_method}"
        )

        print(
            f"    Characters: {len(text)}"
        )

    pdf.close()

    return documents


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    if not PDF_FOLDER.exists():

        raise FileNotFoundError(
            f"PDF folder not found: {PDF_FOLDER}"
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    all_documents = []

    pdf_files = sorted(
        PDF_FOLDER.glob("*.pdf")
    )

    print("=" * 70)
    print("PDF INGESTION STARTED")
    print("=" * 70)

    print(
        f"PDF folder: {PDF_FOLDER}"
    )

    print(
        f"PDF files found: {len(pdf_files)}"
    )

    print()

    # -----------------------------------------------------
    # Process every PDF
    # -----------------------------------------------------

    for pdf_path in pdf_files:

        print(
            f"Processing: {pdf_path.name}"
        )

        documents = extract_pdf(
            pdf_path
        )

        all_documents.extend(
            documents
        )

        print(
            f"  Pages extracted: "
            f"{len(documents)}"
        )

        print()

    # -----------------------------------------------------
    # Save extracted documents
    # -----------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_documents,
            f,
            indent=2,
            ensure_ascii=False
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("=" * 70)
    print("PDF INGESTION COMPLETE")
    print("=" * 70)

    print(
        f"PDFs processed: {len(pdf_files)}"
    )

    print(
        f"Documents/pages extracted: "
        f"{len(all_documents)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print()

    print("Scheme coverage:")

    scheme_counts = {}

    for document in all_documents:

        for scheme_id in document[
            "metadata"
        ]["scheme_ids"]:

            scheme_counts[scheme_id] = (
                scheme_counts.get(
                    scheme_id,
                    0
                ) + 1
            )

    for scheme_id, count in sorted(
        scheme_counts.items()
    ):

        print(
            f"  {scheme_id}: "
            f"{count} page(s)"
        )


if __name__ == "__main__":
    main()