# The Girl in the Mirror — daily publisher

A zero-cost pipeline that publishes one diary entry + one photo per day,
for a story that runs a year, and cross-posts the same photo to Instagram.
No Ghost, no trial, no monthly bill.

## The free stack this uses

| Piece | Tool | Cost |
|---|---|---|
| Blog hosting | GitHub Pages (serves the `docs/` folder) | $0 forever |
| Scheduling | GitHub Actions (cron, once a day) | $0 (public repo = unlimited; private repo = 2,000 min/month free, this uses ~1 min/day) |
| Daily photo | Pollinations.ai image generation | $0, no key, no account |
| Instagram posting | Instagram Graph API — Business Login for Instagram | $0, no app review needed for posting to your own account |
| Story data | A single `content/story.json` file | $0 |

Only optional cost: a custom domain (~$10–15/year) if you don't want to use
the free `you.github.io/repo-name` address. Not required to launch.

When the blog is actually earning, *then* it's worth revisiting Ghost —
either Ghost(Pro) hosting, or self-hosting the open-source Ghost software
for free on something like Oracle Cloud's Always Free tier for the
membership/paywall features this setup doesn't try to replace.

## How it works

1. `content/story.json` holds every day of the story: title, HTML body,
   Instagram caption, an `image_prompt` describing that day's scene, and
   which image file goes with it.
2. Every day, GitHub Actions runs the pipeline in **two steps**, because
   Instagram fetches the image from your *live* site — it has to already be
   deployed before Instagram can see it:
   - **Step 1 — `daily_publish.py build`**: if today's image doesn't exist
     yet, generates it with `generate_image.py` (Pollinations.ai, using a
     fixed "style bible" + that day's `image_prompt` so every day looks like
     it belongs to the same account). Renders the day's HTML page, rebuilds
     `docs/index.html`, commits, and pushes — which triggers the Pages
     deployment.
   - **The workflow then polls the GitHub Pages API** until the new
     deployment reports `built`.
   - **Step 2 — `daily_publish.py instagram`**: now that the image is
     actually live, posts it + the caption to Instagram, marks the day
     `"published": true`, commits, and pushes again.
3. GitHub Pages serves whatever's in `docs/` — no build step, no server.

### The image style

`scripts/generate_image.py` has a `STYLE_BASE` constant — the fixed
description (hair, sweater, always-hidden face, room, lighting) that gets
prepended to every day's `image_prompt` so the 365 generated photos read as
one consistent account rather than 365 unrelated AI images. It's written to
match the two reference photos of the mirror-selfie / hand-over-face look.
Tweak `STYLE_BASE` once, early on, rather than fixing it per-day later.

You can always override the AI image for any specific day: just drop a real
file at `docs/images/day_XXX.jpg` before that day runs, and the script skips
generation and uses yours instead — useful if a generated photo comes out
looking wrong and you want to hand-fix just that one day.

### A practical note on AI-generated photos

Meta's Instagram policy asks accounts to disclose when photorealistic
content is AI-generated (it can add an "AI info" label automatically, or you
can add it in the caption). Worth doing here regardless of the policy —
`content/story.json` already tags every post `"tier"` and the homepage
tagline says the diary and photos are fictional/AI-generated; keep that
visible rather than relying only on the fine print.

## One-time setup

### 1. The blog

- Create a new **public** GitHub repo and push this project into it.
  (Public repos get unlimited free Actions minutes — a private repo works
  fine too, this workflow uses well under the 2,000 free minutes/month.)
- In the repo, go to **Settings → Pages → Build and deployment → Deploy from
  a branch**, and pick `main` / `docs`.
- Your site is now live at `https://YOUR-USERNAME.github.io/YOUR-REPO`.
- Copy `config.example.json` to `config.json` and set:
  - `start_date`: the date day 1 should go out (`YYYY-MM-DD`).
  - `site_base_url`: your live Pages URL from above.

### 2. Instagram

1. Convert the Instagram account to a **Professional (Business or Creator)**
   account — in the Instagram app, Settings → Account type. Free.
2. Create a Meta developer app at [developers.facebook.com](https://developers.facebook.com/)
   (free) and add the **"Instagram API setup with Instagram Login"** product.
   This path does **not** require linking a Facebook Page.
3. Under that product, run through **Business Login for Instagram** using
   your own Instagram account. This gives you:
   - Your **Instagram User ID** (`IG_USER_ID`)
   - A **long-lived access token** (`IG_ACCESS_TOKEN`, valid ~60 days)
4. Because you're only publishing to your *own* account, this stays in
   Standard Access — no Meta App Review needed, and no waiting period.
5. In your GitHub repo, go to **Settings → Secrets and variables → Actions**
   and add `IG_USER_ID` and `IG_ACCESS_TOKEN` as repository secrets.

Optional but recommended: add the `GH_PAT` secret (a personal access token
with `repo` scope) so `.github/workflows/refresh-ig-token.yml` can rotate
`IG_ACCESS_TOKEN` automatically every two weeks. Otherwise, refresh it by
hand before day 60.

### 3. The content

- `scripts/scaffold_story.py` builds `content/story.json`. It already has
  the first 20 days from your outline — day 1 fully written, days 2–20 with
  titles and `image_prompt`s but bodies still `TODO`. Add more days into the
  `SEED_POSTS` dict (title, `body_html`, `instagram_caption`, `image_prompt`)
  and re-run the script; it never touches a day already marked `published`.
- Images are generated automatically the day they're needed — you don't
  have to pre-make them. Writing a good one-line `image_prompt` per day
  (what she's doing, where, what's in the room) is the main manual work
  left; the `STYLE_BASE` in `generate_image.py` handles the rest.
- `day_001.jpg` (published on day 1) is the one exception: since day 1 is
  already marked `published`, the pipeline won't auto-generate it for you —
  add a real image at `docs/images/day_001.jpg` before you go live, or
  briefly flip its `"published"` back to `false` and let the pipeline
  generate one for it on the first run.

### 4. Test before the year starts

```bash
pip install -r requirements.txt
cp config.example.json config.json   # set start_date to today, for testing
DRY_RUN=1 python scripts/daily_publish.py
```

`DRY_RUN=1` builds the HTML and updates `story.json` but skips the actual
Instagram call, so you can check `docs/index.html` and
`docs/posts/day-001.html` look right before going live. Once you're happy,
reset `story.json` (`python scripts/scaffold_story.py` — it's non-destructive
for unpublished days) and set the real `start_date`.

## Day-to-day

Nothing to do. The `daily-publish` workflow runs on its own every day at
08:00 UTC (edit the cron line in `.github/workflows/daily-publish.yml` to
change the time). Check the **Actions** tab occasionally, especially for
any day where the log says a post or image is missing — those are the only
cases where it stops and waits for you rather than posting.

## Later: monetization

This setup deliberately doesn't build a paywall — that's a separate piece
of work once there's an audience worth charging. The `tier` field already
sitting on each `story.json` entry (`"free"` / `"paid"`) is there so a
paid-tier gate can be added later without restructuring anything, whether
that's a lightweight Stripe Checkout gate on certain post pages, or moving
the paid tier to something like Substack or Beehiiv once you want built-in
subscriber billing without any of your own payment code.
