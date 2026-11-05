# Composition (HyperFrames + filmkit)

Read the `hyperframes` skill first for the render contract. This file covers how films are structured with `filmkit`.

## Project layout
```
project/
  gen.py            # the film: chapters as code (copy example/gen.py)
  index.html        # generated — never hand-edit unless you stop using gen.py (see Hand-off)
  events.json       # generated picture events for the sound pass
  hyperframes.json, meta.json
  assets/           # media, fonts, gsap.min.js, MorphSVGPlugin.min.js, film3d.js, geo.js, illos.json, grounds, overlays
```

## Building blocks (`Film` methods)
- Clips: `ground` (drifting plate + giant outline word), `container` (wraps a layer), `canvas3d`, `raw_clip`, `full_video`.
- Media: `win_img`, `win_vid` (top-level muted `<video>` + frame), `polaroid`, `tagbox`.
- Type: `title` (chip + headline rise/letters/blur + sub line), `counter`.
- Drawn: `illo` (hero illustration from `illos.json`), `arrow`, `note` (hand or sticker), `brace`, `underline`, `loop`,
  `process_line` — all edge-boiled.
- Transitions: `band_wipe`, `whip`, `texture_cover`, `shutter`, `cloud_pass`, `burst` (can follow a map point), `fade_out`.
- 3D: `film.init3d("FILM3D.particles(...)")` / `FILM3D.map(...)` on a `canvas3d`.
- Every helper records picture events (`film.event`) → `events.json`, which the sound pass uses.

## Layout grammar that works
- **Layers per chapter:** `bN` (back, under videos) and `fN` (front, over videos) → `container("cbN","bN",...)` z 18–22 and
  `container("cfN","fN",...)` z 40. Videos z 20–30. Grounds z 1–20 (later chapters higher). Transitions z 150–180.
  End card z 90–95. Grain/vignette z 200. Fade-out z 300.
- **Overlap chapters by 0.3–0.6 s** and let the next ground fade/cover; end each front container (or fade it) before the next
  chapter's content appears, or old stickers float over new scenes.
- **Fill the frame:** 2–3 media windows + an illustration + title per chapter; avoid big empty areas. Use giant outline words
  and pre-rendered grounds for colour and depth.
- **Safe areas:** titles top-left at x≈130, y≈140–150; nothing important within 60 px of edges.
- **Never** let an oversized image or overlay scale below the frame size (edges show). Keep cover-type overlays ≥ 1.04×.

## Grounds
Render gradients and glows to images with `filmkit.grounds.plate(...)` (2112×1188, they drift). Stacking CSS radial
gradients and blurred blobs triggers lint warnings and slows renders.

## Lint and checks
`npx hyperframes lint` must show 0 errors. Generated single-file films trigger `nested_structure_needs_subcomposition`
warnings — expected; they only affect how the Studio timeline displays rows. Split chapters into sub-compositions only
if someone will edit the film by hand on the Studio timeline.

## Hand-off to the HyperFrames app
Copy the project folder (index.html + assets + hyperframes.json + meta.json) to the editor's machine; they open it with
File › Open Folder. From then on `index.html` is the source of truth: either port their edits back into `gen.py` or switch
to editing `index.html` directly. Ask them to log changes (time, element id, what, why) in `CHANGES.md` so the sound mix
and cut-downs can be rebuilt. Timing changes break the fixed soundtrack — re-run the sound pass after them.
