# Media audit and preparation

1. **Inventory** every clip and photo: `ffprobe` for duration/fps/resolution/audio, then a contact sheet
   (`kit/audio/finish.py sheet clip.mp4 sheet.jpg --times ...`). Note what each shows, usable ranges, and problems
   (shake, exposure, faces, sensitive info, other brands' logos).
2. **Pick per beat** — the clearest frame of each process step. Prefer motion (hands, machines) for video windows, stills
   for polaroids/frames. Real media is the proof; never substitute generated imagery for the product or process.
3. **Transcode** clips for the composition: H.264, 1080p or the window size ×1.5, audio stripped, keyframe every 1 s:
   `ffmpeg -i in.mov -an -c:v libx264 -crf 18 -preset slow -g 30 -pix_fmt yuv420p -vf scale=1920:-2 assets/V1.mp4`.
   Videos in the composition are always `muted`.
4. **Clean photos** deterministically: `python3 kit/assets/prep.py cleanup in.jpg out.jpg` (denoise, neutral highlights,
   local contrast, light sharpen; framing untouched). Image models may be used to clean photos **only** when nothing in
   frame carries text, labels or logos — and you must compare framing and details against the original before using it.
5. **Freeze frames:** if a clip ends before its window, export its last frame (`ffmpeg -sseof -0.05 -i v.mp4 -frames:v 1 v_last.jpg`)
   and place it under the video so the window never goes empty.
6. **Licensing:** stock footage and photos only from licensed sources (Pexels and Pixabay APIs; see `references/tools-and-sources.md`), with a licence note per file. Never download from YouTube or general web search results.
