---
name: motion-film
description: Make a studio-quality motion film in code for any subject — brand, product launch, explainer, process, data story, event recap, social cut — combining real footage and photos, hand-drawn animated graphics, kinetic type, GSAP motion, Three.js 3D (particles, maps) and a real-recorded sound mix, rendered with HyperFrames, storyboarded for review and cut down to shorter versions. Use whenever someone wants a video built from code.
---

# motion-film

An end-to-end workflow for films that look like a motion-design studio made them: real media in framed windows,
illustrations and annotations that boil like hand animation, kinetic type, 3D layers, transitions that are *caused* by
something on screen, and a soundtrack of real recordings placed on the exact frames. Everything is code, so every
change is cheap, re-timeable and re-renderable, and every frame can be checked before the long render.

The kit adapts to the film you're asked for — any brand, subject, length, tone or aspect ratio (16:9, 9:16, 1:1 via
`Film(width=…, height=…)`). Nothing in it assumes a particular industry or story shape.

Kit (in this skill folder):
- `kit/filmkit/` — Python composition builder (`Film`, `Theme`) and ground plates. Writes `index.html` + `events.json`.
- `kit/node/` — Three.js layer bundle (`FILM3D.particles`, `FILM3D.map`), geography for any country (`geo.mjs`),
  hand-drawn illustration builder (`illo-lib.mjs`, rough.js; `illos.mjs` is an example to copy).
- `kit/assets/prep.py` — cut generated overlays out of black, particle sprites, brand tints, material textures, safe photo clean-up.
- `kit/audio/` — `mixkit.py` (cue placement + levels), `master.py` (−14 LUFS / −1 dBTP), `music_grid.py` (bars/phrases),
  `cutdowns.py` (shorter versions from the hero), `finish.py` (mux, QA, share encodes, contact sheets), `credits.py`.
- `kit/storyboard/build_storyboard.py` — storyboard page built from real frames of the composition.
- `example/` — a runnable 20 s demo that uses every piece. Start here: `example/setup.sh`, then read `example/gen.py`.

Companion skills (installed by this repo's installer):
- Composition: `hyperframes`, `hyperframes-cli` (render contract — read first when writing composition code), `threejs-*`.
- Story and media: `script-structure` (beat sheets and scoring), `stock-footage-sourcer` (licensed stock when there is no
  own footage), `ffmpeg-processor` / `ffmpeg-skill` (media prep and edits).
- Sound: `real-sound` (full soundtrack from real recordings), `real-sfx` (frame-accurate effects), `openverse-audio`
  (licensed effects and music), `earshot` (measuring audio), `audio-mastering` (denoise + loudness).
- Voice-over: `qwen-tts-voiceover` (narration), `caption-sync` (word timings and captions).

Every tool, library, API and content source is listed in `references/tools-and-sources.md`.

## The workflow (phases and gates)

Work in this order. Each phase ends with a gate; do not start the next phase until it passes. Read the phase's reference
file before doing it.

| # | Phase | Output | Gate | Read |
|---|---|---|---|---|
| 1 | Brief and story | one-page brief, beat sheet on a bar grid | the story works as one-line beats with a payoff | `references/brief-and-story.md` |
| 2 | Media audit | contact sheet of every clip/photo, picks, trims, clean-ups | every beat has real media or a planned graphic | `references/media.md` |
| 3 | Music first | licensed track, bar grid, edit length | beat starts sit on bar lines; payoff on the strongest hit | `references/sound.md` §1 |
| 4 | Build | `gen.py` → `index.html`, lint clean | `npx hyperframes lint` 0 errors | `references/composition.md`, `references/motion-language.md`, `references/threejs-layers.md` |
| 5 | Generated assets | overlays/textures cut out and graded | no AI-drawn text or logos anywhere | `references/ai-assets.md` |
| 6 | Storyboard | page of real stills + captions, published for review | the person approves or marks frames | `references/storyboard-and-review.md` |
| 7 | Critique loop | snapshots → critique → fix → re-snapshot | `references/review-checklist.md` passes | `references/review-checklist.md` |
| 8 | Sound | cue sheet on picture events, mix, master | −14 LUFS ±0.5, TP ≤ −1 dBTP, no inaudible or dominant cues | `references/sound.md` |
| 9 | Render, QA, deliver | master + share versions + credits | specs, black/freeze scan, loudness, frame spot-checks pass | `references/render-qa-deliver.md` |
| 10 | Cut-downs | shorter versions from the hero, own music edits | frame-exact, cuts on bars, end card ≥ 3 s | `references/cutdowns.md` |

Approval rules: show the storyboard before any long render. After a round of notes, change only what was marked (scope
discipline) and say what else you would change.

## Non-negotiables

- **Real media is the hero** when the subject has real media. Graphics frame, explain and connect footage; they never
  replace proof. Films without footage lean on illustration, type, 3D and generated textures instead.
- **No generated text, logos or labels.** Image models garble words and redraw marks. Generate textures and effects only;
  composite real logo files and set real type in code.
- **Never "clean up" photos with printed text, packaging or signage in an image model** — it redraws the print and
  re-frames the shot. Use `kit/assets/prep.py cleanup` (deterministic) instead.
- **Facts only from the person or their sources.** Numbers, claims, places, names: from the brief or marked `[CONFIRM]`.
- **Every transition is motivated** by something in frame (a band, a panel, a burst, a whip, a texture, the camera rising).
- **Determinism.** Everything is a function of timeline time: GSAP on the paused timeline, Three.js on `hf-seek`, no
  `Math.random()` at render time (seeded generators only), no wall-clock animation.
- **Music leads, effects articulate.** Real recordings only, each with a licence and source URL recorded at download time.
- **Restraint with annotation.** One drawn loop per film reads as emphasis; one per scene reads as a tic. Prefer arrows and
  stickers that point at a real thing; prefer solid lines over dotted ones.

## Quick start

```bash
cd example && ./setup.sh                      # 3D bundle, geography, illustrations, fonts, assets, index.html
npx hyperframes lint                          # 0 errors expected (nested-structure warnings are expected for generated films)
npx hyperframes snapshot --at 3,9,14.5,18.8 -o snaps
python3 sound.py --demo                       # placeholder audio -> mixed and mastered
npx hyperframes render . -o renders/picture.mp4 -q high
python3 ../kit/audio/finish.py mux renders/picture.mp4 audio/out/mix_master.wav renders/film.mp4
python3 ../kit/audio/finish.py qa renders/film.mp4
```
On Linux without a GPU set `PRODUCER_HEADLESS_SHELL_PATH` to a chrome-headless-shell binary; software WebGL renders
roughly 1 frame per second, so a 70 s film takes about an hour (desktop GPUs are far faster). The HyperFrames desktop app
can open the project folder for hand edits (File › Open Folder); see `references/render-qa-deliver.md` §Hand-off.
