---
name: ffmpeg-processor
description: Wraps FFmpeg for all raw video/audio manipulation in a video production pipeline — trimming, concatenating, transcoding, extracting audio, muxing tracks together, overlaying images/subtitles, and probing media metadata. Use this skill whenever a task involves cutting clips to length, joining multiple video/audio files, converting between formats/codecs/resolutions, pulling the audio track out of a video, burning in subtitles, or combining a separately-rendered Remotion or HyperFrames overlay with sourced footage or a voiceover track. This is the low-level media-manipulation layer underneath the rest of the pipeline — reach for it before writing custom video/audio code by hand.
---

# FFmpeg Processor

FFmpeg CLI wrapper for deterministic media operations. Always confirm `ffmpeg -version` works before running pipeline steps — if it's missing, tell the user to install it rather than trying to work around it.

## Core principles

- Never guess codec/container compatibility — check with `ffprobe` first if unsure.
- Prefer stream copy (`-c copy`) when no re-encode is needed (e.g. simple trims on keyframe boundaries, concatenation of identical formats) — it's lossless and near-instant.
- Re-encode explicitly when formats differ or frame-accurate cuts are needed. Use `-c:v libx264 -crf 18 -preset slow` for high-quality H.264, or `-c:v libx265` for smaller 4K files.
- Always specify `-pix_fmt yuv420p` on final exports for broad compatibility (YouTube, most players).
- For anything destined for YouTube, target these container/codec combos: MP4 (H.264/H.265 video + AAC audio) up to 4K.

## Common operations

### Probe a file (always do this first for unknown inputs)
```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```
Use this to check resolution, frame rate, codec, duration, and audio sample rate before deciding on re-encode settings.

### Trim a clip
Frame-accurate (re-encodes, slower but exact):
```bash
ffmpeg -i input.mp4 -ss 00:00:10.500 -to 00:00:25.000 -c:v libx264 -crf 18 -c:a aac output.mp4
```
Fast (keyframe-snapped, no re-encode — only use when exact frame accuracy isn't required):
```bash
ffmpeg -ss 00:00:10 -i input.mp4 -to 00:00:25 -c copy output.mp4
```

### Concatenate clips (same codec/resolution)
Create a list file `list.txt`:
```
file 'clip1.mp4'
file 'clip2.mp4'
file 'clip3.mp4'
```
Then:
```bash
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```
If clips differ in codec/resolution/fps, re-encode instead using the `concat` filter (see `references/concat-filter.md`) rather than stream-copy concat, which will produce broken output on mismatched inputs.

### Extract audio from video
```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 48000 -ac 2 audio.wav
```

### Mux a new audio track onto video (e.g. attaching mastered voiceover to visuals)
```bash
ffmpeg -i video.mp4 -i voiceover_mastered.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest output.mp4
```
`-shortest` truncates to the shorter of the two streams — remove it if you've already matched durations upstream (e.g. in Remotion) and want to catch length mismatches as errors instead.

### Overlay a transparent layer rendered by HyperFrames or Remotion (e.g. captions/arrows/callouts) onto source footage
If the composition tool rendered a transparent-background WebM/ProRes overlay:
```bash
ffmpeg -i background.mp4 -i overlay.mov -filter_complex "[0:v][1:v]overlay=0:0" -c:a copy output.mp4
```

### Burn in subtitles (SRT) hard-coded into the video
```bash
ffmpeg -i input.mp4 -vf "subtitles=captions.srt" -c:a copy output.mp4
```
Prefer soft captions (rendered in the composition, timed via WhisperX) for style flexibility; only hard-burn as a fallback or for platforms that don't support styled captions.

### Resize / change resolution
```bash
ffmpeg -i input.mp4 -vf "scale=3840:2160:flags=lanczos" -c:v libx264 -crf 18 output_4k.mp4
```

### Final YouTube-ready export settings
```bash
ffmpeg -i input.mp4 -c:v libx264 -profile:v high -crf 16 -preset slow \
  -pix_fmt yuv420p -c:a aac -b:a 384k -ar 48000 -movflags +faststart \
  output_final.mp4
```
`-movflags +faststart` moves the moov atom to the front so the file starts playing/uploading before fully downloaded — always include this on final exports.

## When NOT to use this skill

- Don't use FFmpeg for programmatic animation/overlay creation (arrows, circles, animated captions) — that belongs in the composition tool (HyperFrames, Remotion). FFmpeg only composites/muxes what Remotion (or other tools) already rendered.
- Don't use this for loudness normalization — see the `audio-mastering` skill, which wraps `ffmpeg-normalize` with the pipeline's fixed -14 LUFS standard.

## Reference files

- `references/concat-filter.md` — how to concatenate clips with mismatched codecs/resolutions using the `concat` filter graph instead of stream-copy concat.
