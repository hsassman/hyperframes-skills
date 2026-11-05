# The motion-film workflow at a glance

A film is built as code: an HTML composition (HyperFrames) driven by one GSAP timeline, with Three.js canvases for 3D
layers, rendered frame by frame to MP4. Because it is code, every frame can be snapshotted for a storyboard, every
picture event can drive the sound cue sheet, and cut-downs can be assembled from the hero render without re-rendering.

```
brief ─► media audit ─► music + beat sheet ─► composition (gen.py → index.html)
                                                     │
                       ┌─────── storyboard (snapshots) ◄┘ ◄── review rounds
                       ▼
               picture lock ─► render ─┐
   events.json ─► sound pass ─► master ┴► mux ─► QA ─► cut-downs ─► delivery + editable project
```

| Phase | Skills / tools | Output | Gate |
|---|---|---|---|
| 1. Brief and story | motion-film | answers, single-minded message, facts list, beat sheet | questions answered |
| 2. Media | FFmpeg, `prep.py` | inventory, contact sheets, transcodes, clean-ups | every beat has media or a graphic |
| 3. Music | `music_grid.py`, Pixabay Music | licensed track, bar grid, edit length | beats on bar lines |
| 4. Composition | motion-film kit, hyperframes, threejs-* | `gen.py`, `index.html`, `events.json` | lint 0 errors |
| 5. Generated assets | image model, `prep.py` | cut-out textures and effects | no generated text or logos |
| 6. Storyboard | `build_storyboard.py`, Claude artifacts | review page from real frames | approval |
| 7. Critique | `review-checklist.md` | fixes | checklist passes |
| 8. Sound | Pixabay / Freesound / Openverse, `mixkit.py`, real-sfx, earshot, `master.py` | stems, master, credits | −14 LUFS, report clean |
| 9. Render and QA | HyperFrames, `finish.py` | master, share versions | specs, scans, frame count |
| 10. Cut-downs | `cutdowns.py` | shorter versions | cuts on bars |

Details for each phase live in `skills/motion-film/references/`.
