import os, time, requests

CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOGGER_BLOG_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    return r.json()["access_token"]

def fetch_news():
    r = requests.get(f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=us&language=en&category=top")
    return r.json().get("results", [])[:8]

def format_content(article):
    title = article.get("title", "Untitled")
    description = article.get("description") or ""
    content = article.get("content") or description
    link = article.get("link") or ""

    html = f"<h2>{title}</h2>"

    # Collect all possible image fields
    image_fields = [k for k in article.keys() if "image" in k]
    for field in image_fields:
        img = article.get(field)
        if img:
            html += f"<img src='{img}' alt='{title}' style='max-width:100%;height:auto;'/><br>"

    html += f"<p>{content}</p>"
    if link:
        html += f"<p><a href='{link}' target='_blank'>Read full article</a></p>"
    return html

def post_to_blogger(article, token):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {"Authorization": f"Bearer {token}"}
    body = {"title": article.get("title"), "content": format_content(article)}
    r = requests.post(url, headers=headers, json=body)
    if r.status_code == 429:  # rate limit
        time.sleep(5)
        return post_to_blogger(article, token)
    print("✅" if r.ok else f"❌ {r.text}", "-", article.get("title"))

def main():
    token = get_access_token()
    for article in fetch_news():
        post_to_blogger(article, token)
        time.sleep(2)  # throttle requests

if __name__ == "__main__":
    main()
