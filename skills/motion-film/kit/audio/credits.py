"""Write the audio credits + cue sheet (markdown) from cues.json and your sources list.

    python3 credits.py cues.json sources.json out.md [--title "Film name"] [--music "Track by Artist (licence, url)"]
sources.json: [{"file": "whoosh_07.mp3", "title": "Slow Swoosh by Artist", "url": "https://...", "licence": "Pixabay Content License"}, ...]
Keep a sources entry for every recording you download, at download time — licences and URLs are hard to recover later."""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("cues"); ap.add_argument("sources"); ap.add_argument("out")
ap.add_argument("--title", default="Film"); ap.add_argument("--music", default="")
ap.add_argument("--master", default="", help='e.g. "-14.0 LUFS, -2.3 dBTP, LRA 5.0 LU"')
a = ap.parse_args()
cues = json.load(open(a.cues))["cues"]
src = {s["file"]: s for s in json.load(open(a.sources))}
used = sorted({c["file"] for c in cues})
L = [f"# Audio credits and cue sheet: {a.title}", ""]
if a.music:
    L += ["## Music", f"- {a.music}", ""]
L += ["## Sound effects"]
for f_ in used:
    s = src.get(f_, {})
    L.append(f"- `{f_}`: {s.get('title', '[CONFIRM title]')}. {s.get('licence', '[CONFIRM licence]')}. {s.get('url', '')}")
if a.master:
    L += ["", "## Master", f"- {a.master}"]
L += ["", "## Cue sheet (film seconds)", "| in | out | sound | role | what it marks |", "|---|---|---|---|---|"]
for c in sorted(cues, key=lambda c: c["t"]):
    L.append(f"| {c['t']:.2f} | {c['end']:.2f} | {c['file']} | {c['role']} | {c['note']} |")
open(a.out, "w").write("\n".join(L) + "\n")
print("wrote", a.out, len(used), "sources,", len(cues), "cues")
