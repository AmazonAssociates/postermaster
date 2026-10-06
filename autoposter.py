import os
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load secrets from GitHub Actions environment
CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOGGER_BLOG_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Authenticate Blogger API using refresh token
creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token"
)
service = build("blogger", "v3", credentials=creds)

def fetch_news():
    """Fetch 8 latest breaking news articles from NewsData.io"""
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q=*&language=en"
    try:
        response = requests.get(url, timeout=10).json()
        articles = response.get("results")

        if isinstance(articles, list) and len(articles) > 0:
            return articles[:8]  # Limit to 8 articles
        else:
            print("⚠️ No breaking news found in NewsData.io response.")
            print("Full response:", response)  # Debug log
            return []
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

def post_to_blogger(article):
    """Post a single article to Blogger"""
    try:
        title = article.get("title", "Untitled")
        description = article.get("description", "")
        link = article.get("link", "")
        image = article.get("image_url", "")

        # Build HTML content
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
        print(f"❌ Failed to post article '{article.get('title', 'Untitled')}': {e}")

if __name__ == "__main__":
    articles = fetch_news()
    if articles:
        for article in articles:
            post_to_blogger(article)
    else:
        print("⚠️ No articles to post today.")
