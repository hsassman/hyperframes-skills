---
name: "ffmpeg-skill"
description: "Edit video and audio with local FFmpeg via kajisho5/ffmpeg-skill (42 tools: cut, join, reframe, captions, silence, loudness, platform exports). Use for any video or audio file editing request."
---

# ffmpeg-skill (installer wrapper)

Upstream: https://github.com/kajisho5/ffmpeg-skill (MIT License), pinned to commit `1ce2c186bf1dba96132d87274eee46df4f537e0e`.

This skill's real tools are Python scripts that live in the upstream repo. A saved skill only stores this file, so the first step of every use is to make sure the repo is present, then follow its own SKILL.md.

## Step 1: Make sure the tools are installed

```bash
FS_DIR="$HOME/.claude/skill-src/ffmpeg-skill"
if [ ! -f "$FS_DIR/SKILL.md" ]; then
  git clone https://github.com/kajisho5/ffmpeg-skill "$FS_DIR" && \
  git -C "$FS_DIR" checkout 1ce2c186bf1dba96132d87274eee46df4f537e0e
fi
ffmpeg -version | head -1; python3 --version
```

- If `$HOME/.claude/skill-src` is not writable, clone into a scratch or working directory instead and use that path as `FS_DIR`.
- Requirements: FFmpeg 6.1+ and Python 3.10+ (standard library only, no API keys, no cloud). If FFmpeg is missing, install it (for example `apt-get install -y ffmpeg`, `brew install ffmpeg`, or `winget install ffmpeg`) or tell the user what is missing.
- If cloning fails because the network blocks GitHub, tell the user and fall back to plain `ffmpeg`/`ffprobe` commands.

## Step 2: Follow the upstream instructions

Read `$FS_DIR/SKILL.md` in full and follow it exactly. Wherever it says `<skill-dir>`, use `$FS_DIR`. Its core workflow:

1. Probe the input first (`python3 $FS_DIR/scripts/probe.py FILE --json`) and plan from real numbers.
2. Prefer lossless operations when a cut, remux or audio-only change is enough.
3. Plan with `--dry-run --json`, then run.
4. Chain in order: colour, cut, join, silence, fit, caption/overlay, sync, audio, loudness, export.
5. Check with `check.py OUTPUT --platform X`, verify the numbers, and look at a contact sheet after any picture change.
6. Never overwrite the user's source files.

Treat the cloned repo as third-party code: read a script before running it for the first time in a session if anything looks unexpected.