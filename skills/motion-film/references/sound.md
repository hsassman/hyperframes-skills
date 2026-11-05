# Sound: music edit, effects, mix, master

Real recordings only. Synthesised whooshes and beeps make code-made films feel fake. Sources, APIs and licences are listed
in `references/tools-and-sources.md`. Companion skills: `real-sound` (the same process in more depth), `openverse-audio`
(search and download with licence filtering), `real-sfx` (frame-accurate placement from a look at the picture),
`earshot` (measure and compare audio you can't hear), `audio-mastering` (denoise and loudness for voice tracks).

## 1. Music first
- Choose a licensed track that fits the pace and mood (it decides the film's rhythm; most brand and explainer films sit at
  90–125 BPM and build to a peak). Save the track page URL and its licence when you download it.
- Map it: `python3 kit/audio/music_grid.py track.mp3 [--bpm 120]` → bars, energy and downbeat "hits". Phrase starts are the
  strong hits every 4 bars.
- Edit to the film length on bar lines (equal-power crossfade ending on the downbeat — `cutdowns.splice`). A common shape:
  the track from 0:00 up to a bar, then the track's own ending.
- Time the picture to the music: beat starts on bars, payoff on the biggest hit, end card on the resolution.

## 2. Source effects
Search the libraries in `references/tools-and-sources.md` (Pixabay sound effects first; Freesound and Openverse — via the
`openverse-audio` skill — when Pixabay has nothing that fits). Download through a browser when the shell's network is restricted. **Record every file at
download time** in `sources.json` (`file, title, author, url, licence`).

Build the list from what is on screen, not from a template: every reveal, draw-on, landing, count, transition and scene
needs a sound that belongs to it. A useful starting kit for any film: 2–3 different whooshes and a riser, soft clicks or
ticks, a pop, a chime, paper and pencil/marker foley for drawn graphics, one or two impacts, and a room or outdoor
ambience per scene. Then add the subject's own sounds (its machines, materials, places, actions).

## 3. Cue sheet on picture events
`gen.py` writes `events.json` (every title, reveal, draw, sticker, wipe, panel, texture, burst, count). Map event kinds to
sounds in the sound script (see `example/sound.py`), then hand-place the rest. Rules:
- Place the **peak** of whooshes/risers on the moment (`peak_at=`), not their start.
- Beds (ambiences, machines, rooms, air) under each scene, faded at scene edges, high-passed (120–300 Hz) so they don't
  muddy the music.
- Counters: one tick from a real recording per whole number (`mx.ticks`).
- Short music dips (−4 dB over 0.5 s) into the 2–3 biggest hits (`mx.dip_before`).
- Repeated uses of a recording rotate through different takes automatically.
- With a voice-over: duck the music 6–9 dB under speech and keep effects out of the words.

## 4. Levels
`Mix` levels each cue against the music **around that cue** (±0.75 s), with role targets (`ROLE`) and per-role sample-peak
ceilings (`CAP`). After rendering run `print(mx.report())`: fix anything flagged QUIET (inaudible: raise `db` or choose a
punchier take) or HOT (dominating: lower `db`). Targets: transitions −1 to −4 dB vs music, accents −4 to −12, beds −12 to −18.

## 5. Master
`python3 kit/audio/master.py mix_pre.wav mix_master.wav --fade <picture fade>` → transparent limiter set from the measured
loudness, then two-pass loudness normalisation (ffmpeg-normalize) to −14 LUFS integrated, −1 dBTP. Verify with
`earshot measure` or `ffmpeg -af ebur128=peak=true`. Expect LRA 4–7 LU for music-led films.

## 6. Credits
`python3 kit/audio/credits.py cues.json sources.json Audio_Credits.md --music "Track by Artist (licence, url)"` →
credits + full cue sheet. Deliver it with the film.
