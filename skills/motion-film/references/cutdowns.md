# Cut-downs (30 s / 15 s) from the hero — no re-render

A cut-down is a sequence of hero segments, every cut on a bar line of the cut-down's own music edit. Because the hero's
chapters already sit on the music grid, segments that start and end on hero bar lines keep every title landing on a beat.

## Choosing segments
- Cut **between** transitions, never in the middle of one: start segments on bar lines where nothing is mid-flight.
- Let a segment **end** with a transition (a whip out, a texture flash, a panel landing) so the next hard cut lands on its downbeat.
- Keep: hook with the opening line → the 2–4 strongest beats → the proof moment → the payoff → end card.
- Put the payoff (counter, map) on the music edit's strongest phrase start.
- End card needs ≥ 3 s after its last element lands, then a short fade (0.5–0.6 s) to the brand's deep colour.
- Avoid segments whose content breaks the reviewer's taste rules if alternatives exist.

## Music edit
Phrase-aligned splices sound natural: e.g. 30 s = track bars 2.4 → 24.4 (if the track starts 0.4 s before a bar) plus the
final phrase and its decay; 15 s = the final phrase with a 1-beat pickup. Equal-power crossfades of 60 ms that **end** on
the downbeat keep the transient intact.

## Effects
Slice the hero's effects stem on the same frames (12 ms crossfades) and re-level against the new music (difference of the
local music levels, clamped −8…+3 dB). The hero's cue timing carries over exactly.

## Run
```bash
python3 kit/audio/cutdowns.py cutdowns.json audio     # music edit + effects + master per cut
python3 kit/audio/cutdowns.py cutdowns.json picture   # frame-accurate picture per cut (checks frame count)
python3 kit/audio/finish.py mux audio/out/cut30_picture.mp4 audio/out/cut30_master.wav deliver/Film_30s.mp4
```
Verify cut points against hero frames (mean absolute difference smallest at offset 0) and watch every cut.
