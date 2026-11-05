#!/usr/bin/env python3
"""
Generate word-level timestamped captions from an audio file using WhisperX.

Produces:
  - captions.srt        (standard segment-level SRT)
  - word_timings.json    (word-level start/end timestamps for Remotion)

Usage:
    python generate_captions.py --audio mastered_voiceover.wav --output-dir captions/ --language en
    python generate_captions.py --audio mastered_voiceover.wav --output-dir captions/ --language en --reference-text script.txt
"""
import argparse
import json
import os
import sys


def format_srt_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_timestamp(seg['start'])} --> {format_srt_timestamp(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")


def write_word_timings(segments, out_path):
    words = []
    for seg in segments:
        for w in seg.get("words", []):
            # whisperx sometimes omits start/end for punctuation-only tokens
            if "start" in w and "end" in w:
                words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--reference-text", default=None,
                         help="Optional path to the known script text, to constrain alignment instead of relying purely on ASR")
    parser.add_argument("--model", default="large-v2", help="WhisperX model size")
    parser.add_argument("--device", default="cuda", help="cuda or cpu")
    args = parser.parse_args()

    try:
        import whisperx
    except ImportError:
        print("whisperx is not installed. Install it before running this script: "
              "https://github.com/m-bain/whisperX", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    device = args.device
    compute_type = "float16" if device == "cuda" else "int8"

    print(f"Loading WhisperX model ({args.model}) on {device}...")
    model = whisperx.load_model(args.model, device, compute_type=compute_type, language=args.language)

    audio = whisperx.load_audio(args.audio)

    if args.reference_text:
        # Use the known script text as the transcript, skip ASR guessing,
        # and go straight to forced alignment for maximum accuracy.
        with open(args.reference_text, "r", encoding="utf-8") as f:
            ref_text = f.read().strip()
        print("Using provided reference text for alignment (skipping ASR transcription step)...")
        result = {"segments": [{"text": ref_text, "start": 0.0, "end": None}], "language": args.language}
    else:
        print("Transcribing...")
        result = model.transcribe(audio, language=args.language)

    print("Loading alignment model...")
    align_model, metadata = whisperx.load_align_model(language_code=args.language, device=device)

    print("Running forced alignment for word-level timestamps...")
    result_aligned = whisperx.align(result["segments"], align_model, metadata, audio, device)

    srt_path = os.path.join(args.output_dir, "captions.srt")
    json_path = os.path.join(args.output_dir, "word_timings.json")

    write_srt(result_aligned["segments"], srt_path)
    write_word_timings(result_aligned["segments"], json_path)

    print(f"Wrote {srt_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
