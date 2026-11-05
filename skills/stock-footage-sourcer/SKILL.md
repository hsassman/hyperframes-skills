---
name: stock-footage-sourcer
description: Searches and downloads licensed stock video footage matching a keyword, phrase, or script line — Pexels and Pixabay APIs as the free primary sources, Storyblocks/Envato as paid fallback when free sources don't have a good match. Writes a license metadata sidecar file for every download. Use this skill whenever a task involves finding B-roll, sourcing footage for a script line, or building a shot list for a video. This skill ONLY searches licensed stock APIs — never scrape or download from YouTube, Google Images, or general web search results, even if asked, since that is a copyright/ToS violation. If the user asks to "search the internet" or "find videos anywhere" for footage, use this skill's licensed-API sources and explain the scope limitation rather than attempting a broader unlicensed search.
---

# Stock Footage Sourcer

Searches licensed stock video APIs and downloads matches, always recording
license/attribution metadata alongside each file. This is the ONLY footage
sourcing path in this pipeline — there is no scrape-the-web fallback, by
design, because that carries real copyright/ToS liability.

## Source priority

1. **Pexels API** (free, no attribution required under the Pexels License) — try first
2. **Pixabay API** (free, similar CC0-like Content License) — try second if Pexels has no good match
3. **Storyblocks / Envato Elements** (paid, requires the user's own commercial API credentials) — only use if 1 and 2 don't return a good match, and only if the user has already configured credentials for one of these; do not sign up for a new paid account on the user's behalf

## Step 1: Search

Use `scripts/search_stock.py` (bundled) to query Pexels and/or Pixabay:

```bash
python scripts/search_stock.py --query "city skyline sunset timelapse" --source pexels --per-page 10
```

Requires API keys set as environment variables:
- `PEXELS_API_KEY`
- `PIXABAY_API_KEY`
- (optional) `STORYBLOCKS_API_KEY` / `STORYBLOCKS_PRIVATE_KEY` if paid fallback is configured

If a key is missing, tell the user which one and how to get it (Pexels and
Pixabay both offer instant free API keys via their developer portals) — don't
silently skip the source.

## Step 2: Review matches before downloading

Stock API search is keyword-based, not semantic — it will not perfectly
understand a nuanced script line. Before downloading, briefly check the
returned results (thumbnail URLs, descriptions, duration, resolution) against
what the script line actually needs, and prefer:
- Horizontal orientation matching the target aspect ratio (16:9 for standard YouTube)
- At least 1080p source resolution (ideally higher, so downscaling doesn't lose quality)
- Duration long enough to cover the script segment it's illustrating, or explicitly plan to loop/extend it

If nothing from Pexels/Pixabay is a reasonable match, either broaden the
search query, try Pixabay if you started with Pexels (or vice versa), or fall
back to the paid source per the priority order above. Report to the user if no
licensed source has a good match rather than substituting something
tangential just to fill the slot.

## Step 3: Download with license metadata

Use `scripts/download_stock.py` (bundled) to download the selected clip AND
write a sidecar JSON recording the source, license, original URL, and
creator/attribution info — this matters even for "no attribution required"
licenses, because you want a paper trail if a video is ever challenged:

```bash
python scripts/download_stock.py --url "<video_file_url>" --source pexels \
  --id "<pexels_video_id>" --output footage/clip_042.mp4
```

This produces `footage/clip_042.mp4` and `footage/clip_042.license.json`
alongside it. Never delete or skip the sidecar file, even when the license
doesn't require attribution — future-proofing against license terms changing
or disputes.

## When NOT to use this skill

- Never use this skill's approach to justify downloading from YouTube,
  Vimeo, or general web search results, even if a video there looks like a
  perfect match and even if it's labeled "Creative Commons" on YouTube —
  YouTube's own ToS restricts downloading regardless of the uploader's
  license claim, and CC labels on YouTube are frequently misapplied. If the
  user explicitly asks for this, explain why it's out of scope for this
  skill rather than attempting it.
- If a project needs genuinely unique/rare footage that no stock library
  has (e.g. a very specific real-world event), that's a signal to shoot or
  commission it, not to source it through this skill.

## Reference files

- `scripts/search_stock.py` — queries Pexels/Pixabay video search endpoints
- `scripts/download_stock.py` — downloads a selected clip and writes a license metadata sidecar file
