import requests
from datetime import datetime, timedelta

API_KEY = "27b3f808a71f48268e9a9c83df394026"

def fetch_company_news(
    company_name: str,
    api_key: str,
    days: int = 30,
    page_size: int = 10
):
    """
    Fetch recent news articles for a company using NewsAPI.
    Returns a list of cleaned news dictionaries.
    """

    base_url = "https://newsapi.org/v2/everything"

    to_date = datetime.today().strftime("%Y-%m-%d")
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")

    params = {
        "q": company_name,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": page_size,
        "apiKey": api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        raise Exception(f"NewsAPI error: {data}")

    articles = []

    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title"),
            "summary": item.get("description"),
            "source": item.get("source", {}).get("name"),
            "published_at": item.get("publishedAt"),
            "url": item.get("url")
        })

    return articles

news = fetch_company_news(
    company_name="Tata Elxsi",
    api_key=API_KEY,
    days=30,
    page_size=5
)

for n in news:
    print("\n---")
    print("Title:", n["title"])
    print("Source:", n["source"])
    print("Date:", n["published_at"])
    print("Summary:", n["summary"])
    print("URL:", n["url"])