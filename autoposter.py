import os
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOGGER_BLOG_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Authenticate Blogger API
creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token"
)
service = build("blogger", "v3", credentials=creds)

def fetch_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=gaming&language=en&page=1"
    try:
        response = requests.get(url, timeout=10).json()
        articles = response.get("results")
        if isinstance(articles, list):
            return articles[:8]
        else:
            print("⚠️ No articles found or API returned unexpected format.")
            return []
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

def post_to_blogger(article):
    try:
        title = article.get("title", "Untitled")
        description = article.get("description", "")
        link = article.get("link", "")
        image = article.get("image_url", "")

        content = f"""
        <h2>{title}</h2>
        <p>{description}</p>
        <p><a href="{link}">Read more</a></p>
        """
        if image:
            content = f'<img src="{image}" alt="News Image" style="max-width:100%;"/>' + content

        post = {
            "kind": "blogger#post",
            "title": title,
            "content": content
        }
        service.posts().insert(blogId=BLOG_ID, body=post).execute()
        print(f"✅ Posted: {title}")
    except Exception as e:
        print(f"❌ Failed to post article: {e}")

if __name__ == "__main__":
    articles = fetch_news()
    if articles:
        for article in articles:
            post_to_blogger(article)
    else:
        print("⚠️ No articles to post today.")
