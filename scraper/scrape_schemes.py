from playwright.sync_api import sync_playwright
from pathlib import Path

URL = "https://www.bighaat.com/kisan-vedika/blogs/government-schemes-farmers-2026"

OUTPUT = Path("data/raw/farmer_schemes_2026.html")


def scrape_page():

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(
            URL,
            wait_until="networkidle",
            timeout=60000
        )

        html = page.content()

        OUTPUT.write_text(
            html,
            encoding="utf-8"
        )

        print(f"Saved scraped page to: {OUTPUT}")

        browser.close()


if __name__ == "__main__":
    scrape_page()