# The motion-film workflow

A film is built as code: an HTML composition (HyperFrames) driven by one GSAP timeline, with Three.js canvases for 3D
layers, rendered frame by frame to MP4. Because it is code, every frame can be snapshotted for a storyboard, every
picture event can drive the sound cue sheet, and cut-downs can be assembled from the hero render without re-rendering.

```
brief ─► media audit ─► music + beat sheet ─► composition (gen.py → index.html)
                                                     │
                       ┌─────── storyboard (snapshots) ◄┘ ◄── client rounds
                       ▼
               picture lock ─► render ─┐
   events.json ─► sound pass ─► master ┴► mux ─► QA ─► cut-downs ─► delivery + hand-off
```

| Phase | Skill(s) | Output | Gate |
|---|---|---|---|
| 1. Brief | motion-film, script-structure | answers, single-minded message, facts list | questions answered |
| 2. Media | ffmpeg-processor, stock-footage-sourcer | inventory, contact sheets, transcodes | — |
| 3. Story | script-structure | beat sheet on the music's bar grid | — |
| 4. Composition | motion-film (kit), hyperframes, threejs-* | `gen.py`, `index.html`, `events.json` | lint 0 errors |
| 5. Storyboard | motion-film (storyboard builder) | review page from real frames | client approval |
| 6. Sound | real-sound, real-sfx, openverse-audio, earshot, audio-mastering | stems, `mix_master.wav`, credits | report clean, −14 LUFS |
| 7. Render | hyperframes | picture MP4 | frame count |
| 8. QA | ffmpeg-skill, earshot | QA report, contact sheet | matches storyboard |
| 9. Cut-downs | motion-film (cutdowns.py) | 30 s / 15 s | cuts on bars |
| 10. Deliver | ffmpeg-processor | masters, share versions, credits, editable project | — |

Optional voice-over: qwen-tts-voiceover → audio-mastering → caption-sync, then time beats to the words.

Details for each phase live in `skills/motion-film/references/`.
