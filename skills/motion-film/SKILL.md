---
name: motion-film
description: Make a high-end promo or explainer film in code — real footage and photos, hand-drawn animated graphics with edge boil, GSAP motion, Three.js 3D (particles, maps), generated overlays, and a real-recorded sound mix — rendered with HyperFrames, storyboarded for client review, then cut down to 30 s / 15 s. Use for any brand, product, process or story video built from code.
---

# motion-film

An end-to-end workflow for films that look like a motion-design studio made them: real media in framed windows, drawn
illustrations and annotations that boil like hand animation, kinetic type, 3D layers, transitions that are *caused* by
something on screen, and a soundtrack made of real recordings placed on the exact frames. Everything is code, so every
change is cheap, re-timeable and re-renderable.

Kit (in this skill folder):
- `kit/filmkit/` — Python composition builder (`Film`, `Theme`) and chapter grounds. Writes `index.html` + `events.json`.
- `kit/node/` — Three.js layer bundle (`FILM3D.particles`, `FILM3D.map`), country geography (`geo.mjs`), illustration builder (`illos.mjs`, rough.js).
- `kit/assets/prep.py` — cut generated overlays out of black, sprites, brand tints, material textures, safe photo clean-up.
- `kit/audio/` — `mixkit.py` (cue placement + levels), `master.py` (−14 LUFS / −1 dBTP), `music_grid.py` (bars/phrases),
  `cutdowns.py` (30 s / 15 s from the hero), `finish.py` (mux, QA, share encodes, contact sheets), `credits.py`.
- `kit/storyboard/build_storyboard.py` — storyboard page from real frames of the composition.
- `example/` — a runnable 20 s demo that uses every piece. Start here: `example/setup.sh`, then read `example/gen.py`.

Companion skills (installed by this repo's installer): `hyperframes` + `hyperframes-cli` (render contract — read first when
writing composition code), `threejs-*` (3D), `real-sound` / `real-sfx` / `earshot` / `openverse-audio` (sound sourcing and
listening), `audio-mastering`, `ffmpeg-processor` / `ffmpeg-skill`, `script-structure`, `stock-footage-sourcer`, `caption-sync`.

## The workflow (phases and gates)

Work in this order. Each phase ends with a gate; do not start the next phase until it passes. Read the phase's reference
file before doing it.

| # | Phase | Output | Gate | Read |
|---|---|---|---|---|
| 1 | Brief and story | one-page brief, beat sheet on a bar grid | the story works as 6–10 one-line beats with a payoff | `references/brief-and-story.md` |
| 2 | Media audit | contact sheet of every clip/photo, picks, trims, clean-ups | every beat has real media or a planned graphic | `references/media.md` |
| 3 | Music first | licensed track, bar grid, edit length | chapter starts sit on bar lines; payoff on the strongest hit | `references/sound.md` §1 |
| 4 | Build | `gen.py` → `index.html`, lint clean | `npx hyperframes lint` 0 errors | `references/composition.md`, `references/motion-language.md`, `references/threejs-layers.md` |
| 5 | Generated assets | overlays/textures cut out and graded | no AI-drawn text or logos anywhere | `references/ai-assets.md` |
| 6 | Storyboard | page of real stills + captions, published for review | client approves or marks frames | `references/storyboard-and-review.md` |
| 7 | Critique loop | snapshots → critique → fix → re-snapshot | the checklist in `references/review-checklist.md` passes | `references/review-checklist.md` |
| 8 | Sound | cue sheet on picture events, mix, master | −14 LUFS ±0.5, TP ≤ −1 dBTP, no inaudible or dominant cues | `references/sound.md` |
| 9 | Render, QA, deliver | hero master + share versions + credits | specs, black/freeze scan, loudness, frame spot-checks pass | `references/render-qa-deliver.md` |
| 10 | Cut-downs | 30 s / 15 s from the hero, own music edits | frame-exact, cuts on bars, end card ≥ 3 s | `references/cutdowns.md` |

Approval rules: show the storyboard before any long render. Never render the hero before the client has approved the
frames. After a round of client notes, change only what they marked (scope discipline) and say what else you would change.

## Non-negotiables

- **Real media is the hero.** Graphics frame, explain and connect footage; they never replace proof.
- **No generated text, logos or labels.** Image models garble words and redraw marks. Generate textures and effects only
  (frost, smoke, clouds, powder, paper); composite real logos and set real type in code.
- **Never "clean up" photos with printed packaging or signage in an image model** — it redraws the print and re-frames
  the shot. Use `kit/assets/prep.py cleanup` (deterministic) instead.
- **Facts only from the client.** Numbers, claims, places, product names: from the brief or marked `[CONFIRM]`.
- **Every transition is motivated** by something in frame (a band, a door, a burst, a whip, the camera rising).
- **Determinism.** Everything is a function of timeline time: GSAP on the paused timeline, Three.js on `hf-seek`, no
  `Math.random()` at render time (seeded generators only), no wall-clock animation.
- **Music leads, effects articulate.** Real recordings only, each with a licence and source URL recorded at download time.
- **Restraint with annotation.** One drawn loop per film reads as emphasis; one per scene reads as a tic. Prefer arrows and
  stickers that point at a real thing; prefer solid lines over dotted ones.

## Quick start

```bash
cd example && ./setup.sh                      # builds the 3D bundle, geography, illustrations, fonts, assets, index.html
npx hyperframes lint                          # 0 errors expected (nested-structure warnings are expected for generated films)
npx hyperframes snapshot --at 3,9,13.5,18 -o snaps
python3 sound.py --demo                       # placeholder audio -> mixed and mastered
npx hyperframes render . -o renders/picture.mp4 -q high
python3 ../kit/audio/finish.py mux renders/picture.mp4 audio/out/mix_master.wav renders/film.mp4
python3 ../kit/audio/finish.py qa renders/film.mp4
```
On Linux without a GPU set `PRODUCER_HEADLESS_SHELL_PATH` to a chrome-headless-shell binary; software WebGL renders
roughly 1 frame per second, so a 70 s film takes about an hour (desktop GPUs are far faster). The HyperFrames desktop app
can open the project folder for hand edits (File › Open Folder); see `references/render-qa-deliver.md` §Hand-off.
