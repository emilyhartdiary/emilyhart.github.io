#!/usr/bin/env python3
"""
Builds (or rebuilds) content/story.json — the year-long story timeline.

Run this once at the start of the project, and again any time you want to add
more written days. It will NOT overwrite a day that's already marked
"published": true in the existing file, so it's safe to re-run.

Usage:
    python scripts/scaffold_story.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY_PATH = ROOT / "content" / "story.json"

TOTAL_DAYS = 365  # length of the story arc

# ---------------------------------------------------------------------------
# Write your posts here as you draft them. Any day not listed gets a TODO
# placeholder so you can see exactly what's left to write.
# body_html supports plain HTML (<p>, <em>, <strong>, etc.)
# ---------------------------------------------------------------------------
SEED_POSTS = {
    1: {
        "title": "I don't know why I'm writing this.",
        "body_html": (
            "<p>I've started this blog three times.</p>"
            "<p>The first time, I deleted it after twenty minutes.</p>"
            "<p>The second time, I wrote twelve pages and never published any of them.</p>"
            "<p>This is the third.</p>"
            "<p>I don't know if anyone will read this.</p>"
            "<p>Maybe that's the point.</p>"
            "<p>I'm not going to tell you my real name.</p>"
            "<p>I'm not going to show you my face.</p>"
            "<p>And there are some things I'm probably never going to tell you.</p>"
            "<p>At least not yet.</p>"
            "<p>So let's start with something easy.</p>"
            "<p>I'm twenty-four.</p>"
            "<p>I live in London.</p>"
            "<p>I drink too much coffee.</p>"
            "<p>I have a terrible habit of falling in love with people who don't love me back.</p>"
            "<p>And last Tuesday, I found something in my mother's house that I don't think "
            "I was supposed to find.</p>"
        ),
        "instagram_caption": "I don't know why I'm writing this. New post tonight. — E",
        "image_prompt": (
            "sitting at a cluttered makeup desk with a mirror, holding her phone up to take "
            "the photo, perfume bottles and brushes in front of her, postcards of European "
            "landmarks taped to the wall, a trailing ivy plant, a lit candle, warm dim light"
        ),
        "tier": "free",
    },
    2: {
        "title": "My bedroom at 2:17 AM",
        "tier": "free",
        "image_prompt": (
            "sitting on the bed at night, one hand pulling her hair across her face, phone "
            "screen glowing faintly, a window with city lights blurred behind her"
        ),
    },
    3: {
        "title": "Things I keep in my makeup drawer",
        "tier": "free",
        "image_prompt": "close-up of hands sorting through an open makeup drawer, an old photograph half-visible among the items",
    },
    4: {
        "title": "The boy on the Northern Line",
        "tier": "free",
        "image_prompt": "her reflection in a dark Tube train window at night, face hidden by hair, tunnel lights streaking past",
    },
    5: {
        "title": "Five things I never tell people about myself",
        "tier": "free",
        "image_prompt": "lying on the bed, phone held straight up overhead, face turned to the side, fairy lights on the wall behind",
    },
    6: {
        "title": "My mother doesn't know I found it",
        "tier": "free",
        "image_prompt": "hands holding an old, slightly worn photograph over a wooden table, out of focus in the background",
    },
    7: {
        "title": "A rainy Sunday in London",
        "tier": "free",
        "image_prompt": "standing at a rain-streaked window with a mug of tea, back to the camera, grey daylight",
    },
    8: {
        "title": "The photograph",
        "tier": "free",
        "image_prompt": "an old photograph propped against a lamp on a nightstand, her silhouette blurred in the background",
    },
    9: {
        "title": "I think someone is reading this",
        "tier": "free",
        "image_prompt": "sitting cross-legged on the floor with the phone held low, hair falling forward completely covering her face",
    },
    10: {
        "title": "Things I miss about being 17",
        "tier": "free",
        "image_prompt": "flipping through an old school notebook on the bed, hand covering the lower half of her face",
    },
    11: {
        "title": "The message",
        "tier": "free",
        "image_prompt": "close-up of a phone screen glowing in a dark room, her blurred hand and wrist visible, face out of frame",
    },
    12: {
        "title": "I shouldn't have answered",
        "tier": "free",
        "image_prompt": "sitting on the floor against the bed frame, knees pulled up, phone held to take the mirror photo, dim lamp light",
    },
    13: {
        "title": "Coffee with someone I haven't seen in seven years",
        "tier": "free",
        "image_prompt": "hands around a coffee cup on a café table by a window, rain outside, face out of frame",
    },
    14: {
        "title": "Why I don't show my face",
        "tier": "free",
        "image_prompt": "sitting at the mirror desk again, phone raised, hair pulled fully over her face this time, candle burning nearby",
    },
    15: {
        "title": "The room upstairs",
        "tier": "free",
        "image_prompt": "standing in a dim, dusty attic room, back to camera, holding an old box, single bare lightbulb",
    },
    16: {
        "title": "There was another photograph",
        "tier": "free",
        "image_prompt": "two old photographs laid side by side on a wooden floor, her blurred knees and hands in frame",
    },
    17: {
        "title": "I lied to you",
        "tier": "free",
        "image_prompt": "sitting on the bed with the phone lowered slightly, hair covering most of her face, softer warmer light than usual",
    },
    18: {
        "title": "His name is Daniel",
        "tier": "free",
        "image_prompt": "a folded letter and an old photograph on the nightstand beside the lit candle, her blurred shoulder in frame",
    },
    19: {
        "title": "Tomorrow I'm leaving London",
        "tier": "free",
        "image_prompt": "a half-packed suitcase on the bed, postcards being peeled off the wall, her silhouette by the window",
    },
    20: {
        "title": "Before I go",
        "tier": "free",
        "image_prompt": "standing in the doorway of the now nearly-empty bedroom, phone raised for one last mirror photo, evening light",
    },
}


def load_existing() -> dict:
    if STORY_PATH.exists():
        with open(STORY_PATH, encoding="utf-8") as f:
            return {d["day"]: d for d in json.load(f)}
    return {}


def build():
    existing = load_existing()
    days = []
    for day in range(1, TOTAL_DAYS + 1):
        if day in existing and existing[day].get("published"):
            # Never touch a day that's already gone out.
            days.append(existing[day])
            continue

        seed = SEED_POSTS.get(day, {})
        days.append({
            "day": day,
            "title": seed.get("title", f"TODO: untitled (day {day})"),
            "body_html": seed.get("body_html", "<p>TODO: write this post.</p>"),
            "instagram_caption": seed.get("instagram_caption", seed.get("title", "")),
            "image_file": f"day_{day:03d}.jpg",
            "image_prompt": seed.get("image_prompt"),
            "tier": seed.get("tier", "free"),
            "published": False,
        })

    STORY_PATH.parent.mkdir(exist_ok=True)
    with open(STORY_PATH, "w", encoding="utf-8") as f:
        json.dump(days, f, ensure_ascii=False, indent=2)
    print(f"Wrote {STORY_PATH} with {TOTAL_DAYS} days "
          f"({len(SEED_POSTS)} written, {TOTAL_DAYS - len(SEED_POSTS)} still TODO).")


if __name__ == "__main__":
    build()
