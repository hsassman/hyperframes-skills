---
name: "real-sound"
description: "Build a realistic soundtrack for a code-made video (Remotion, HyperFrames, three.js, GSAP) from real licensed recordings: cue list, sourcing, music edit, mix, QA, mastering, credits, mux. Use for film sound design."
---

# real-sound (installer wrapper)

Source: Leonxlnx/earshot, `skills/real-sound` (MIT License), https://github.com/Leonxlnx/earshot, pinned to commit 591fa3e028032e6dce56620a20e932e35667e8d8.

A sound-supervisor workflow for launch films, product videos, UI walkthroughs, logo stings and explainers: cue list from the picture, sourcing real recordings with licence checks, a music edit at bar lines, a deterministic JSON-driven mixer, measured QA (clicks, masking, harshness, sync, loudness) plus earshot listening, critique, mastering, credits and the final mux. Code places and processes sound; it never generates one.

## 1. Install (once)

This uses the same install as the `earshot` skill. If `$HOME/.claude/skill-src/earshot/.venv` does not exist yet, run the install block from the `earshot` skill first (pinned commit above; about 1.1 GB of models on first run - tell the user). Then:

```bash
SRC="$HOME/.claude/skill-src/earshot"
SKILL="$SRC/skills/real-sound"
PY="$SRC/.venv/bin/python"            # Windows: $SRC\.venv\Scripts\python.exe
"$PY" -c "import earshot, numpy, scipy, soundfile"
```

Node.js is needed for `scripts/mux.mjs`; FFmpeg must be on PATH.

## 2. Hand over

Read `$SKILL/SKILL.md` in full, plus the references it names (`references/process.md`, `references/sound-design.md`), and follow them exactly. Substitute the full venv interpreter path for every `{{PY}}` placeholder, `$SKILL` for `<skill>`, and run its scripts with `-I` as it instructs.

## Rules

- Only real, licensed recordings. Check every licence with the skill's own audit step and produce its credits file; never use a sound whose licence forbids the user's intended use.
- For sourcing candidates, the `openverse-audio` skill searches openly licensed audio; Freesound, Mixkit and others need their own licence checks as the upstream skill describes.
- Work on copies; deliver a new MP4, the mixed audio and the credits. Do not modify files inside the cloned repo.