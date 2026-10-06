# Poster Master Bot

This GitHub Actions bot fetches 8 daily gaming news articles from NewsData.io and publishes them to Blogger automatically.

## Features
- Runs once per day (6 AM UTC)
- Posts 8 news articles with images
- Uses secure GitHub Secrets for API keys and Blogger credentials

## Setup
1. Add secrets in GitHub:
   - BLOGGER_CLIENT_ID
   - BLOGGER_CLIENT_SECRET
   - BLOGGER_REFRESH_TOKEN
   - BLOGGER_BLOG_ID
   - NEWS_API_KEY
2. Push workflow and script to repo.
3. GitHub Actions will run daily and publish posts.
