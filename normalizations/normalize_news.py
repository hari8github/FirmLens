import sys
import re
import hashlib
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data.news_extraction import fetch_company_news, API_KEY

# --------------------------------
# Helpers
# --------------------------------

def generate_news_id(url: str) -> str:
    """Stable ID based on URL"""
    return hashlib.md5(url.encode()).hexdigest()


def clean_text(text: str | None) -> str | None:
    if not text:
        return None
    return text.strip()


def parse_date(date_str: str | None) -> str | None:
    """
    Converts '2026-01-14T06:36:26Z' -> '2026-01-14'
    """
    if not date_str:
        return None
    return date_str.split("T")[0]


def infer_event_type(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()

    if any(k in text for k in ["profit", "pat", "earnings", "results", "margin"]):
        return "earnings"
    if any(k in text for k in ["labour", "law", "regulation", "policy"]):
        return "regulation"
    if any(k in text for k in ["brokerage", "rating", "target", "buy", "sell"]):
        return "market_opinion"
    if any(k in text for k in ["deal", "contract", "order", "partnership"]):
        return "business_update"

    return "general"


def infer_time_context(text: str) -> str | None:
    """
    Extracts Q / FY context if present
    """
    match = re.search(r"(Q[1-4])\s*(FY)?\s*(\d{2,4})?", text)
    if match:
        return match.group(0)
    return None


# --------------------------------
# Normalization
# --------------------------------

def normalize_news():
    COMPANY_NAME = "Tata Elxsi"
    COMPANY_ID = "TATA_ELXSI"

    # Fetch articles from news_extraction.py
    raw_articles = fetch_company_news(
        company_name=COMPANY_NAME,
        api_key=API_KEY,
        days=30,
        page_size=10
    )
    normalized = []

    for article in raw_articles:
        title = clean_text(article.get("title"))
        summary = clean_text(article.get("summary"))  # Changed from "description" to "summary"
        url = article.get("url")

        if not title or not url:
            continue

        event_type = infer_event_type(title, summary or "")
        time_context = infer_time_context(title + " " + (summary or ""))

        normalized.append({
            "news_id": generate_news_id(url),
            "company_id": COMPANY_ID,

            "title": title,
            "summary": summary,
            "source": article.get("source"),  # Already a string, not a dict
            "published_at": parse_date(article.get("published_at")),  # Changed from "publishedAt" to "published_at"
            "url": url,

            "event_type": event_type,
            "time_context": time_context
        })

    return normalized


# --------------------------------
# Run directly
# --------------------------------

if __name__ == "__main__":
    news = normalize_news()

    print("\n--- NORMALIZED NEWS ---")
    print("Total articles:", len(news))
    print("=" * 80)

    for n in news:
        print("\n---")
        print("Title:", n["title"])
        print("Summary:", n["summary"])
        print("Source:", n["source"])
        print("Date:", n["published_at"])
        print("Event Type:", n["event_type"])
        print("Time Context:", n["time_context"])
        print("URL:", n["url"])
        print("News ID:", n["news_id"])