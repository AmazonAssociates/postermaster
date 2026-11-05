import os
import re
import time
import requests

CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOGGER_BLOG_ID")

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

def get_all_posts(token):
    posts = []
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?maxResults=500"
    headers = {"Authorization": f"Bearer {token}"}
    
    while url:
        response = requests.get(url, headers=headers)
        if not response.ok:
            print(f"❌ Failed to fetch posts: {response.text}")
            break
        data = response.json()
        items = data.get("items", [])
        posts.extend(items)
        
        pageToken = data.get("nextPageToken")
        if pageToken:
            url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?maxResults=500&pageToken={pageToken}"
        else:
            url = None
            
    return posts

def update_post_content(post, token):
    post_id = post["id"]
    content = post.get("content", "")
    
    # Check if it's a movie post containing the vidsrc embed
    match = re.search(r'vidsrc\.to/embed/movie/(\d+)', content)
    if not match:
        return False
    
    updated_content = content
    
    # Completely remove sandbox attribute from the iframe to fix the embedding error
    if 'sandbox=' in updated_content:
        updated_content = re.sub(r'\s+sandbox="[^"]*"', '', updated_content)
        updated_content = re.sub(r"\s+sandbox='[^']*'", '', updated_content)

    if updated_content == content:
        return False

    # Send update request to Blogger API
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "title": post["title"],
        "content": updated_content
    }
    
    res = requests.put(url, headers=headers, json=body)
    if res.ok:
        print(f"✅ Cleaned sandbox error for: {post['title']}")
        return True
    else:
        print(f"❌ Failed to update {post['title']}: {res.text}")
        return False

def main():
    token = get_access_token()
    print("Fetching published posts from Blogger...")
    posts = get_all_posts(token)
    print(f"Found {len(posts)} total published posts.")

    updated_count = 0
    for post in posts:
        try:
            if update_post_content(post, token):
                updated_count += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"Error processing post {post.get('id')}: {e}")

    print(f"\n🎉 Finished! Fixed video embeds on {updated_count} older posts.")

if __name__ == "__main__":
    main()
