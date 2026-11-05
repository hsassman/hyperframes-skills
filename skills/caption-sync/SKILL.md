---
name: caption-sync
description: Generates word-level timestamped captions from a voiceover audio file using WhisperX, producing both SRT subtitle files and a JSON word-timing format that Remotion can consume for karaoke-style animated captions and for timing visual cut points to speech. Use this skill whenever a task involves generating captions/subtitles, syncing text to audio, timing Remotion overlays to narration, or anyone mentions captions, subtitles, word timing, or transcript alignment. Always run this on the final MASTERED voiceover (after audio-mastering), not the raw or stitched draft, so caption timing matches what viewers actually hear.
---

# Caption Sync

Wraps WhisperX to produce word-level timestamps from a voiceover track. This
is what makes karaoke-style animated captions and speech-synced visual cuts
possible in HyperFrames or Remotion — plain Whisper only gives segment-level timing, which
is too coarse for word-by-word caption animation.

## When to run this

Run AFTER the `audio-mastering` skill, on the final mastered voiceover file —
not on the raw TTS output or the stitched-but-unmastered draft. Timing should
be derived from the exact audio that ends up in the final video; mastering
(denoise/normalize) doesn't change timing, but always sourcing from the final
file avoids any risk of drift if the mastering step ever trims silence or
otherwise adjusts length.

## Step 1: Confirm WhisperX is available

```bash
python -c "import whisperx" 2>&1 || echo "WhisperX not installed -- install per https://github.com/m-bain/whisperX before proceeding"
```

Note: WhisperX's alignment step pulls wav2vec2 forced-alignment models from
Hugging Face, some of which are gated (require accepting terms on the HF
model page and an HF access token). If alignment fails with an auth error,
tell the user to accept the model terms on Hugging Face and set `HF_TOKEN`,
rather than silently falling back to unaligned (segment-only) output.

## Step 2: Run transcription + alignment

Use `scripts/generate_captions.py` (bundled):

```bash
python scripts/generate_captions.py --audio mastered_voiceover.wav --output-dir captions/ --language en
```

This produces:
- `captions/captions.srt` — standard SRT subtitle file (segment-level, for platforms/tools that only accept SRT)
- `captions/word_timings.json` — word-level timestamps: `[{"word": "Hello", "start": 0.12, "end": 0.34}, ...]`

Since the script came from a known text source (the TTS script, possibly
already chunked by `qwen-tts-voiceover`), you can optionally pass
`--reference-text script.txt` to constrain alignment to the known script text
rather than relying purely on ASR transcription — this improves accuracy
since WhisperX doesn't have to guess what was said, only when.

## Step 3: Feed word timings into the composition (HyperFrames or Remotion)

The `word_timings.json` format is deliberately simple so it can be imported
directly into a HyperFrames or Remotion composition and mapped to frame numbers:

```javascript
const frame = Math.round(word.start * fps);
```

Use this to drive:
- Karaoke-style caption highlighting (one word active at a time)
- Timing cut points between B-roll clips to land on natural speech pauses
- Triggering overlay animations (arrows, callouts) exactly when a relevant word is spoken

## Verifying alignment quality

Spot check a handful of words in `word_timings.json` against the audio by ear
(or waveform) before treating it as ground truth — forced alignment is
generally reliable but can drift on TTS voices with unusual pacing or on
audio with residual noise. If timings look off, confirm the mastered
(denoised) file was used as input, not a noisy raw take.

## When NOT to use this skill

- Don't use this for languages other than what WhisperX's alignment models
  support well — verify language support before assuming word-level accuracy
  for non-English scripts.
- Don't run this before mastering — see note above.

## Reference files

- `scripts/generate_captions.py` — runs WhisperX transcription + forced alignment, outputs SRT + word-level JSON
