# Concatenating mismatched clips

Stream-copy concat (`-f concat -c copy`) only works when every input file shares
identical codec, resolution, frame rate, and pixel format. Sourced stock footage
rarely matches these exactly across providers, so use the `concat` filter graph
instead, which re-encodes and can normalize mismatched inputs on the way through.

## Filter-graph concat with normalization

```bash
ffmpeg \
  -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 \
  -filter_complex "
    [0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];
    [1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];
    [2:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v2];
    [0:a]aresample=48000[a0];
    [1:a]aresample=48000[a1];
    [2:a]aresample=48000[a2];
    [v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[outv][outa]
  " \
  -map "[outv]" -map "[outa]" -c:v libx264 -crf 18 -c:a aac output.mp4
```

This scales/pads every clip to a common resolution (1920x1080 here — adjust to
your target), forces a common frame rate (30fps here), resamples audio to a
common sample rate, then concatenates. Adjust the target resolution/fps to
match your project's output spec (e.g. use 3840x2160 for a 4K timeline).

## Clips with no audio track

If a source clip has no audio stream (common with silent stock footage), add a
silent track before concatenating so the filter graph doesn't fail on a missing
`[N:a]` input:

```bash
ffmpeg -i silent_clip.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
  -c:v copy -c:a aac -shortest silent_clip_with_audio.mp4
```

Run this as a pre-processing pass on any clip missing audio before feeding it
into the concat filter graph above.
