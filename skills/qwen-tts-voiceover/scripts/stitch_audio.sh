#!/usr/bin/env bash
# Stitch numbered TTS chunk audio files together with a silence gap between
# each, using ffmpeg's concat filter (re-encodes, safe for chunks generated
# in separate TTS calls that may not be byte-identical in format).
#
# Usage:
#   bash stitch_audio.sh <input_dir> <output_file> [--gap-ms 150]
#
# Expects input_dir to contain files matching chunk_*.wav (or .mp3), sorted
# in the order they should be concatenated.

set -euo pipefail

INPUT_DIR=""
OUTPUT_FILE=""
GAP_MS=150

# simple arg parsing
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gap-ms)
      GAP_MS="$2"
      shift 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
set -- "${POSITIONAL[@]}"

INPUT_DIR="$1"
OUTPUT_FILE="$2"

if [[ -z "$INPUT_DIR" || -z "$OUTPUT_FILE" ]]; then
  echo "Usage: bash stitch_audio.sh <input_dir> <output_file> [--gap-ms 150]"
  exit 1
fi

FILES=($(ls "$INPUT_DIR"/chunk_*.wav 2>/dev/null | sort))
if [[ ${#FILES[@]} -eq 0 ]]; then
  FILES=($(ls "$INPUT_DIR"/chunk_*.mp3 2>/dev/null | sort))
fi
if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No chunk_*.wav or chunk_*.mp3 files found in $INPUT_DIR"
  exit 1
fi

echo "Found ${#FILES[@]} chunk audio files to stitch."

GAP_SEC=$(awk "BEGIN { printf \"%.3f\", $GAP_MS / 1000 }")

# Build a silence file matching the sample rate/channels of the first chunk
SAMPLE_RATE=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 "${FILES[0]}")
CHANNELS=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "${FILES[0]}")

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

SILENCE_FILE="$TMP_DIR/silence.wav"
ffmpeg -y -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=${SAMPLE_RATE}" \
  -t "$GAP_SEC" -ac "$CHANNELS" "$SILENCE_FILE" -loglevel error

LIST_FILE="$TMP_DIR/list.txt"
> "$LIST_FILE"
for i in "${!FILES[@]}"; do
  # normalize each chunk to a consistent intermediate wav first (re-encode
  # avoids concat issues if TTS output formats vary slightly between calls)
  NORM_FILE="$TMP_DIR/norm_$(printf '%03d' "$i").wav"
  ffmpeg -y -i "${FILES[$i]}" -ar "$SAMPLE_RATE" -ac "$CHANNELS" -c:a pcm_s16le "$NORM_FILE" -loglevel error
  echo "file '$NORM_FILE'" >> "$LIST_FILE"
  if [[ $i -lt $((${#FILES[@]} - 1)) ]]; then
    echo "file '$SILENCE_FILE'" >> "$LIST_FILE"
  fi
done

ffmpeg -y -f concat -safe 0 -i "$LIST_FILE" -c:a pcm_s16le "$OUTPUT_FILE" -loglevel error

echo "Stitched ${#FILES[@]} chunks with ${GAP_MS}ms gaps into: $OUTPUT_FILE"
