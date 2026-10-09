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

DEFAULT_IMAGE = "https://picsum.photos/1200/700"


def get_access_token():
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )

    response.raise_for_status()
    return response.json()["access_token"]


def already_posted(url):

    if not url:
        return False

    if not os.path.exists(POSTED_FILE):
        return False

    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return url.strip() in [
            x.strip() for x in f.readlines()
        ]


def mark_posted(url):

    if not url:
        return

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

    text = str(text)

    for phrase in blocked:
        text = text.replace(phrase, "")

    return text.strip()


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

            response = requests.get(
                url,
                timeout=30
            )

            if response.status_code == 429:
                print("Quota reached. Switching key...")
                continue

            data = response.json()

            if data.get("status") == "error":
                continue

            for article in data.get(
                "results",
                []
            ):

                title = clean_text(
                    article.get(
                        "title",
                        ""
                    )
                )

                description = clean_text(
                    article.get(
                        "description",
                        ""
                    )
                )

                content = clean_text(
                    article.get(
                        "content",
                        ""
                    )
                )

                if not description and not content:
                    print(
                        f"Skipping empty article: {title}"
                    )
                    continue

                if len(content) < 50:
                    content = description

                article["title"] = title
                article["description"] = description
                article["content"] = content

                articles.append(article)

            if articles:
                return articles

        except Exception as e:

            print(
                f"API Error: {e}"
            )

    return articles


def format_content(article):

    title = article.get("title", "")
    description = article.get("description", "")
    content = article.get("content", "")

    source = article.get(
        "source_id",
        "Unknown Source"
    )

    pub_date = article.get(
        "pubDate",
        ""
    )

    image_url = (
        article.get("image_url")
        or article.get("image")
        or article.get("imageUrl")
        or article.get("photo_url")
        or article.get("thumbnail")
        or DEFAULT_IMAGE
    )

    author = article.get(
        "creator",
        []
    )

    category = article.get(
        "category",
        []
    )

    country = article.get(
        "country",
        []
    )

    keywords = article.get(
        "keywords",
        []
    )

    link = article.get(
        "link",
        ""
    )

    html = f"""
<div style="font-family:Arial,sans-serif;max-width:900px;margin:auto;line-height:1.8">

<h1>{title}</h1>

{image_url}

<p>
<strong>Published:</strong> {pub_date}<br>
<strong>Source:</strong> {source}
</p>

<h2>Overview</h2>

<p>{description}</p>

<h2>Details</h2>

<p>{content}</p>
"""

    if author:

        html += f"""
<h3>Author</h3>
<p>{', '.join(author)}</p>
"""

    if category:

        html += f"""
<h3>Category</h3>
<p>{', '.join(category)}</p>
"""

    if country:

        html += f"""
<h3>Country</h3>
<p>{', '.join(country)}</p>
"""

    if keywords:

        html += "<h3>Keywords</h3><ul>"

        for keyword in keywords:
            html += f"<li>{keyword}</li>"

        html += "</ul>"

    if link:

        html += f"""
<p>
{link}
Read Original Source
</a>
</p>
"""

    html += "</div>"

    return html


def post_to_blogger(article, token):

    article_url = article.get(
        "link",
        ""
    )

    if already_posted(article_url):

        print(
            f"Duplicate skipped: {article.get('title')}"
        )

        return

    url = (
        "https://www.googleapis.com/blogger/v3/blogs/"
        f"{BLOG_ID}/posts/"
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    body = {
        "title": article.get("title"),
        "content": format_content(article)
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code == 429:

        time.sleep(5)

        return post_to_blogger(
            article,
            token
        )

    if response.ok:

        mark_posted(article_url)

        print(
            f"✅ Posted: {article.get('title')}"
        )

    else:

        print(
            f"❌ Failed: {response.text}"
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
                f"Posting Error: {e}"
            )


if __name__ == "__main__":
    main()
