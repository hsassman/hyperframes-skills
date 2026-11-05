# Sound: music edit, effects, mix, master

Real recordings only. Synthesised whooshes and beeps make code-made films feel fake. (The `real-sound` and `real-sfx`
skills cover sourcing and placement in depth; `earshot` measures and compares audio; `openverse-audio` searches
openly-licensed libraries; `audio-mastering` covers the loudness standard.)

## 1. Music first
- Choose a licensed track that fits the pace (documentary/cinematic, 90–125 BPM, builds to a peak). Keep the licence page
  and the track's source URL.
- Map it: `python3 kit/audio/music_grid.py track.mp3 [--bpm 120]` → bars, energy and downbeat "hits". Phrase starts are the
  strong hits every 4 bars.
- Edit to the film length on bar lines (equal-power crossfade ending on the downbeat — `cutdowns.splice`). A common shape:
  the track from 0:00 up to a bar, then the track's own ending.
- Time the picture to the music: chapter starts on bars, payoff on the biggest hit, end card on the resolution.

## 2. Source effects
Search licensed libraries (Pixabay sound effects, Openverse, Freesound with a commercial-use licence). Download through a
browser when the shell's network is restricted. **Record every file at download time** in `sources.json`
(`file, title, url, licence`). Typical set for a process film: paper slides, marker/pencil, tape, box thuds, machine and
room ambiences, whooshes (2–3 different), a riser, clicks/ticks, a soft chime, pops, a door/shutter, wind, a powder puff.

## 3. Cue sheet on picture events
`gen.py` writes `events.json` (every title, reveal, draw, sticker, wipe, slam, burst, count). Map event kinds to sounds in
the sound script (see `example/sound.py`), then hand-place the rest. Rules:
- Place the **peak** of whooshes/risers on the moment (`peak_at=`), not their start.
- Beds (machines, rooms, wind) under each chapter, faded at chapter edges, high-passed (120–300 Hz) so they don't muddy music.
- Counters: one tick from a real recording per whole number (`mx.ticks`).
- Short music dips (−4 dB over 0.5 s) into the 2–3 biggest hits (`mx.dip_before`).
- Repeated uses of a recording rotate through different takes automatically.

## 4. Levels
`Mix` levels each cue against the music **around that cue** (±0.75 s), with role targets (`ROLE`) and per-role sample-peak
ceilings (`CAP`). After rendering run `print(mx.report())`: fix anything flagged QUIET (inaudible: raise `db` or choose a
punchier take) or HOT (dominating: lower `db`). Targets: transitions −1 to −4 dB vs music, accents −4 to −12, beds −12 to −18.

## 5. Master
`python3 kit/audio/master.py mix_pre.wav mix_master.wav --fade <picture fade>` → transparent limiter set from the measured
loudness, then two-pass loudness normalisation to −14 LUFS integrated, −1 dBTP. Verify with `earshot measure` or
`ffmpeg -af ebur128=peak=true`. Expect LRA 4–7 LU for this style.

## 6. Credits
`python3 kit/audio/credits.py cues.json sources.json Audio_Credits.md --music "Track by Artist (licence, url)"` →
credits + full cue sheet. Deliver it with the film.
