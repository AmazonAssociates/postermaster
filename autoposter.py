import os
import time
import requests

CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOGGER_BLOG_ID")

NEWS_API_KEYS = [
    os.getenv("NEWS_API_KEY"),
    os.getenv("NEWS_API_KEY1")
]

POSTED_FILE = "posted_urls.txt"


def get_access_token():

    r = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )

    r.raise_for_status()

    return r.json()["access_token"]


def already_posted(url):

    if not os.path.exists(POSTED_FILE):
        return False

    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return url in f.read()


def mark_posted(url):

    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def clean_text(text):

    if not text:
        return ""

    blocked = [
        "ONLY AVAILABLE IN PAID PLANS",
        "AVAILABLE IN PAID PLANS",
        "AVAILABLE ON PAID PLANS",
        "FULL ARTICLE AVAILABLE",
        "FULL ARTICLE AVAILABLE ON PREMIUM PLAN",
        "PREMIUM PLAN",
        "PAID PLAN",
        "PAID PLANS"
    ]

    for item in blocked:
        text = text.replace(item, "")

    return text.strip()


def is_premium_article(article):

    combined = (
        str(article.get("title", ""))
        + " "
        + str(article.get("description", ""))
        + " "
        + str(article.get("content", ""))
    ).lower()

    blocked = [
        "paid plan",
        "paid plans",
        "premium plan",
        "full article available",
        "only available in paid plans"
    ]

    return any(word in combined for word in blocked)


def fetch_news():

    all_articles = []

    for api_key in NEWS_API_KEYS:

        if not api_key:
            continue

        try:

            print(f"Using API Key: {api_key[:6]}******")

            url = (
                "https://newsdata.io/api/1/news"
                f"?apikey={api_key}"
                "&country=us"
                "&language=en"
            )

            r = requests.get(url, timeout=20)

            if r.status_code == 429:
                print("Quota exhausted. Switching API...")
                continue

            data = r.json()

            if data.get("status") == "error":
                continue

            for article in data.get("results", []):

                if is_premium_article(article):
                    print(
                        "Skipping premium article:",
                        article.get("title")
                    )
                    continue

                description = clean_text(
                    article.get("description", "")
                )

                content = clean_text(
                    article.get("content", "")
                )

                if len(description) < 80 and len(content) < 80:
                    print(
                        "Skipping weak article:",
                        article.get("title")
                    )
                    continue

                all_articles.append(article)

            if all_articles:
                return all_articles

        except Exception as e:
            print("API Error:", e)

    return []


def format_content(article):

    title = article.get("title", "")

    description = clean_text(
        article.get("description", "")
    )

    content = clean_text(
        article.get("content", "")
    )

    source = article.get("source_id", "")
    link = article.get("link", "")
    date = article.get("pubDate", "")

    creator = article.get("creator", [])
    category = article.get("category", [])
    country = article.get("country", [])
    keywords = article.get("keywords", [])

    html = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.8;max-width:900px;margin:auto;">

    <h1>{title}</h1>

    <p>
    <strong>Published:</strong> {date}<br>
    <strong>Source:</strong> {source}
    </p>
    """

    image_fields = [
        key
        for key in article.keys()
        if "image" in key.lower()
    ]

    for field in image_fields:

        image_url = article.get(field)

        if image_url:

            html += f"""
            {image_url}
            <br><br>
            """

            break

    html += f"""
    <h2>Overview</h2>
    <p>{description}</p>
    """

    if content and len(content) > 50:

        html += f"""
        <h2>Details</h2>
        <p>{content}</p>
        """

    if creator:

        html += f"""
        <h3>Author</h3>
        <p>{", ".join(creator)}</p>
        """

    if category:

        html += f"""
        <h3>Category</h3>
        <p>{", ".join(category)}</p>
        """

    if country:

        html += f"""
        <h3>Country</h3>
        <p>{", ".join(country)}</p>
        """

    if keywords:

        html += "<h3>Keywords</h3><ul>"

        for kw in keywords:
            html += f"<li>{kw}</li>"

        html += "</ul>"

    if link:

        html += f"""
        <p>
        {link}
        Original Source
        </a>
        </p>
        """

    html += "</div>"

    return html


def post_to_blogger(article, token):

    link = article.get("link", "")

    if link and already_posted(link):

        print(
            "Already posted:",
  
