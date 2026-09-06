from bs4 import BeautifulSoup
from pathlib import Path
import json
import re


INPUT_FILE = Path("data/raw/farmer_schemes_2026.html")
OUTPUT_FILE = Path("data/processed/schemes.json")


SOURCE_URL = (
    "https://www.bighaat.com/"
    "kisan-vedika/blogs/government-schemes-farmers-2026"
)


def clean_text(text):
    """Clean extra whitespace from extracted HTML text."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_scheme_id(name):
    """Create a stable ID for each scheme."""
    name = name.upper()

    replacements = {
        "PRADHAN MANTRI KISAN SAMMAN NIDHI": "PM_KISAN",
        "PM-KISAN": "PM_KISAN",
        "PRADHAN MANTRI FASAL BIMA YOJANA (PMFBY)": "PMFBY",
        "PMFBY": "PMFBY",
        "KISAN CREDIT CARD (KCC)": "KCC",
        "PM KRISHI SINCHAI YOJANA": "PM_KRISHI_SINCHAI",
        "SOIL HEALTH CARD SCHEME": "SOIL_HEALTH_CARD",
        "NATIONAL MISSION ON SUSTAINABLE AGRICULTURE": "NMSA",
        "AGRICULTURE MECHANIZATION SUBSIDY SCHEMES": "AGRI_MECHANIZATION",
        "PM-KUSUM SCHEME": "PM_KUSUM",
    }

    for key, value in replacements.items():
        if key in name:
            return value

    # Fallback ID
    name = re.sub(r"[^A-Z0-9]+", "_", name)
    return name.strip("_")


def extract_schemes(soup):
    """
    Extract numbered scheme sections from the BigHaat article.
    """

    schemes = []

    headings = soup.find_all("h3")

    for heading in headings:

        heading_text = clean_text(heading.get_text(" ", strip=True))

        # We only want numbered scheme headings:
        # 1. PM-KISAN...
        # 2. PMFBY...
        # etc.
        if not re.match(r"^\d+\.", heading_text):
            continue

        scheme_name = re.sub(
            r"^\d+\.\s*",
            "",
            heading_text
        ).strip()

        scheme_id = normalize_scheme_id(scheme_name)

        description_parts = []
        benefits = []

        current = heading.find_next_sibling()

        while current:

            # Stop at the next h3
            if current.name == "h3":
                break

            # Stop if we reach a major h2 section
            if current.name == "h2":
                break

            if current.name == "p":

                text = clean_text(
                    current.get_text(" ", strip=True)
                )

                if text:
                    description_parts.append(text)

            elif current.name == "ul":

                items = []

                for li in current.find_all("li"):

                    item = clean_text(
                        li.get_text(" ", strip=True)
                    )

                    if item:
                        items.append(item)

                # Most lists in this article are benefit lists.
                if items:
                    benefits.extend(items)

            current = current.find_next_sibling()

        scheme = {
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "category": "Government Scheme",
            "description": " ".join(description_parts),
            "benefits": benefits,
            "eligibility": "",
            "application_process": "",
            "documents_required": [],
            "target_audience": [
                "farmer",
                "public"
            ],
            "states": [
                "all_india"
            ],
            "source_type": "bighaat",
            "source_url": SOURCE_URL,
            "year": "2026"
        }

        schemes.append(scheme)

    return schemes


def extract_general_application_info(soup):
    """
    Extract the common application/document information
    appearing later in the article.
    """

    application = {
        "application_process": [],
        "documents_required": []
    }

    headings = soup.find_all("h2")

    for heading in headings:

        heading_text = clean_text(
            heading.get_text(" ", strip=True)
        ).lower()

        if "how to apply" not in heading_text:
            continue

        current = heading.find_next_sibling()

        while current:

            if current.name == "h2":
                break

            if current.name == "ol":

                for li in current.find_all("li"):

                    text = clean_text(
                        li.get_text(" ", strip=True)
                    )

                    if text:
                        application["application_process"].append(text)

            elif current.name == "ul":

                for li in current.find_all("li"):

                    text = clean_text(
                        li.get_text(" ", strip=True)
                    )

                    if text:
                        application["documents_required"].append(
                            text
                        )

            current = current.find_next_sibling()

    return application


def main():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"HTML file not found: {INPUT_FILE}"
        )

    print(f"Reading: {INPUT_FILE}")

    html = INPUT_FILE.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    schemes = extract_schemes(soup)

    general_info = extract_general_application_info(
        soup
    )

    # Add common application information
    # to every scheme.
    for scheme in schemes:

        scheme["application_process"] = (
            general_info["application_process"]
        )

        scheme["documents_required"] = (
            general_info["documents_required"]
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            schemes,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("SCHEMA EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Number of schemes: {len(schemes)}")
    print(f"Output: {OUTPUT_FILE}")
    print()

    for scheme in schemes:

        print(
            f"- {scheme['scheme_id']}: "
            f"{scheme['scheme_name']}"
        )


if __name__ == "__main__":
    main()