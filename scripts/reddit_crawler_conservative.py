"""
Conservative pullpush.io Reddit crawler.
Use this when the default fast batch (size=100, sleep=0.5s) hits 429 or
execute_code times out.  It uses small batches, long sleeps, exponential
backoff, and writes incremental results so progress is not lost.

Typical call pattern:
    terminal(background=True, notify_on_complete=True)
    python3 /path/to/reddit_crawler_conservative.py

Then poll/wait and read the JSON outputs.
"""
import json
import os
import time
from datetime import datetime

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# ---------------------------------------------------------------------------
# CONFIGURE YOUR RUN HERE
# ---------------------------------------------------------------------------
SUBREDDITS = ["gardyn", "aerogarden", "IndoorGarden", "hydroponics"]
OUTPUT_DIR = "/workspace/reddit_community_data"
POSTS_PER_SUB = 120          # safe default; raise only if rate limit behaves
COMMENTS_PER_SUB = 150
BATCH_SIZE = 30
SLEEP_SECONDS = 5.0
RETRIES = 10
BACKOFF_BASE = 6.0
# ---------------------------------------------------------------------------

PRICE_KEYWORDS = [
    "seed", "pod", "ycube", "rockwool", "refill", "cost", "price", "pricing",
    "expensive", "cheap", "affordable", "$", "dollar", "spend", "money",
    "subscription", "replacement", "buy", "purchase", "value",
]

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_with_retry(url, params, retries=RETRIES, base_delay=BACKOFF_BASE):
    """GET with exponential backoff on 429 or transient errors."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=40)
            if r.status_code == 429:
                wait = base_delay * (2 ** attempt) + (attempt * 3)
                print(f"    429, retry in {wait:.1f}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            wait = base_delay * (2 ** attempt)
            print(f"    error {e}, retry in {wait:.1f}s")
            time.sleep(wait)
    raise Exception(f"Failed after {retries} retries: {params}")


def fetch_submissions(sub, total=POSTS_PER_SUB):
    all_posts = []
    before = None
    remaining = total
    while remaining > 0:
        size = min(BATCH_SIZE, remaining)
        params = {"subreddit": sub, "size": size, "sort": "desc"}
        if before:
            params["before"] = before
        r = get_with_retry(
            "https://api.pullpush.io/reddit/search/submission/", params
        )
        data = r.json().get("data", [])
        if not data:
            break
        all_posts.extend(data)
        before = min(p["created_utc"] for p in data)
        remaining -= len(data)
        time.sleep(SLEEP_SECONDS)
    return all_posts


def fetch_comments(sub, total=COMMENTS_PER_SUB):
    all_comments = []
    before = None
    remaining = total
    while remaining > 0:
        size = min(BATCH_SIZE, remaining)
        params = {"subreddit": sub, "size": size, "sort": "desc"}
        if before:
            params["before"] = before
        r = get_with_retry(
            "https://api.pullpush.io/reddit/search/comment/", params
        )
        data = r.json().get("data", [])
        if not data:
            break
        all_comments.extend(data)
        before = min(c["created_utc"] for c in data)
        remaining -= len(data)
        time.sleep(SLEEP_SECONDS)
    return all_comments


def is_price_related(text):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in PRICE_KEYWORDS)


def save_state(posts, comments, filename):
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(posts if "posts" in filename else comments, f, ensure_ascii=False, indent=2)


def main():
    all_posts = []
    all_comments = []

    for sub in SUBREDDITS:
        print(f"Fetching r/{sub}...")
        posts = fetch_submissions(sub)
        time.sleep(SLEEP_SECONDS + 1)
        comments = fetch_comments(sub)
        print(f"  posts={len(posts)}, comments={len(comments)}")
        all_posts.extend(posts)
        all_comments.extend(comments)
        # Write incremental checkpoint after each subreddit
        save_state(all_posts, all_comments, "raw_posts.json")
        save_state(all_posts, all_comments, "raw_comments.json")
        time.sleep(SLEEP_SECONDS + 1)

    price_posts = [
        p for p in all_posts
        if is_price_related(p.get("title", "") + " " + p.get("selftext", ""))
    ]
    price_comments = [
        c for c in all_comments
        if is_price_related(c.get("body", ""))
    ]

    with open(os.path.join(OUTPUT_DIR, "price_posts.json"), "w", encoding="utf-8") as f:
        json.dump(price_posts, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT_DIR, "price_comments.json"), "w", encoding="utf-8") as f:
        json.dump(price_comments, f, ensure_ascii=False, indent=2)

    print(f"\nTotal posts: {len(all_posts)}")
    print(f"Price-related posts: {len(price_posts)}")
    print(f"Total comments: {len(all_comments)}")
    print(f"Price-related comments: {len(price_comments)}")
    print(f"Saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
