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

    if not url:
        return False

    if not os.path.exists(POSTED_FILE):
        return False

    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return url.strip() in f.read()


def mark_posted(url):

    if not url:
        return

    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def clean_text(text):

    if not text:
        return ""

    blocked_phrases = [
        "ONLY AVAILABLE IN PAID PLANS",
        "AVAILABLE IN PAID PLANS",
        "AVAILABLE ON PAID PLANS",
        "FULL ARTICLE AVAILABLE",
        "FULL ARTICLE AVAILABLE ON PREMIUM PLAN",
        "PREMIUM PLAN",
        "PAID PLAN",
        "PAID PLANS"
    ]

    cleaned = str(text)

    for phrase in blocked_phrases:
        cleaned = cleaned.replace(phrase, "")

    return cleaned.strip()


def fetch_news():

    articles = []

    for api_key in NEWS_API_KEYS:

        if not api_key:
            continue

        try:

            print(f"Trying API Key: {api_key[:5]}*****")

            url = (
                "https://newsdata.io/api/1/latest"
                f"?apikey={api_key}"
                "&language=en"
                "&removeduplicate=1"
            )

            r = requests.get(url, timeout=30)

            if r.status_code == 429:
                print("Quota exhausted. Switching key...")
                continue

            data = r.json()

            if data.get("status") == "error":
                continue

            for article in data.get("results", []):

                title = clean_text(
                    article.get("title", "")
                )

                description = clean_text(
                    article.get("description", "")
                )

                content = clean_text(
                    article.get("content", "")
                )

                if not description and not content:
                    print(
                        "Skipping empty article:",
                        title
                    )
                    continue

                if (
                    len(content) < 50
                    and len(description) > 50
                ):
                    content = description

                article["title"] = title
                article["description"] = description
                article["content"] = content

                articles.append(article)

            if articles:
                return articles

        except Exception as e:
            print("News API Error:", e)

    return articles


def format_content(article):

    title = article.get("title", "")

    description = article.get("description", "")

    content = article.get("content", "")

    source = article.get("source_id", "Unknown Source")

    date = article.get("pubDate", "")

    creator = article.get("creator") or []

    category = article.get("category") or []

    country = article.get("country") or []

    keywords = article.get("keywords") or []

    html = f"""
<div style="font-family:Arial,sans-serif;line-height:1.9;max-width:900px;margin:auto;">

<h1>{title}</h1>

<p>
<strong>Published:</strong> {date}<br>
<strong>Source:</strong> {source}
</p>
"""

    image_url = None

    for key in article.keys():

        if "image" in key.lower():

            image_url = article.get(key)

            if image_url:
                break

    if image_url:

        html += f"""
{image_url}
<br><br>
"""

    html += f"""
<h2>Overview</h2>

<p>{description}</p>
"""

    if content:

        html += f"""
<h2>Detailed Report</h2>

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

    link = article.get("link")

    if link:

        html += f"""
<p>
{link}
View Original Source
</a>
</p>
"""

    html += "</div>"

    return html


def post_to_blogger(article, token):

    article_url = article.get("link", "")

    if already_posted(article_url):

        print(
            "Duplicate skipped:",
            article.get("title")
        )

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

        return post_to_blogger(
            article,
            token
        )

    if r.ok:

        mark_posted(article_url)

        print(
            "✅ Posted:",
            article.get("title")
        )

    else:

        print(
            "❌ Blogger error:",
            r.text
        )


def main():

    token = get_access_token()

    articles = fetch_news()

    print(
        f"Found {len(articles)} valid articles"
    )

    for article in articles[:20]:

        try:

            post_to_blogger(
                article,
                token
            )

            time.sleep(2)

        except Exception as e:

            print(
                "Posting error:",
                e
            )


if __name__ == "__main__":
    main()
