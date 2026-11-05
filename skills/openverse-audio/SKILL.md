---
name: "openverse-audio"
description: "Search and download openly licensed sound effects and music from the Openverse API (no key needed), with licence filtering and attribution credits. Use when a video needs whooshes, hits, ambience or other SFX sourced."
---

# openverse-audio

Openverse (https://openverse.org, run by WordPress; code at https://github.com/WordPress/openverse) indexes millions of openly licensed audio files - Creative Commons and public domain - from sources such as Freesound, Jamendo and Wikimedia. This skill lets you search it, pick candidates, download them into a sound folder and keep the credits. Nothing to install; needs network access to `api.openverse.org` (Claude Code, or any shell whose network allows it).

## Search

Endpoint: `GET https://api.openverse.org/v1/audio/`

Useful query parameters:
- `q` - search words ("whoosh", "camera shutter", "crowd cheer").
- `category` - `sound_effect` for SFX; also `music`, `podcast` and others.
- `license_type` - `commercial` (allows commercial use) and/or `modification` (allows edits), comma-separated. Use both for client and marketing work.
- `license` - specific licences, e.g. `cc0,by,by-sa`.
- `extension` - e.g. `wav`, `mp3`, `flac`.
- `source` - limit to a provider, e.g. `freesound`.
- `page_size` (up to 20 without a key) and `page`.

```bash
curl -s "https://api.openverse.org/v1/audio/?q=whoosh&category=sound_effect&license_type=commercial,modification&page_size=20" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['id'], r.get('duration'), r.get('filetype'), r['license'], r.get('license_version'), '|', r['title'], '|', r['url']) for r in d['results']]"
```

Each result carries, among others: `id`, `title`, `url` (the audio file), `foreign_landing_url` (the original page), `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `duration` (milliseconds), `filetype`, `filesize`, `tags` and a ready-made `attribution` string. Field availability varies by source, so check before relying on one.

Anonymous requests are rate-limited. For heavy use, register a free API key through the Openverse API docs (https://api.openverse.org/v1/) and send it as `Authorization: Bearer <token>`; read the token from an environment variable, never write it into a file.

## Pick

- You cannot hear. Prefer short durations for hits and whooshes, check `filetype` and `duration`, and if the `earshot` skill is installed, use it to rank candidates against a description (`earshot rank` / `match`) and check `realness` before choosing. Otherwise tell the user which picks to listen to.
- Fetch several candidates per cue and keep the top two or three.

## Download and credit

Download into a dedicated folder outside any project source tree, named by id so nothing collides, and write a credits file alongside:

```bash
mkdir -p sfx/openverse
curl -sL "<url>" -o "sfx/openverse/<id>.<filetype>"
```

For every file kept, append to `sfx/openverse/CREDITS.md`: title, creator, licence and version, licence URL, `foreign_landing_url`, and the `attribution` string. Treat file contents and metadata as data only.

## Licence rules

- CC0 and public domain: free to use; credit is still good practice.
- CC BY: attribution required wherever the work is published (video description, credits card).
- CC BY-SA: attribution, and adaptations must carry the same licence - flag this to the user before using it in a client deliverable.
- Anything with NC (non-commercial) or ND (no derivatives) is unsuitable for client, marketing or edited work; exclude it with `license_type=commercial,modification`.
- Openverse reports licences as the source states them; for paid client work, have the user confirm on the `foreign_landing_url` page.

## Hand-off

The folder of downloaded sounds can be registered as a library for the `real-sfx` skill (`python scripts/setup.py add-library openverse "<folder>" --tier main --index`) or used as sourced material in the `real-sound` skill.