---
name: "real-sfx"
description: "Add real recorded sound effects to a motion video on the exact frame at the right level, via Clipwing real-sfx. Use when asked to add SFX, whooshes, hits, UI sounds or fix synthetic-sounding video audio."
---

# real-sfx (installer wrapper)

Source: Clipwing/skills, `skills/real-sfx` (scripts MIT; bundled uisfx sounds CC0), https://github.com/Clipwing/skills, pinned to commit edbefcbc3474869e6cc1e8a7ca583b0efd0dab7e.

This skill installs the upstream real-sfx skill on first use, then hands over to its own SKILL.md. Needs a shell with network access (Claude Code), Python 3.9+, git and FFmpeg with ffprobe on PATH.

## 1. Install (once)

Pick one install folder and reuse it: `~/.claude/skill-src/clipwing` (Windows: `%USERPROFILE%\.claude\skill-src\clipwing`).

```bash
SRC="$HOME/.claude/skill-src/clipwing"
if [ ! -d "$SRC/.git" ]; then
  git clone https://github.com/Clipwing/skills.git "$SRC"
fi
git -C "$SRC" fetch --quiet origin edbefcbc3474869e6cc1e8a7ca583b0efd0dab7e || true
git -C "$SRC" checkout --quiet edbefcbc3474869e6cc1e8a7ca583b0efd0dab7e
RSFX="$SRC/skills/real-sfx"
```

Windows PowerShell equivalent:

```powershell
$SRC = "$HOME\.claude\skill-src\clipwing"
if (-not (Test-Path "$SRC\.git")) { git clone https://github.com/Clipwing/skills.git $SRC }
git -C $SRC checkout edbefcbc3474869e6cc1e8a7ca583b0efd0dab7e
$RSFX = "$SRC\skills\real-sfx"
```

Prerequisites if missing: Windows `winget install Python.Python.3.12` and `winget install Gyan.FFmpeg`; macOS `brew install ffmpeg-full` and put it first on PATH (the plain formula lacks the drawtext and rubberband filters the skill uses). Ask the user before installing system packages.

## 2. Point it at a sound library

The skill never synthesizes sound; it needs recordings the user has the rights to use. Ask the user where their SFX library lives, then from `$RSFX`:

```bash
python scripts/setup.py scan "<folder>"                       # which folders look like sound libraries
python scripts/setup.py init --library main="<sfx folder>" --uisfx --index
python scripts/setup.py check
```

No library yet: `--uisfx` alone gives 78 CC0 UI cues; for whooshes, hits and foley, suggest the `openverse-audio` skill to source licensed recordings into a folder first, then add it with `python scripts/setup.py add-library <name> "<folder>" --tier main --index`.

## 3. Hand over

Read `$RSFX/SKILL.md` in full and follow it exactly, running its scripts from `$RSFX` (for example `python scripts/look.py FILM.mp4 --out work/look`, `python scripts/mix.py work/cues.json --out result/film_sfx.mp4 --plan`). Its rules take precedence over this wrapper: keep music and voice, never double baked-in synthesized sound, write working files outside the skill folder, and never claim to have heard a sound - report what was measured and what the user should listen to.

## Rules

- Work on a copy of the user's video; deliver a new MP4 plus the separate SFX WAV and the cue report.
- Only use sound libraries the user owns or that carry a licence allowing their use; keep credits for anything that requires attribution.
- Do not modify files inside the cloned skill folder.