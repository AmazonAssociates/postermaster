import os
import time
import requests

CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOGGER_BLOG_ID")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

POSTED_FILE = "posted_movies.txt"
DEFAULT_IMAGE = "https://picsum.photos/1200/700"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w1280"


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


def already_posted(movie_id):
    if not movie_id:
        return False
    if not os.path.exists(POSTED_FILE):
        return False

    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return str(movie_id) in [x.strip() for x in f.readlines()]


def mark_posted(movie_id):
    if not movie_id:
        return
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(str(movie_id) + "\n")


def fetch_movies():
    movies = []
    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY is missing!")
        return movies

    # Fetching trending movies from TMDB
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
    
    try:
        print("Fetching trending movies from TMDB...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        for item in results:
            movie_id = item.get("id")
            title = item.get("title") or item.get("original_title", "Unknown Title")
            overview = item.get("overview", "No overview available.")
            release_date = item.get("release_date", "Coming Soon")
            vote_average = item.get("vote_average", 0)
            
            poster_path = item.get("poster_path")
            image_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else DEFAULT_IMAGE

            movies.append({
                "id": movie_id,
                "title": title,
                "overview": overview,
                "release_date": release_date,
                "vote_average": vote_average,
                "image_url": image_url
            })
            
    except Exception as e:
        print(f"TMDB API Error: {e}")

    return movies


def format_movie_content(movie):
    title = movie["title"]
    overview = movie["overview"]
    release_date = movie["release_date"]
    vote_average = movie["vote_average"]
    image_url = movie["image_url"]
    movie_id = movie["id"]

    # Stream embed template using the TMDB ID that matches your app setup!
    stream_url = f"https://vidsrc.to/embed/movie/{movie_id}"

    html = f"""
<div style="font-family:Arial,sans-serif;max-width:900px;margin:auto;line-height:1.8">

<h1>{title}</h1>

<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 20px; display: block;" />

<p>
<strong>Release Date:</strong> {release_date}<br>
<strong>TMDB Rating:</strong> ⭐ {vote_average} / 10
</p>

<h2>Overview</h2>
<p>{overview}</p>

<h2>Watch / Stream Online</h2>
<p>Enjoy watching <strong>{title}</strong> directly below:</p>

<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; margin-bottom: 20px;">
  <iframe src="{stream_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:0; border-radius: 8px;" allowfullscreen="true"></iframe>
</div>

</div>
"""
    return html


def post_to_blogger(movie, token):
    movie_id = movie["id"]

    if already_posted(movie_id):
        print(f"Duplicate skipped: {movie['title']}")
        return False

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {"Authorization": f"Bearer {token}"}

    body = {
        "title": f"Watch {movie['title']} ({movie['release_date'][:4]}) Full Movie Online",
        "content": format_movie_content(movie)
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 429:
        print("Rate limited. Waiting...")
        time.sleep(5)
        return post_to_blogger(movie, token)

    if response.ok:
        mark_posted(movie_id)
        print(f"✅ Posted Movie: {movie['title']}")
        return True
    else:
        print(f"❌ Failed to post {movie['title']}: {response.text}")
        return False


def main():
    token = get_access_token()
    movies = fetch_movies()

    print(f"Found {len(movies)} movies from TMDB.")

    posted_count = 0
    target_posts = 8  # Post exactly 8 movies per run

    for movie in movies:
        if posted_count >= target_posts:
            break

        try:
            success = post_to_blogger(movie, token)
            if success:
                posted_count += 1
            time.sleep(2)
        except Exception as e:
            print(f"Posting Error: {e}")

    print(f"Finished! Successfully posted {posted_count} movies today.")


if __name__ == "__main__":
    main()
