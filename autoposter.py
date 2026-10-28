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

# All Official Links & Platforms (Updated APK Link)
APK_DRIVE_LINK = "https://drive.google.com/uc?export=download&id=1Zy569gvAUDnCjpKLin2o--Ehq4j-8X9N"
WHATSAPP_LINK = "https://chat.whatsapp.com/L02vNHjowvW83MLbJVqIwC?s=cl&p=a&mlu=4&ilr=4"
FB_PAGE_LINK = "https://www.facebook.com/profile.php?id=61595278122419"
FB_GROUP_LINK = "https://www.facebook.com/share/g/19zsQAbGu7/"
INSTAGRAM_LINK = "https://www.instagram.com/filmboxseries?exln=cTF0dnRlZXV0MXhm"
BLOGGER_LINK = "https://filmboxproductions.blogspot.com"
PAYPAL_LINK = "https://www.paypal.com/donate?business=lomalianorman@gmail.com&currency_code=USD"


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


def fetch_movie_details(movie_id):
    """Fetch rich metadata for a specific movie from TMDB."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching movie details for ID {movie_id}: {e}")
    return {}


def fetch_movies():
    movies = []
    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY is missing!")
        return movies

    # Fetch multiple pages (1 to 3) to ensure we always have enough fresh movies
    for page in range(1, 4):
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}&page={page}"
        
        try:
            print(f"Fetching trending movies from TMDB (Page {page})...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            for item in results:
                movie_id = item.get("id")
                if not movie_id:
                    continue

                # Avoid duplicates within the fetched batch
                if any(m["id"] == movie_id for m in movies):
                    continue

                # Fetch deep detailed metadata for rich post content
                details = fetch_movie_details(movie_id)

                title = item.get("title") or item.get("original_title", "Unknown Title")
                overview = item.get("overview") or details.get("overview") or "No overview available for this cinematic release."
                release_date = item.get("release_date") or details.get("release_date") or "Coming Soon"
                vote_average = item.get("vote_average", 0)
                vote_count = details.get("vote_count", item.get("vote_count", 0))
                tagline = details.get("tagline", "")
                runtime = details.get("runtime", 0)
                budget = details.get("budget", 0)
                revenue = details.get("revenue", 0)
                status = details.get("status", "Released")
                
                genres_list = details.get("genres", [])
                genres_str = ", ".join([g.get("name", "") for g in genres_list]) if genres_list else "Cinematic, Drama, Action"

                production_companies = details.get("production_companies", [])
                companies_str = ", ".join([c.get("name", "") for c in production_companies[:3]]) if production_companies else "Independent Studios"

                poster_path = item.get("poster_path") or details.get("poster_path")
                image_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else DEFAULT_IMAGE

                movies.append({
                    "id": movie_id,
                    "title": title,
                    "overview": overview,
                    "release_date": release_date,
                    "vote_average": vote_average,
                    "vote_count": vote_count,
                    "tagline": tagline,
                    "runtime": runtime,
                    "budget": budget,
                    "revenue": revenue,
                    "status": status,
                    "genres": genres_str,
                    "companies": companies_str,
                    "image_url": image_url
                })
                
        except Exception as e:
            print(f"TMDB API Error on page {page}: {e}")

    return movies


def format_movie_content(movie):
    title = movie["title"]
    overview = movie["overview"]
    release_date = movie["release_date"]
    vote_average = movie["vote_average"]
    vote_count = movie["vote_count"]
    tagline = movie["tagline"]
    runtime = movie["runtime"]
    budget = movie["budget"]
    revenue = movie["revenue"]
    status = movie["status"]
    genres = movie["genres"]
    companies = movie["companies"]
    image_url = movie["image_url"]
    movie_id = movie["id"]

    stream_url = f"https://vidsrc.to/embed/movie/{movie_id}"

    runtime_display = f"{runtime} mins" if runtime else "Standard Feature"
    budget_display = f"${budget:,}" if budget and budget > 0 else "N/A"
    revenue_display = f"${revenue:,}" if revenue and revenue > 0 else "N/A"

    html = f"""
<div style="font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width:900px; margin:auto; line-height:1.8; color:#cbd5e1; background: radial-gradient(circle at top left, #1e1b4b 0%, #0f172a 50%, #020617 100%); padding:30px; border-radius:20px; border: 2px solid rgba(56, 189, 248, 0.4); box-shadow: 0 20px 50px rgba(0,0,0,0.8);">

<h1 style="font-size:34px; font-weight:900; text-align:center; margin-bottom:10px; text-transform:uppercase; letter-spacing:1px; background:linear-gradient(90deg, #38bdf8, #25d366, #f472b6, #fbbf24); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">{title}</h1>

{f'<p style="text-align:center; font-style:italic; color:#38bdf8; font-size:16px; margin-bottom:20px; font-weight:600;">"{tagline}"</p>' if tagline else ''}

<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 14px; margin-bottom: 25px; display: block; margin-left:auto; margin-right:auto; box-shadow: 0 12px 35px rgba(0,0,0,0.8); border: 2px solid rgba(56, 189, 248, 0.3);" />

<!-- QUICK METADATA GRID -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 25px;">
  <div style="background: rgba(15, 23, 42, 0.85); padding: 14px; border-radius: 12px; border-left: 4px solid #38bdf8; font-size: 14px; color:#cbd5e1;">
    📅 <strong>Release Date:</strong><br><span style="color:#f8fafc; font-weight:600;">{release_date}</span>
  </div>
  <div style="background: rgba(15, 23, 42, 0.85); padding: 14px; border-radius: 12px; border-left: 4px solid #fbbf24; font-size: 14px; color:#cbd5e1;">
    ⭐ <strong>TMDB Score:</strong><br><span style="color:#fbbf24; font-weight:bold;">{vote_average} / 10</span> <span style="font-size:11px; color:#94a3b8;">({vote_count} votes)</span>
  </div>
  <div style="background: rgba(15, 23, 42, 0.85); padding: 14px; border-radius: 12px; border-left: 4px solid #25d366; font-size: 14px; color:#cbd5e1;">
    ⏱️ <strong>Runtime:</strong><br><span style="color:#f8fafc; font-weight:600;">{runtime_display}</span>
  </div>
  <div style="background: rgba(15, 23, 42, 0.85); padding: 14px; border-radius: 12px; border-left: 4px solid #f472b6; font-size: 14px; color:#cbd5e1;">
    🎬 <strong>Genres:</strong><br><span style="color:#f8fafc; font-weight:600;">{genres}</span>
  </div>
</div>

<!-- DETAILED STORY OVERVIEW -->
<h2 style="color:#38bdf8; border-bottom:2px solid rgba(56,189,248,0.3); padding-bottom:8px; text-transform:uppercase; font-size:20px; margin-top:25px;">📖 Comprehensive Story Overview</h2>
<p style="font-size:16px; color:#e2e8f0; font-weight:500; line-height:1.7; background: rgba(15, 23, 42, 0.5); padding: 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">{overview}</p>

<!-- PRODUCTION & FINANCIAL STATS -->
<h2 style="color:#fbbf24; border-bottom:2px solid rgba(251,191,36,0.3); padding-bottom:8px; margin-top:35px; text-transform:uppercase; font-size:20px;">📊 Movie Specifications &amp; Production</h2>
<div style="background: rgba(15, 23, 42, 0.85); padding: 18px; border-radius: 12px; font-size: 14.5px; color:#cbd5e1; line-height: 1.6; border: 1px solid rgba(255,255,255,0.05);">
  <ul style="margin: 0; padding-left: 20px;">
    <li><strong>Production Status:</strong> <span style="color:#f8fafc;">{status}</span></li>
    <li><strong>Production Companies:</strong> <span style="color:#f8fafc;">{companies}</span></li>
    <li><strong>Production Budget:</strong> <span style="color:#f8fafc;">{budget_display}</span></li>
    <li><strong>Box Office Revenue:</strong> <span style="color:#f8fafc;">{revenue_display}</span></li>
  </ul>
</div>

<!-- STREAMING PLAYER -->
<h2 style="color:#f472b6; border-bottom:2px solid rgba(244,114,182,0.3); padding-bottom:8px; margin-top:35px; text-transform:uppercase; font-size:20px;">🍿 Watch / Stream Online in HD</h2>
<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; margin-bottom: 35px; box-shadow:0 12px 35px rgba(0,0,0,0.9); border-radius:14px; overflow:hidden; border: 2px solid rgba(244,114,182,0.4);">
  <iframe src="{stream_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:0;" allowfullscreen="true"></iframe>
</div>

<!-- HIGH GRAPHICS APP DOWNLOAD & SOCIAL HUB BANNER -->
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 35px 20px; border-radius: 20px; text-align: center; margin-top: 40px; box-shadow: 0 15px 40px rgba(56, 189, 248, 0.3); border: 2px solid #38bdf8;">
  
  <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 6px 18px; border-radius: 20px; font-size: 12px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; border: 1px solid #38bdf8; display: inline-block; margin-bottom: 15px;">
    🎬 OFFICIAL FILM BOX PLATFORM
  </span>

  <h2 style="font-size: 26px; font-weight: 900; margin: 10px 0; background: linear-gradient(90deg, #38bdf8, #25d366, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-transform: uppercase;">
    Get The Android App &amp; Join Community
  </h2>

  <p style="color: #94a3b8; font-size: 14.5px; font-weight: 600; max-width: 600px; margin: 0 auto 25px auto; line-height: 1.5;">
    Stream thousands of blockbusters in crisp HD quality, connect with fellow movie fans, and get instant release notifications!
  </p>

  <!-- APK Button -->
  <div style="margin-bottom: 25px;">
    <a href="{APK_DRIVE_LINK}" target="_blank" rel="noopener noreferrer" style="background: linear-gradient(90deg, #25d366, #128c7e); color: #ffffff; padding: 16px 36px; font-size: 17px; font-weight: 900; text-decoration: none; border-radius: 40px; display: inline-block; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 8px 25px rgba(37, 211, 102, 0.5); border: 2px solid #ffffff;">
      🚀 INSTALL FILM BOX APK
    </a>
  </div>

  <!-- Social Media & Support Grid Links -->
  <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin-top: 20px;">
    <a href="{BLOGGER_LINK}" target="_blank" rel="noopener noreferrer" style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 10px 18px; border-radius: 25px; font-size: 13px; font-weight: 800; text-decoration: none; border: 1px solid #38bdf8;">
      🌐 𝗕𝗟𝗢𝗚𝗚𝗘𝗥 𝗪𝗘𝗕𝗦𝗜𝗧𝗘
    </a>
    <a href="{FB_PAGE_LINK}" target="_blank" rel="noopener noreferrer" style="background: rgba(24, 119, 242, 0.2); color: #60a5fa; padding: 10px 18px; border-radius: 25px; font-size: 13px; font-weight: 800; text-decoration: none; border: 1px solid #1877f2;">
      📘 𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗣𝗔𝗚𝗘
    </a>
    <a href="{FB_GROUP_LINK}" target="_blank" rel="noopener noreferrer" style="background: rgba(0, 132, 255, 0.2); color: #38bdf8; padding: 10px 18px; border-radius: 25px; font-size: 13px; font-weight: 800; text-decoration: none; border: 1px solid #0084ff;">
      👥 𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗚𝗥𝗢𝗨𝗣
    </a>
    <a href="{WHATSAPP_LINK}" target="_blank" rel="noopener noreferrer" style="background: rgba(37, 211, 102, 0.2); color: #4ade80; padding: 10px 18px; border-radius: 25px; font-size: 13px; font-weight: 800; text-decoration: none; border: 1px solid #25d366;">
      💬 𝗪𝗛𝗔𝗧𝗦𝗔𝗣𝗣 𝗩𝗜𝗣
    </a>
    <a href="{INSTAGRAM_LINK}" target="_blank" rel="noopener noreferrer" style="background: rgba(225, 48, 108, 0.2); color: #f43f5e; padding: 10px 18px; border-radius: 25px; font-size: 13px; font-weight: 800; text-decoration: none; border: 1px solid #e1306c;">
      📸 𝗜𝗡𝗦𝗧𝗔𝗚𝗥𝗔𝗠
    </a>
    <a href="{PAYPAL_LINK}" target="_blank" rel="noopener noreferrer" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 10px 18px; border-radius: 25px; font-size: 13px; font-weight: 800; text-decoration: none; border: 1px solid #f59e0b;">
      ☕ 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 𝗣𝗔𝗬𝗣𝗔𝗟
    </a>
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
        "title": f"Watch {movie['title']} ({movie['release_date'][:4] if movie['release_date'] and len(movie['release_date']) >= 4 else '2026'}) Full Movie Online",
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

    print(f"Found {len(movies)} total movies from TMDB.")

    posted_count = 0
    target_posts = 10

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

    print(f"Finished! Successfully posted {posted_count} new movies today.")


if __name__ == "__main__":
    main()
