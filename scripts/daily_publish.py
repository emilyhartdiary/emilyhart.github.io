#!/usr/bin/env python3
"""
Publishes "today's" entry from content/story.json — in two steps, because
Instagram fetches the image from the LIVE site, so the page has to already
be deployed on GitHub Pages before we can tell Instagram about it.

  python scripts/daily_publish.py build
      1. Works out which day number today is (config.json's start_date).
      2. If today's image doesn't exist yet, generates it with
         scripts/generate_image.py (Pollinations.ai, free).
      3. Writes docs/posts/day-XXX.html and rebuilds docs/index.html.
      Does NOT touch Instagram and does NOT mark the day published — that
      happens after the site has actually redeployed with the new files.

  python scripts/daily_publish.py instagram
      Re-reads today's day, publishes its (now-live) image + caption to
      Instagram, then marks it "published": true in story.json.

Run automatically by .github/workflows/daily-publish.yml, which runs `build`,
commits + pushes, waits for the Pages deployment to finish, then runs
`instagram` and commits + pushes again.

Environment variables used:
  SITE_BASE_URL   e.g. https://yourname.github.io/girl-in-the-mirror
                  (must be the LIVE public URL — Instagram fetches the image
                  from here, so the image has to already be deployed)
  IG_USER_ID      Instagram professional account's numeric user id
  IG_ACCESS_TOKEN Long-lived Instagram User access token
  DRY_RUN         set to "1" to skip the actual Instagram call
"""
import html
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

import generate_image

ROOT = Path(__file__).resolve().parent.parent
STORY_PATH = ROOT / "content" / "story.json"
CONFIG_PATH = ROOT / "config.json"
DOCS_DIR = ROOT / "docs"
POSTS_DIR = DOCS_DIR / "posts"

GRAPH_API_VERSION = "v22.0"

POST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — The Girl in the Mirror</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header><a href="../index.html">&larr; The Girl in the Mirror</a></header>
<main>
<article>
<h1>{title}</h1>
<p class="meta">{date}</p>
<img src="../images/{image_file}" alt="">
{body_html}
</article>
</main>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Girl in the Mirror</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header><h1>The Girl in the Mirror</h1>
<p class="tagline">Emily Hart is a fictional character. This is a fictional diary. Photos are AI-generated.</p></header>
<main>
<div class="post-grid">
{entries}
</div>
</main>
</body>
</html>
"""

CARD_TEMPLATE = """<article class="post-card">
<a href="posts/day-{day:03d}.html">
<img src="images/{image_file}" alt="">
<div class="post-card-body">
<h2>{title}</h2>
<p class="meta">{date}</p>
<p class="excerpt">{excerpt}</p>
</div>
</a>
</article>"""


def excerpt_from_html(body_html: str, max_chars: int = 160) -> str:
    text = re.sub(r"<[^>]+>", " ", body_html)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"
    return html.escape(text)


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_story() -> list:
    with open(STORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_story(days: list):
    with open(STORY_PATH, "w", encoding="utf-8") as f:
        json.dump(days, f, ensure_ascii=False, indent=2)


def day_number_for_today(start_date_str: str) -> int:
    start = date.fromisoformat(start_date_str)
    today = datetime.now(timezone.utc).date()
    return (today - start).days + 1


def get_today_entry(days: list, day_number: int) -> dict:
    entry = next((d for d in days if d["day"] == day_number), None)
    if entry is None:
        print(f"No story entry for day {day_number} (story only has {len(days)} days). Nothing to do.")
        sys.exit(0)
    if entry["title"].startswith("TODO") or "TODO" in entry.get("body_html", ""):
        print(f"Day {day_number} ('{entry['title']}') hasn't been fully written yet in content/story.json.")
        sys.exit(1)
    return entry


def write_post_html(entry: dict, published_date: str):
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = f"day-{entry['day']:03d}"
    html = POST_TEMPLATE.format(
        title=entry["title"],
        date=published_date,
        image_file=entry["image_file"],
        body_html=entry["body_html"],
    )
    path = POSTS_DIR / f"{slug}.html"
    path.write_text(html, encoding="utf-8")
    print(f"Wrote {path}")


def rebuild_index(days: list, up_to_day: int, start_date_str: str):
    # Include today's day even before it's marked published, so the site
    # goes live with it BEFORE we ask Instagram to fetch the image from it.
    visible = [d for d in days if d.get("published") or d["day"] == up_to_day]
    visible.sort(key=lambda d: d["day"], reverse=True)

    start = date.fromisoformat(start_date_str)
    cards = []
    for d in visible:
        post_date = (start + timedelta(days=d["day"] - 1)).isoformat()
        cards.append(CARD_TEMPLATE.format(
            day=d["day"],
            image_file=d["image_file"],
            title=d["title"],
            date=post_date,
            excerpt=excerpt_from_html(d["body_html"]),
        ))

    (DOCS_DIR / "index.html").write_text(
        INDEX_TEMPLATE.format(entries="\n".join(cards) or '<p class="meta">Nothing published yet.</p>'),
        encoding="utf-8",
    )
    print(f"Rebuilt index.html with {len(visible)} posts.")


def cmd_build():
    config = load_config()
    day_number = day_number_for_today(config["start_date"])
    days = load_story()
    entry = get_today_entry(days, day_number)

    if entry.get("published"):
        print(f"Day {day_number} was already published. Nothing to build.")
        return

    image_path = DOCS_DIR / "images" / entry["image_file"]
    if not image_path.exists():
        print(f"No image yet for day {day_number} — generating one.")
        ok = generate_image.generate(day_number, entry.get("image_prompt"), image_path)
        if not ok:
            print("Image generation failed. Not publishing today.")
            sys.exit(1)

    published_date = datetime.now(timezone.utc).date().isoformat()
    write_post_html(entry, published_date)
    rebuild_index(days, day_number, config["start_date"])
    print(f"Build done for day {day_number}. Commit + push, then run 'instagram' once Pages has redeployed.")


def cmd_instagram():
    config = load_config()
    day_number = day_number_for_today(config["start_date"])
    days = load_story()
    entry = get_today_entry(days, day_number)

    if entry.get("published"):
        print(f"Day {day_number} was already published. Skipping.")
        return

    ig_user_id = os.environ.get("IG_USER_ID")
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    if os.environ.get("DRY_RUN") == "1":
        print("DRY_RUN=1 — skipping the actual Instagram API calls.")
    elif not (ig_user_id and access_token):
        print("IG_USER_ID / IG_ACCESS_TOKEN not set — skipping Instagram publish.")
    else:
        image_url = f"{config['site_base_url'].rstrip('/')}/images/{entry['image_file']}"
        caption = entry.get("instagram_caption") or entry["title"]

        create_resp = requests.post(
            f"https://graph.instagram.com/{GRAPH_API_VERSION}/{ig_user_id}/media",
            data={"image_url": image_url, "caption": caption, "access_token": access_token},
            timeout=30,
        )
        create_resp.raise_for_status()
        creation_id = create_resp.json()["id"]

        publish_resp = requests.post(
            f"https://graph.instagram.com/{GRAPH_API_VERSION}/{ig_user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": access_token},
            timeout=30,
        )
        publish_resp.raise_for_status()
        print(f"Published to Instagram: {publish_resp.json()}")

    entry["published"] = True
    save_story(days)
    print(f"Day {day_number} marked published.")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("build", "instagram"):
        print("Usage: python scripts/daily_publish.py [build|instagram]")
        sys.exit(1)
    {"build": cmd_build, "instagram": cmd_instagram}[sys.argv[1]]()


if __name__ == "__main__":
    main()
