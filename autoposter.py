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

# Direct Drive Link for your APK
APK_DRIVE_LINK = "https://drive.google.com/file/d/19RPdMPaflAMCujyiroh95BxDWJRoff4X/view?usp=sharing"


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

    stream_url = f"https://vidsrc.to/embed/movie/{movie_id}"

    html = f"""
<div style="font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width:900px; margin:auto; line-height:1.8; color:#e0e0e0; background-color:#0d0d11; padding:25px; border-radius:16px;">

<h1 style="color:#ffffff; font-size:32px; font-weight:800; text-align:center; margin-bottom:20px; text-transform:uppercase; letter-spacing:1px; background:linear-gradient(90deg, #00d2ff, #3a7bd5, #f700ff, #ff0055); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">{title}</h1>

<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 12px; margin-bottom: 25px; display: block; margin-left:auto; margin-right:auto; box-shadow: 0 10px 30px rgba(0,0,0,0.8); border: 1px solid rgba(255,255,255,0.1);" />

<div style="background: rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:20px; font-size:15px; border-left: 4px solid #f700ff;">
<strong>📅 Release Date:</strong> {release_date}<br>
<strong>⭐ TMDB Rating:</strong> <span style="color:#ffd700; font-weight:bold;">{vote_average} / 10</span>
</div>

<h2 style="color:#00d2ff; border-bottom:2px solid #00d2ff; padding-bottom:5px;">Overview</h2>
<p style="font-size:16px; color:#cccccc;">{overview}</p>

<h2 style="color:#f700ff; border-bottom:2px solid #f700ff; padding-bottom:5px; margin-top:30px;">Watch / Stream Online</h2>
<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; margin-bottom: 30px; box-shadow:0 8px 25px rgba(0,0,0,0.9); border-radius:12px; overflow:hidden;">
  <iframe src="{stream_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:0;" allowfullscreen="true"></iframe>
</div>

<!-- HIGH GRAPHICS FILM BOX APP INSTALL PROMO BANNER -->
<div style="background: linear-gradient(135deg, #0f0c1b 0%, #1a102f 50%, #0d1b2a 100%); padding: 30px 20px; border-radius: 20px; border: 2px solid transparent; background-clip: padding-box; position: relative; text-align: center; margin-top: 40px; box-shadow: 0 12px 40px rgba(247, 0, 255, 0.25), 0 0 20px rgba(0, 210, 255, 0.2); outline: 2px solid #f700ff;">
  
  <div style="display:inline-block; background: linear-gradient(90deg, #ff0055, #f700ff, #00d2ff, #ffd700); padding: 2px; border-radius: 50px; margin-bottom: 15px;">
    <span style="background: #0d0d11; color: #fff; padding: 6px 18px; border-radius: 50px; font-size: 13px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; display: inline-block;">
      🎬 Official Mobile App
    </span>
  </div>

  <h2 style="font-size: 28px; font-weight: 900; margin: 10px 0; background: linear-gradient(90deg, #ffd700, #ff8c00, #ff0055, #f700ff, #00d2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-transform: uppercase;">
    Experience FILM BOX App
  </h2>

  <p style="color: #dddddd; font-size: 15px; max-width: 650px; margin: 0 auto 25px auto; line-height: 1.6;">
    Stream thousands of blockbusters, watch HD releases with zero ad popups, and enjoy high-speed mobile playback natively on your Android device!
  </p>

  <a href="{APK_DRIVE_LINK}" target="_blank" rel="noopener noreferrer" style="background: linear-gradient(90deg, #ff0055 0%, #f700ff 33%, #00d2ff 66%, #00ffa3 100%); color: #ffffff; padding: 16px 36px; font-size: 18px; font-weight: 900; text-decoration: none; border-radius: 50px; display: inline-block; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 6px 25px rgba(247, 0, 255, 0.6), 0 0 15px rgba(0, 210, 255, 0.5); border: 2px solid #ffffff; transition: transform 0.2s;">
    🚀 Install FILM BOX APK
  </a>

  <div style="margin-top: 20px; font-size: 12px; color: #aaaaaa; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
    <span>✅ Fast Download</span>
    <span>•</span>
    <span>⚡ 100% Free &amp; Secure</span>
    <span>•</span>
    <span>📱 Android Compatible</span>
  </div>

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
    target_posts = 8

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
