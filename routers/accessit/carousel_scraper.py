import json
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from playwright.sync_api import sync_playwright

router = APIRouter()

URL = "https://nz.accessit.online/ACG01/#!dashboard"
JSON_FILE_PATH = Path("routers/accessit/new_books.json")
CACHE_DURATION_SECONDS = 2 * 60 * 60  # 2 hours


def find_chromium_executable() -> str | None:
    """Find Chromium executable across common Linux/macOS paths at startup."""
    common_paths = [
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    ]
    for path in common_paths:
        if path.is_file():
            return str(path)
    return None


# Locate chromium once on startup
CHROMIUM_EXECUTABLE_PATH = find_chromium_executable()


def scraper(url: str, output_path: Path) -> None:
    """Scrapes book cover images and details from AccessIt and saves to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        launch_kwargs: dict[str, Any] = {"headless": True}
        if CHROMIUM_EXECUTABLE_PATH:
            launch_kwargs["executable_path"] = CHROMIUM_EXECUTABLE_PATH

        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")

        # Wait for the book covers to load
        page.wait_for_selector('img[src*="vimage"]', timeout=15000)

        # Scrape img elements pointing to the /vimage endpoint
        books = page.eval_on_selector_all(
            'img[src*="vimage"]',
            """imgs => imgs.map(img => ({
                title: (img.getAttribute('data-flip-title') || img.getAttribute('alt') || 'Untitled').trim(),
                url: img.src
            }))""",
        )

        # Save title and URL directly to JSON using Path API
        output_path.write_text(
            json.dumps(books, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        browser.close()


@router.get("/acg/new-books")
def get_notifications(sites: list[str] = Query([])) -> list[dict[str, str]]:
    """Returns new books, updating the cache file if missing or older than 2 hours."""
    now = time.time()
    should_scrape = False

    if not JSON_FILE_PATH.exists():
        should_scrape = True
    else:
        last_modified = JSON_FILE_PATH.stat().st_mtime
        if (now - last_modified) > CACHE_DURATION_SECONDS:
            should_scrape = True

    if should_scrape:
        scraper(URL, JSON_FILE_PATH)

    if not JSON_FILE_PATH.exists():
        raise HTTPException(
            status_code=500, detail="Failed to retrieve book data."
        )

    return json.loads(JSON_FILE_PATH.read_text(encoding="utf-8"))
