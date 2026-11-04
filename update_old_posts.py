import os
import re
import time
import requests

CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOGGER_BLOG_ID")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

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
    
    # Extract TMDB Movie ID from the existing vidsrc iframe embed URL
    match = re.search(r'vidsrc\.to/embed/movie/(\d+)', content)
    if not match:
        print(f"⚠️ Skipped post (no movie ID found): {post.get('title')}")
        return False
    
    movie_id = match.group(1)
    
    # 1. Update old APK drive links to the new link
    old_apk_pattern = r'https://drive\.google\.com/file/d/[a-zA-Z0-9_-]+/view\?usp=sharing'
    new_apk_link = "https://drive.google.com/file/d/177gxXg5zZ4USgG_3uHQNZAVNcMES4CCk/view?usp=sharing"
    updated_content = re.sub(old_apk_pattern, new_apk_link, content)
    
    # 2. Add sandbox attributes to iframe if missing
    if 'sandbox=' not in updated_content:
        updated_content = updated_content.replace(
            '<iframe src=',
            '<iframe id="filmbox-video-frame" sandbox="allow-scripts allow-same-origin allow-presentation" src='
        )
    
    # 3. Inject Paywall Modal & Timer Script if missing
    if 'filmbox-paywall-modal' not in updated_content:
        paywall_html = f"""
  <!-- PAYWALL OVERLAY MODAL -->
  <div id="filmbox-paywall-modal" style="display:none; position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(2, 6, 23, 0.95); z-index:9999; padding:20px; box-sizing:border-box; overflow-y:auto; text-align:center;">
    <div style="max-width:600px; margin:20px auto; background:linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); border:2px solid #38bdf8; border-radius:20px; padding:25px; box-shadow:0 15px 40px rgba(56,189,248,0.4);">
      <span style="background:rgba(56,189,248,0.2); color:#38bdf8; padding:5px 15px; border-radius:20px; font-size:11px; font-weight:800; text-transform:uppercase; border:1px solid #38bdf8;">⏳ Free 10-Minute Trial Ended</span>
      <h2 style="color:#ffffff; font-size:24px; margin:15px 0 10px 0; text-transform:uppercase;">Unlock Unlimited HD Streaming</h2>
      <p style="color:#94a3b8; font-size:13.5px; margin-bottom:20px;">Your free viewing window has expired. Choose a VIP Pass below to continue watching instantly!</p>
      <div style="display:flex; flex-direction:column; gap:10px; max-height:300px; overflow-y:auto; padding-right:5px;">
        <a href="https://www.paypal.com/ncp/payment/GGNT396SFSNCC" target="_blank" style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.9); border:1px solid #a855f7; padding:12px 18px; border-radius:12px; text-decoration:none;"><span style="color:#e879f9; font-weight:800; font-size:14px;">✨ Trial VIP Pass</span><span style="background:#a855f7; color:#fff; padding:6px 14px; border-radius:20px; font-weight:900; font-size:13px;">$0.10 USD</span></a>
        <a href="https://www.paypal.com/ncp/payment/NUZ4E4JMHTB92" target="_blank" style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.9); border:1px solid #38bdf8; padding:12px 18px; border-radius:12px; text-decoration:none;"><span style="color:#38bdf8; font-weight:800; font-size:14px;">🔥 Daily VIP Pass</span><span style="background:#38bdf8; color:#0f172a; padding:6px 14px; border-radius:20px; font-weight:900; font-size:13px;">$0.40 USD</span></a>
        <a href="https://www.paypal.com/ncp/payment/LMANQFKU3MMNS" target="_blank" style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.9); border:1px solid #22c55e; padding:12px 18px; border-radius:12px; text-decoration:none;"><span style="color:#4ade80; font-weight:800; font-size:14px;">⚡ Weekend VIP Pass</span><span style="background:#22c55e; color:#fff; padding:6px 14px; border-radius:20px; font-weight:900; font-size:13px;">$0.90 USD</span></a>
        <a href="https://www.paypal.com/ncp/payment/K8PHR3W33B83A" target="_blank" style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.9); border:1px solid #eab308; padding:12px 18px; border-radius:12px; text-decoration:none;"><span style="color:#facc15; font-weight:800; font-size:14px;">👑 Weekly Master VIP</span><span style="background:#eab308; color:#0f172a; padding:6px 14px; border-radius:20px; font-weight:900; font-size:13px;">$1.90 USD</span></a>
        <a href="https://www.paypal.com/ncp/payment/6JY7ZUPLGM78U" target="_blank" style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.9); border:1px solid #ec4899; padding:12px 18px; border-radius:12px; text-decoration:none;"><span style="color:#f472b6; font-weight:800; font-size:14px;">💎 Monthly VIP Pass</span><span style="background:#ec4899; color:#fff; padding:6px 14px; border-radius:20px; font-weight:900; font-size:13px;">$5.80 USD</span></a>
        <a href="https://www.paypal.com/ncp/payment/V3V43NQ97MAWC" target="_blank" style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.9); border:1px solid #06b6d4; padding:12px 18px; border-radius:12px; text-decoration:none;"><span style="color:#22d3ee; font-weight:800; font-size:14px;">🏆 Annual Diamond VIP</span><span style="background:#06b6d4; color:#0f172a; padding:6px 14px; border-radius:20px; font-weight:900; font-size:13px;">$42.30 USD</span></a>
        <a href="https://www.paypal.com/ncp/payment/EDTSB5JV9CC8G" target="_blank" style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.9); border:1px solid #f97316; padding:12px 18px; border-radius:12px; text-decoration:none;"><span style="color:#fb923c; font-weight:800; font-size:14px;">🚀 Lifetime VIP Pass</span><span style="background:#f97316; color:#fff; padding:6px 14px; border-radius:20px; font-weight:900; font-size:13px;">$76.90 USD</span></a>
      </div>
    </div>
  </div>
"""
        timer_js = f"""
<script>
  document.addEventListener("DOMContentLoaded", function() {{
    const TRIAL_DURATION = 10 * 60 * 1000;
    const storageKey = "filmbox_trial_start_{movie_id}";
    let startTime = localStorage.getItem(storageKey);
    if (!startTime) {{
      startTime = Date.now();
      localStorage.setItem(storageKey, startTime);
    }}
    function checkTrialTime() {{
      let elapsed = Date.now() - parseInt(startTime, 10);
      if (elapsed >= TRIAL_DURATION) {{
        let modal = document.getElementById("filmbox-paywall-modal");
        let frame = document.getElementById("filmbox-video-frame");
        if (modal) modal.style.display = "block";
        if (frame) frame.src = "";
      }} else {{
        setTimeout(checkTrialTime, 5000);
      }}
    }}
    checkTrialTime();
  }});
</script>
"""
        # Inject modal inside the iframe parent container
        updated_content = updated_content.replace('</iframe>', f'</iframe>{paywall_html}')
        # Append JS timer at the bottom
        updated_content += timer_js

    # Send update request to Blogger API
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "title": post["title"],
        "content": updated_content
    }
    
    res = requests.put(url, headers=headers, json=body)
    if res.ok:
        print(f"✅ Successfully updated old post: {post['title']}")
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
            time.sleep(1)
        except Exception as e:
            print(f"Error processing post {post.get('id')}: {e}")

    print(f"\n🎉 Finished! Updated {updated_count} older posts with ad blocking and paywalls.")

if __name__ == "__main__":
    main()
