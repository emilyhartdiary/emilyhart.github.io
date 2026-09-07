#!/usr/bin/env python3
"""
Generates today's photo with Pollinations.ai — free, no API key, no account.

Builds the prompt from a fixed "style bible" (so every day looks like it
belongs to the same person/account) plus a per-day scene description from
content/story.json's "image_prompt" field. If a day has no image_prompt,
falls back to a generic variation on the style bible so the pipeline never
blocks on a missing prompt.

Usage:
    python scripts/generate_image.py <day_number>

Writes docs/images/day_XXX.jpg. Skips generation (does nothing) if that file
already exists, so re-running is always safe and you can still hand-drop a
real photo into docs/images/ to override the AI one for any given day.
"""
import sys
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "docs" / "images"

# ---------------------------------------------------------------------------
# The style bible. This is what keeps 365 independently-generated images
# feeling like one consistent Instagram account instead of 365 random AI
# pictures. Based on the two reference photos: mirror/handheld phone shots,
# brunette wavy hair, dark oversized knit, gold hoop earrings, a bedroom
# with travel postcards taped up and trailing ivy, warm lamp/candle light,
# slightly grainy phone-camera look — never a clear view of the face.
# ---------------------------------------------------------------------------
STYLE_BASE = (
    "amateur iPhone selfie photo, candid and slightly grainy, natural warm "
    "lamplight, no flash, no filter, not glossy or influencer-polished. "
    "A young woman in her mid-20s with long wavy brunette hair, wearing an "
    "oversized dark knit sweater and small gold hoop earrings. Her face is "
    "always fully hidden or obscured — by her hair, by her hand, by the "
    "phone she's holding up, or because she's turned away or out of frame. "
    "Do not render any visible face, eyes, or clear facial features."
)

NEGATIVE = "visible face, clear facial features, eyes visible, studio lighting, glossy, posed model, text, watermark"

FALLBACK_SCENES = [
    "sitting on the edge of an unmade bed, holding a phone up in a mirror, "
    "postcards of London taped to the wall behind her, a trailing ivy plant",
    "close-up of her hands wrapped around a coffee mug on a wooden desk, "
    "out-of-focus fairy lights in the background",
    "standing by a rain-streaked window in a dim bedroom, back to camera",
    "a bedside table with a lit candle, an open notebook, and her phone",
]


def build_prompt(image_prompt: str | None, day: int) -> str:
    scene = image_prompt or FALLBACK_SCENES[day % len(FALLBACK_SCENES)]
    return f"{STYLE_BASE} Scene: {scene}."


def generate(day: int, image_prompt: str | None, out_path: Path, retries: int = 3) -> bool:
    if out_path.exists():
        print(f"{out_path} already exists — skipping generation.")
        return True

    prompt = build_prompt(image_prompt, day)
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1024&height=1280&seed={day}&nologo=true&model=flux"
        f"&negative={urllib.parse.quote(NEGATIVE)}"
    )

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=90)
            resp.raise_for_status()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(resp.content)
            print(f"Wrote {out_path} ({len(resp.content)} bytes)")
            return True
        except requests.RequestException as exc:
            print(f"Attempt {attempt}/{retries} failed: {exc}")
            if attempt < retries:
                time.sleep(5 * attempt)

    print(f"Giving up on generating day {day}'s image.")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_image.py <day_number> [image_prompt]")
        sys.exit(1)

    day = int(sys.argv[1])
    image_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    out_path = IMAGES_DIR / f"day_{day:03d}.jpg"

    ok = generate(day, image_prompt, out_path)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
