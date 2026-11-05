---
name: "earshot"
description: "Give an agent ears with earshot (Leonxlnx/earshot): measure, rank, compare and critique audio, check realness and sync, and generate or forge sounds in code. Use before judging how any audio sounds."
---

# earshot (installer wrapper)

Source: Leonxlnx/earshot (MIT License), https://github.com/Leonxlnx/earshot, pinned to commit 591fa3e028032e6dce56620a20e932e35667e8d8.

earshot lets you judge audio you cannot hear: loudness, matching a sound to a description, ranking candidates, real-vs-synthesized checks, timelines against picture, A/B mix comparisons, and `forge`/`sfx`/`kit` for making a brand-new sound in code when no recording fits. It runs locally on CPU. Needs a shell with network access (Claude Code), Python 3.10+, git and FFmpeg. The first run downloads about 1.1 GB of listening models - tell the user before starting.

## 1. Install (once)

```bash
SRC="$HOME/.claude/skill-src/earshot"
if [ ! -d "$SRC/.git" ]; then git clone https://github.com/Leonxlnx/earshot "$SRC"; fi
git -C "$SRC" fetch --quiet origin 591fa3e028032e6dce56620a20e932e35667e8d8 || true
git -C "$SRC" checkout --quiet 591fa3e028032e6dce56620a20e932e35667e8d8
python3 -m venv "$SRC/.venv"
PY="$SRC/.venv/bin/python"            # Windows: $SRC\.venv\Scripts\python.exe
"$PY" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
"$PY" -m pip install -e "$SRC[mcp,llm]"
"$PY" -m earshot doctor
```

On Windows never use bare `python` for earshot (often the Microsoft Store stub); always the venv's `python.exe` by full path.

Optional, recommended for many calls (models stay loaded between calls) - register the MCP server, after asking the user:

```bash
claude mcp add earshot --scope user -e EARSHOT_THREADS=3 -- "$PY" -m earshot mcp
```

The optional `llm` critique sends audio to Gemini and needs `GEMINI_API_KEY` in the user's environment; never write a key into a file, and tell the user that this one command leaves the machine.

## 2. Hand over

Read `$SRC/skills/earshot/SKILL.md` in full and follow it exactly - its commands (`measure`, `describe`, `match`, `rank`, `find`, `compare`, `ab`, `realness`, `timeline`, `sheet`, `critique`, `forge`, `sfx`, `kit`) and its rule: never say how audio sounds without an earshot reading behind it, and quote the number.

For building a full soundtrack from real licensed recordings, use the companion `real-sound` skill (same install) or the `motion-film` skill's `references/sound.md`; earshot is how you check every step.

## Rules

- Pass absolute paths. Cache and outputs go outside the cloned repo.
- Do not modify files inside the cloned repo.