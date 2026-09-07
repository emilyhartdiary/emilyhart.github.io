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
      Does NOT touch Instagram and does NOT mark the day published.

  python scripts/daily_publish.py instagram
      Re-reads today's day, checks that the image is publicly accessible,
      publishes its image + caption to Instagram, then marks it
      "published": true in story.json.

Run automatically by .github/workflows/daily-publish.yml, which runs
`build`, commits + pushes, waits for the Pages deployment to finish,
then runs `instagram` and commits + pushes again.

Environment variables used:
  SITE_BASE_URL
      e.g. https://yourname.github.io/girl-in-the-mirror
      Must be the LIVE public URL — Instagram fetches the image from here.

  IG_USER_ID
      Instagram professional account's numeric user id.

  IG_ACCESS_TOKEN
      Long-lived Instagram User access token.

  DRY_RUN
      Set to "1" to skip the actual Instagram API calls.
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
<header>
<h1>The Girl in the Mirror</h1>
<p class="tagline">
Emily Hart is a fictional character. This is a fictional diary.
Photos are AI-generated.
</p>
</header>
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
</article>
"""


def excerpt_from_html(body_html: str, max_chars: int = 160) -> str:
    """Convert HTML body into a short plain-text excerpt."""

    text = re.sub(r"<[^>]+>", " ", body_html)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"

    return html.escape(text)


def load_config() -> dict:
    """Load config.json."""

    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_story() -> list:
    """Load story.json."""

    with open(STORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_story(days: list):
    """Save story.json."""

    with open(STORY_PATH, "w", encoding="utf-8") as f:
        json.dump(days, f, ensure_ascii=False, indent=2)


def day_number_for_today(start_date_str: str) -> int:
    """
    Calculate today's story day number.

    Uses UTC because GitHub Actions normally runs in UTC.
    """

    start = date.fromisoformat(start_date_str)
    today = datetime.now(timezone.utc).date()

    return (today - start).days + 1


def get_today_entry(days: list, day_number: int) -> dict:
    """Find and validate today's story entry."""

    entry = next(
        (d for d in days if d["day"] == day_number),
        None,
    )

    if entry is None:
        print(
            f"No story entry for day {day_number} "
            f"(story only has {len(days)} days). Nothing to do."
        )
        sys.exit(0)

    if (
        entry["title"].startswith("TODO")
        or "TODO" in entry.get("body_html", "")
    ):
        print(
            f"Day {day_number} ('{entry['title']}') "
            "hasn't been fully written yet in content/story.json."
        )
        sys.exit(1)

    return entry


def write_post_html(entry: dict, published_date: str):
    """Write the individual blog post HTML file."""

    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    slug = f"day-{entry['day']:03d}"

    html_content = POST_TEMPLATE.format(
        title=entry["title"],
        date=published_date,
        image_file=entry["image_file"],
        body_html=entry["body_html"],
    )

    path = POSTS_DIR / f"{slug}.html"

    path.write_text(
        html_content,
        encoding="utf-8",
    )

    print(f"Wrote {path}")


def rebuild_index(
    days: list,
    up_to_day: int,
    start_date_str: str,
):
    """
    Rebuild index.html.

    Include today's day even before it is marked published, so the site
    goes live with today's image BEFORE Instagram tries to fetch it.
    """

    visible = [
        d
        for d in days
        if d.get("published") or d["day"] == up_to_day
    ]

    visible.sort(
        key=lambda d: d["day"],
        reverse=True,
    )

    start = date.fromisoformat(start_date_str)

    cards = []

    for d in visible:
        post_date = (
            start + timedelta(days=d["day"] - 1)
        ).isoformat()

        cards.append(
            CARD_TEMPLATE.format(
                day=d["day"],
                image_file=d["image_file"],
                title=d["title"],
                date=post_date,
                excerpt=excerpt_from_html(
                    d["body_html"]
                ),
            )
        )

    index_content = INDEX_TEMPLATE.format(
        entries="\n".join(cards)
        or '<p class="meta">Nothing published yet.</p>'
    )

    index_path = DOCS_DIR / "index.html"

    index_path.write_text(
        index_content,
        encoding="utf-8",
    )

    print(
        f"Rebuilt index.html with {len(visible)} posts."
    )


def cmd_build():
    """Build today's post and image."""

    config = load_config()

    day_number = day_number_for_today(
        config["start_date"]
    )

    days = load_story()

    entry = get_today_entry(
        days,
        day_number,
    )

    if entry.get("published"):
        print(
            f"Day {day_number} was already published. "
            "Nothing to build."
        )
        return

    image_path = (
        DOCS_DIR
        / "images"
        / entry["image_file"]
    )

    if not image_path.exists():
        print(
            f"No image yet for day {day_number} "
            "— generating one."
        )

        ok = generate_image.generate(
            day_number,
            entry.get("image_prompt"),
            image_path,
        )

        if not ok:
            print(
                "Image generation failed. "
                "Not publishing today."
            )
            sys.exit(1)

    published_date = (
        datetime.now(timezone.utc)
        .date()
        .isoformat()
    )

    write_post_html(
        entry,
        published_date,
    )

    rebuild_index(
        days,
        day_number,
        config["start_date"],
    )

    print(
        f"Build done for day {day_number}. "
        "Commit + push, then run 'instagram' once "
        "Pages has redeployed."
    )


def check_image_url(image_url: str) -> bool:
    """
    Check that the image is publicly accessible.

    Instagram needs to be able to fetch the image itself.
    """

    print()
    print("Checking image URL before contacting Instagram...")
    print(f"Image URL: {image_url}")

    try:
        response = requests.get(
            image_url,
            timeout=30,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        print(
            "ERROR: Could not access image URL."
        )
        print(f"Reason: {exc}")
        return False

    print(
        f"Image URL response: HTTP {response.status_code}"
    )

    print(
        "Final URL: "
        f"{response.url}"
    )

    content_type = response.headers.get(
        "content-type",
        "",
    )

    print(
        f"Content-Type: {content_type}"
    )

    print(
        f"Image size: {len(response.content)} bytes"
    )

    if response.status_code != 200:
        print()
        print(
            "ERROR: The image URL is not publicly "
            "accessible."
        )
        print(
            "Instagram will not be able to fetch "
            "this image."
        )
        return False

    if not content_type.lower().startswith(
        "image/"
    ):
        print()
        print(
            "ERROR: The URL returned something that "
            "does not appear to be an image."
        )
        print(
            f"Content-Type was: {content_type}"
        )
        return False

    if len(response.content) == 0:
        print()
        print(
            "ERROR: The image URL returned an empty "
            "response."
        )
        return False

    print("Image URL looks good.")

    return True


def print_instagram_error(response: requests.Response):
    """Print useful information from an Instagram API error."""

    print()
    print("=" * 60)
    print("INSTAGRAM API ERROR")
    print("=" * 60)

    print(
        f"HTTP status: {response.status_code}"
    )

    print(
        f"URL: {response.url}"
    )

    print()
    print("Response from Instagram:")
    print(response.text)

    print("=" * 60)
    print()


def cmd_instagram():
    """Publish today's entry to Instagram."""

    config = load_config()

    day_number = day_number_for_today(
        config["start_date"]
    )

    days = load_story()

    entry = get_today_entry(
        days,
        day_number,
    )

    if entry.get("published"):
        print(
            f"Day {day_number} was already published. "
            "Skipping."
        )
        return

    # ---------------------------------------------------------
    # DRY RUN
    # ---------------------------------------------------------

    if os.environ.get("DRY_RUN") == "1":
        print(
            "DRY_RUN=1 — skipping the actual "
            "Instagram API calls."
        )
        print(
            "The post will NOT be marked as published."
        )
        return

    # ---------------------------------------------------------
    # ENVIRONMENT VARIABLES
    # ---------------------------------------------------------

    ig_user_id = os.environ.get(
        "IG_USER_ID"
    )

    access_token = os.environ.get(
        "IG_ACCESS_TOKEN"
    )

    if not ig_user_id:
        print(
            "ERROR: IG_USER_ID is not set."
        )
        sys.exit(1)

    if not access_token:
        print(
            "ERROR: IG_ACCESS_TOKEN is not set."
        )
        sys.exit(1)

    # ---------------------------------------------------------
    # IMAGE URL
    # ---------------------------------------------------------

    site_base_url = config.get(
        "site_base_url"
    )

    if not site_base_url:
        print(
            "ERROR: site_base_url is missing "
            "from config.json."
        )
        sys.exit(1)

    image_url = (
        f"{site_base_url.rstrip('/')}"
        f"/images/{entry['image_file']}"
    )

    caption = (
        entry.get("instagram_caption")
        or entry["title"]
    )

    print()
    print("=" * 60)
    print("INSTAGRAM PUBLISH")
    print("=" * 60)

    print(
        f"Day: {day_number}"
    )

    print(
        f"Title: {entry['title']}"
    )

    print(
        f"Image URL: {image_url}"
    )

    print(
        f"Caption: {caption}"
    )

    print(
        f"Instagram User ID: {ig_user_id}"
    )

    print("=" * 60)
    print()

    # ---------------------------------------------------------
    # CHECK THAT INSTAGRAM CAN PROBABLY FETCH THE IMAGE
    # ---------------------------------------------------------

    if not check_image_url(image_url):
        print(
            "Stopping before Instagram API call."
        )
        sys.exit(1)

    # ---------------------------------------------------------
    # STEP 1 — CREATE INSTAGRAM MEDIA CONTAINER
    # ---------------------------------------------------------

    media_url = (
        f"https://graph.instagram.com/"
        f"{GRAPH_API_VERSION}/"
        f"{ig_user_id}/media"
    )

    print()
    print(
        "Creating Instagram media container..."
    )

    try:
        create_resp = requests.post(
            media_url,
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token,
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        print()
        print(
            "ERROR: Could not connect to "
            "Instagram Graph API."
        )
        print(
            f"Reason: {exc}"
        )
        sys.exit(1)

    print(
        f"Instagram media response: "
        f"HTTP {create_resp.status_code}"
    )

    if not create_resp.ok:
        print_instagram_error(
            create_resp
        )
        sys.exit(1)

    print(
        "Instagram media container created."
    )

    try:
        create_data = create_resp.json()
    except ValueError:
        print(
            "ERROR: Instagram returned invalid JSON."
        )
        print(create_resp.text)
        sys.exit(1)

    creation_id = create_data.get(
        "id"
    )

    if not creation_id:
        print(
            "ERROR: Instagram response did not "
            "contain a creation ID."
        )
        print(
            "Response:"
        )
        print(create_data)
        sys.exit(1)

    print(
        f"Creation ID: {creation_id}"
    )

    # ---------------------------------------------------------
    # STEP 2 — PUBLISH MEDIA CONTAINER
    # ---------------------------------------------------------

    publish_url = (
        f"https://graph.instagram.com/"
        f"{GRAPH_API_VERSION}/"
        f"{ig_user_id}/media_publish"
    )

    print()
    print(
        "Publishing Instagram media container..."
    )

    try:
        publish_resp = requests.post(
            publish_url,
            data={
                "creation_id": creation_id,
                "access_token": access_token,
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        print()
        print(
            "ERROR: Could not connect to "
            "Instagram Graph API."
        )
        print(
            f"Reason: {exc}"
        )
        sys.exit(1)

    print(
        f"Instagram publish response: "
        f"HTTP {publish_resp.status_code}"
    )

    if not publish_resp.ok:
        print_instagram_error(
            publish_resp
        )
        sys.exit(1)

    try:
        publish_data = publish_resp.json()
    except ValueError:
        print(
            "ERROR: Instagram returned invalid JSON."
        )
        print(publish_resp.text)
        sys.exit(1)

    print()
    print(
        "Instagram published successfully:"
    )
    print(
        publish_data
    )

    # ---------------------------------------------------------
    # ONLY MARK PUBLISHED AFTER BOTH API CALLS SUCCEEDED
    # ---------------------------------------------------------

    entry["published"] = True

    save_story(days)

    print()
    print(
        f"Day {day_number} marked published."
    )


def main():
    """Command-line entry point."""

    if (
        len(sys.argv) != 2
        or sys.argv[1] not in (
            "build",
            "instagram",
        )
    ):
        print(
            "Usage: "
            "python scripts/daily_publish.py "
            "[build|instagram]"
        )
        sys.exit(1)

    commands = {
        "build": cmd_build,
        "instagram": cmd_instagram,
    }

    commands[sys.argv[1]]()


if __name__ == "__main__":
    main()
