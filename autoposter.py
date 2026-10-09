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
        return url.strip() in [x.strip() for x in f.readlines()]


def mark_posted(url):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def contains_premium_text(article):

    text = " ".join([
        str(article.get("title", "")),
        str(article.get("description", "")),
        str(article.get("content", ""))
    ]).lower()

    blocked = [
        "only available in paid plans",
        "available in paid plans",
        "available on paid plans",
        "full article available",
        "premium plan",
        "paid plan",
        "paid plans"
    ]

    return any(x in text for x in blocked)


def fetch_news():

    valid_articles = []

    for api_key in NEWS_API_KEYS:

        if not api_key:
            continue

        try:

            print(f"Trying API key: {api_key[:5]}*****")

            url = (
                "https://newsdata.io/api/1/news"
                f"?apikey={api_key}"
                "&language=en"
                "&country=us"
            )

            r = requests.get(url, timeout=30)

            if r.status_code == 429:
                print("Quota reached, switching key...")
                continue

            data = r.json()

            for article in data.get("results", []):

                if contains_premium_text(article):
                    print(
                        "Skipped premium article:",
                        article.get("title")
                    )
                    continue

                description = article.get("description", "") or ""
                content = article.get("content", "") or ""

                if len(description) < 40 and len(content) < 40:
                    print(
                        "Skipped weak article:",
                        article.get("title")
                    )
                    continue

                valid_articles.append(article)

            if valid_articles:
                return valid_articles

        except Exception as e:
            print("API Error:", e)

    return valid_articles


def format_content(article):

    title = article.get("title", "")
    description = article.get("description", "") or ""
    content = article.get("content", "") or ""

    source = article.get("source_id", "")
    published = article.get("pubDate", "")
    link = article.get("link", "")

    creator = article.get("creator", [])
    category = article.get("category", [])
    country = article.get("country", [])
    keywords = article.get("keywords", [])

    html = f"""
<div style="font-family:Arial,sans-serif;line-height:1.8;max-width:900px;margin:auto;">

<h1>{title}</h1>

<p>
<b>Published:</b> {published}<br>
<b>Source:</b> {source}
</p>
"""

    for key in article.keys():

        if "image" in key.lower():

            image_url = article.get(key)

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

    if content:

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
View Original Source
</a>
</p>
"""

    html += """
</div>
"""

    return html


def post_to_blogger(article, token):

    article_url = article.get("link", "")

    if article_url and already_posted(article_url):
        print("Duplicate skipped:", article.get("title"))
        return

    url = (
        f"https://www.googleapis.com/blogger/v3/blogs/"
        f"{BLOG_ID}/posts/"
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    body = {
        "title": article.get("title"),
        "content": format_content(article)
    }

    r = requests.post(
        url,
        headers=headers,
        json=body
    )

    if r.status_code == 429:
        time.sleep(5)
        return post_to_blogger(article, token)

    if r.ok:

        if article_url:
            mark_posted(article_url)

        print("✅ Posted:", article.get("title"))

    else:
        print("❌ Failed:", r.text)


def main():

    token = get_access_token()

    articles = fetch_news()

    print(f"Found {len(articles)} valid articles")

    for article in articles[:20]:

        try:
            post_to_blogger(article, token)
            time.sleep(2)

        except Exception as e:
            print("Posting error:", e)


if __name__ == "__main__":
    main()
