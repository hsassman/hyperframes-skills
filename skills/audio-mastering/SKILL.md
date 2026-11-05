---
name: audio-mastering
description: Masters voiceover and final mixed audio to YouTube's loudness standard (-14 LUFS integrated, -1 dBTP true peak) using two-pass ffmpeg-normalize, and cleans up background noise/room hiss using DeepFilterNet before mastering. Use this skill whenever a task involves finalizing audio for a video export, normalizing loudness, cleaning up a TTS or microphone recording, or anyone mentions LUFS, loudness, audio quality, or "the audio sounds off/noisy/quiet/inconsistent." This is the required last step on any audio track before it gets muxed into a final video — always run cleanup before normalization, never the reverse.
---

# Audio Mastering

Two-stage pipeline: denoise first, then loudness-normalize. Order matters —
normalizing before denoising will amplify noise along with the signal.

## Pipeline order (always this sequence)

1. **Denoise** raw voiceover/recording with DeepFilterNet
2. **Two-pass loudness normalize** the denoised file to -14 LUFS / -1 dBTP
3. Hand off the mastered file to `ffmpeg-processor` for muxing into the final video

## Step 1: Denoise with DeepFilterNet

Check it's installed first:
```bash
deep-filter --version
```
If missing, install per DeepFilterNet's official instructions (pip package or
precompiled `deep-filter` binary) — don't attempt to fake noise reduction with
a generic EQ/gate as a substitute; it's markedly worse for speech.

Run denoise:
```bash
deep-filter raw_voiceover.wav --output-dir ./denoised/
```
This produces `denoised/raw_voiceover_DeepFilterNet3.wav` (exact suffix depends
on installed model version — check the output directory for the actual filename).

Skip this step only if the source audio is already clean (e.g. output straight
from a well-tuned local TTS model with no background noise) — TTS output is
often clean enough to skip denoising, but always spot-check by ear first.

## Step 2: Two-pass loudness normalization

Use `ffmpeg-normalize` (Python CLI, wraps ffmpeg's `loudnorm` filter) rather than
hand-rolling single-pass loudnorm — two-pass is significantly more accurate
because it measures the actual input loudness first, then applies a precise
correction, instead of guessing from a running estimate.

Check it's installed:
```bash
ffmpeg-normalize --version
```

Run the pipeline standard — **-14 LUFS integrated, -1 dBTP true peak, 11 LU loudness range**:
```bash
ffmpeg-normalize denoised/raw_voiceover_DeepFilterNet3.wav \
  -o mastered_voiceover.wav \
  -t -14 \
  -tp -1.0 \
  -lrp 11 \
  -c:a pcm_s16le -ar 48000
```

Flags:
- `-t -14` — target integrated loudness in LUFS (YouTube's reference level — YouTube turns down louder content but does not boost quieter content, so hitting -14 exactly, not under it, matters)
- `-tp -1.0` — true peak ceiling in dBTP (prevents inter-sample clipping after YouTube's own encoding)
- `-lrp 11` — loudness range target in LU (keeps dynamics consistent, avoids overly squashed or overly wide dynamics)
- Output as 16-bit PCM WAV at 48kHz for a clean handoff to the video muxing step; convert to AAC only at final export (see `ffmpeg-processor` skill)

### Manual two-pass with raw ffmpeg (fallback if `ffmpeg-normalize` isn't available)

Pass 1 — measure:
```bash
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null -
```
Read the JSON output block (`input_i`, `input_tp`, `input_lra`, `input_thresh`,
`target_offset`) from stderr.

Pass 2 — apply, feeding the measured values back in:
```bash
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:linear=true:print_format=summary output.wav
```
Prefer the `ffmpeg-normalize` CLI over this manual approach when available — it
automates exactly this two-pass measure/apply sequence correctly.

## Verifying the result

Spot-check the mastered file's actual loudness before handing it off:
```bash
ffmpeg -i mastered_voiceover.wav -af loudnorm=print_format=summary -f null - 2>&1 | grep "Input Integrated"
```
Should read close to -14 LUFS. If it's meaningfully off (>0.5 LU), something in
the chain is wrong — re-check that step 1's denoised output was used as input
to step 2, not the raw file.

## When NOT to use this skill

- Don't use this for music/BGM tracks that should sit under narration — those
  typically get ducked to roughly -20 to -24 LUFS relative to the voiceover, not
  mastered to -14 LUFS themselves. Master the voiceover per this skill, then
  mix music underneath it at a lower level during final assembly.
