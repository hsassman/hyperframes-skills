---
name: qwen-tts-voiceover
description: Generates voiceover narration from a script using the self-hosted Qwen TTS service, handling the sentence/paragraph chunking and audio stitching required because long-form narration is Qwen TTS's weakest area (quality and prosody drift on long inputs, and the model has a per-request input limit). Use this skill whenever a task involves converting a written script into voiceover audio, generating narration for a video, or anyone mentions TTS, voiceover, narration audio, or voice generation in this pipeline. Always chunk long scripts through this skill rather than sending the full script to the TTS endpoint in one request.
---

# Qwen TTS Voiceover

Wraps the self-hosted Qwen TTS service. The core risk this skill manages:
Qwen TTS's documented weak point is long-form narration — quality and voice
consistency degrade over long single requests, and the hosted API caps input
at 512 tokens per request (the same practical limit applies to self-hosted use
for quality reasons even without a hard cap). Never send an entire multi-minute
script as one TTS request — always chunk first.

## Pipeline

1. **Chunk** the script into TTS-safe segments (sentence/paragraph boundaries, not mid-sentence)
2. **Generate** audio per chunk against the local Qwen TTS service, using a fixed voice/speaker across all chunks
3. **Stitch** chunks together with small silence padding at joins
4. **Normalize** each chunk's level before stitching so joins don't have audible volume jumps (or normalize once after stitching — either works, just be consistent)
5. Hand the stitched file to the `audio-mastering` skill for denoise + loudness normalization — this skill's output is a stitched draft, not the final mastered file

## Step 1: Chunk the script

Use `scripts/chunk_script.py` (bundled) rather than chunking by raw character
count — it splits on sentence boundaries and keeps chunks under a safe token
budget, which avoids both mid-sentence cuts (audible glitches) and hitting any
length limits.

```bash
python scripts/chunk_script.py --input script.txt --output chunks/ --max-tokens 400
```

This produces `chunks/chunk_001.txt`, `chunks/chunk_002.txt`, etc. The
400-token default leaves headroom under the 512-token API limit; lower it
further (e.g. 250–300) if you notice quality dropping even within that budget
during self-hosted generation — the 512 figure is the hosted API's hard cap,
not necessarily the point where self-hosted quality is still fully reliable.

## Step 2: Generate audio per chunk

Call your local Qwen TTS service once per chunk file, using the **same voice
ID / cloned voice reference** for every chunk in a script — switching voices
mid-script (even accidentally, e.g. by omitting the voice parameter on some
calls) is the most common cause of jarring inconsistency.

Confirm the service is reachable before starting a full run:
```bash
curl -s http://localhost:<PORT>/health || echo "Qwen TTS service not responding — check it's running before proceeding"
```

(Ask the user for their actual service endpoint/port and invocation method if
not already known from the project setup — this varies by how they deployed
it locally, e.g. a FastAPI wrapper, ComfyUI-style node, or direct Python
script.)

Generate each chunk to `audio/chunk_001.wav`, `audio/chunk_002.wav`, etc.,
matching the chunk numbering from step 1.

## Step 3: Stitch with padding

Use `scripts/stitch_audio.sh` (bundled, wraps ffmpeg) to concatenate chunks
with a short silence gap at each join — this smooths over any residual prosody
discontinuity between chunks and gives natural-sounding pauses at what were
originally sentence/paragraph breaks anyway:

```bash
bash scripts/stitch_audio.sh audio/ stitched_voiceover.wav --gap-ms 150
```

## Step 4: Level-match before stitching (if doing it per-chunk)

If individual chunks come out at noticeably different volumes (check by ear or
with `ffmpeg -i chunk.wav -af volumedetect -f null -` on a couple of samples),
normalize each chunk to a common peak level before stitching:
```bash
ffmpeg -i chunk_001.wav -af "loudnorm=I=-16:TP=-1.5:print_format=summary" chunk_001_matched.wav
```
This is a rough pre-match only — the real, precise -14 LUFS mastering pass
happens afterward via the `audio-mastering` skill on the full stitched file,
so don't over-engineer this step.

## Handoff

Once stitched, pass `stitched_voiceover.wav` to the `audio-mastering` skill.
Do not treat this skill's raw stitched output as final — it hasn't been
denoised or precisely loudness-normalized yet.

## When NOT to use this skill

- Don't use for short single-line audio (e.g. a single title card VO under
  ~30 seconds / well under the token budget) — just call the TTS service
  directly with one request, no chunking needed.
- If quality remains unacceptably inconsistent even with careful chunking,
  that's a signal to fall back to a different TTS provider for that
  script rather than over-tuning chunk size — flag this to the user rather
  than silently degrading output quality.

## Reference files

- `scripts/chunk_script.py` — sentence-aware script chunker with a token budget
- `scripts/stitch_audio.sh` — ffmpeg-based concatenation with silence padding between chunks
