# Render, QA and delivery

## Render
1. Lock: copy `index.html` → `index_lock.html` (and `gen.py` → `gen_lock.py`). Generate without audio for the picture
   render; the master is muxed afterwards so the mix can change without re-rendering.
2. `npx hyperframes render . -o renders/picture.mp4 -q high` (run in the background; ~1 frame/s on CPU-only Linux).
3. Check the log for errors and the frame count (`duration × fps`).

## Mux and QA
```bash
python3 kit/audio/finish.py mux renders/picture.mp4 audio/out/mix_master.wav deliver/Film_v1_70s.mp4
python3 kit/audio/finish.py qa deliver/*.mp4          # duration, size, fps, codec, frames, black/frozen scan, loudness
python3 kit/audio/finish.py sheet deliver/Film_v1_70s.mp4 qa.jpg --times 1,3.2,8,...
```
Compare the contact sheet with the approved storyboard frame by frame. Spot-check sync at the biggest hits (a slam, a
counter landing) by grabbing frames at the effect peaks.

## Deliver
- **Master:** H.264 High, 1080p, 30 fps, AAC 320k 48 kHz, `+faststart` (from the render, untouched picture).
- **Share versions** sized for messaging/upload limits:
  `python3 kit/audio/finish.py share master.mp4 mix_master.wav Film_share.mp4 --mb 29` (2-pass; keep 1080p — at ~3 Mbps
  1080p still beats 720p for line work and type).
- Credits + cue sheet (`credits.py`), and the storyboard link.
- Name files `Brand_Film-Name_vX.Y_70s.mp4`, `_30s`, `_15s`, `_share`.

## Hand-off for editing
The project folder (index.html + assets + hyperframes.json + meta.json + CLAUDE.md with project notes) opens in the
HyperFrames desktop app (File › Open Folder). Add a short brief to `CLAUDE.md` for any agent working there: chapter
timings, brand rules, allowed claims, "the soundtrack is a fixed mix — log timing changes in CHANGES.md".
