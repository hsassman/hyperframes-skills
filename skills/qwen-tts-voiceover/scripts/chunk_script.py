#!/usr/bin/env python3
"""
Sentence-aware script chunker for TTS input.

Splits a script into chunks that stay under a token budget without cutting
mid-sentence. Approximates token count via a simple word-based heuristic
(roughly 0.75 words per token for English) since exact tokenization depends
on the specific TTS model's tokenizer, which we don't need exact parity
with -- we just need a safe margin under the limit.

Usage:
    python chunk_script.py --input script.txt --output chunks/ --max-tokens 400
"""
import argparse
import os
import re
import sys


def split_sentences(text: str):
    """Split text into sentences, keeping the terminator attached."""
    # Split on sentence-ending punctuation followed by whitespace and a
    # capital letter or end of string. Keeps abbreviations like "Dr." from
    # being treated as hard splits in the common case, though not perfectly.
    sentence_pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\u201c])')
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences = []
    for para in paragraphs:
        parts = sentence_pattern.split(para)
        for i, part in enumerate(parts):
            part = part.strip()
            if part:
                sentences.append(part)
        sentences.append("")  # paragraph break marker
    # drop trailing marker
    if sentences and sentences[-1] == "":
        sentences.pop()
    return sentences


def estimate_tokens(text: str) -> int:
    words = len(text.split())
    return int(words / 0.75) + 1


def chunk_sentences(sentences, max_tokens: int):
    chunks = []
    current = []
    current_tokens = 0

    for sent in sentences:
        if sent == "":
            # paragraph break -- prefer to break chunk here if we have content
            if current:
                chunks.append(" ".join(current))
                current = []
                current_tokens = 0
            continue

        sent_tokens = estimate_tokens(sent)

        if sent_tokens > max_tokens:
            # single sentence exceeds budget on its own -- flush current,
            # emit it alone (caller should be warned)
            if current:
                chunks.append(" ".join(current))
                current = []
                current_tokens = 0
            chunks.append(sent)
            print(
                f"WARNING: a single sentence exceeds max-tokens ({sent_tokens} > {max_tokens}). "
                f"Emitted as its own chunk -- consider manually splitting it:\n  {sent[:100]}...",
                file=sys.stderr,
            )
            continue

        if current_tokens + sent_tokens > max_tokens:
            chunks.append(" ".join(current))
            current = [sent]
            current_tokens = sent_tokens
        else:
            current.append(sent)
            current_tokens += sent_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to script text file")
    parser.add_argument("--output", required=True, help="Output directory for chunk files")
    parser.add_argument("--max-tokens", type=int, default=400, help="Max estimated tokens per chunk")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    os.makedirs(args.output, exist_ok=True)

    sentences = split_sentences(text)
    chunks = chunk_sentences(sentences, args.max_tokens)

    for i, chunk in enumerate(chunks, start=1):
        out_path = os.path.join(args.output, f"chunk_{i:03d}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(chunk.strip() + "\n")

    print(f"Wrote {len(chunks)} chunks to {args.output}")
    for i, chunk in enumerate(chunks, start=1):
        print(f"  chunk_{i:03d}.txt: ~{estimate_tokens(chunk)} tokens, {len(chunk)} chars")


if __name__ == "__main__":
    main()
