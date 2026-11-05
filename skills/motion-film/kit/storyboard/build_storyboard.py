"""Storyboard from the composition itself: snapshot real frames at chosen times and lay them out with captions.

    python3 build_storyboard.py spec.json path/to/project out_dir [--no-snap]

spec.json:
{
  "title": "Northwind demo", "eyebrow": "Brand film · v1 storyboard",
  "lede": "Every frame is a still pulled from the composition. Approve it or say which frames to change.",
  "meta": ["20 s · 1920×1080 · 30 fps", "Music: ...", "No voice-over"],
  "chapters": [
    {"num": "00", "name": "Seed", "span": "0:00 – 0:06",
     "frames": [{"t": 1.2, "title": "Hook", "text": "What happens and why.", "sound": "soft wind", "transition": false, "badge": "New"}]}
  ],
  "notes": ["Anything the reviewer must confirm."]
}
Frames are snapshotted with the HyperFrames CLI (needs Chrome; set PRODUCER_HEADLESS_SHELL_PATH on Linux), saved as
1280×720 JPEGs, and index.html is self-contained apart from frames/. Publish the folder as a page (e.g. a Claude artifact
with the frames as supporting files) so reviewers can check it on a phone."""
import argparse, glob, html, json, os, shutil, subprocess

CSS = """
:root{--bg:#F7F4EE;--surface:#FFFFFF;--ink:#1D2328;--muted:#5B6670;--line:#E4DED3;--accent:#B4561A}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121619;--surface:#1B2125;--ink:#ECE8E1;--muted:#A5AEB5;--line:#2C343A;--accent:#F0955A}}
:root[data-theme=dark]{--bg:#121619;--surface:#1B2125;--ink:#ECE8E1;--muted:#A5AEB5;--line:#2C343A;--accent:#F0955A}
*{box-sizing:border-box;margin:0}body{background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;padding:32px 16px 64px}
main{max-width:1180px;margin:0 auto}.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{font-size:clamp(30px,5vw,48px);line-height:1.1;margin:8px 0 12px}.lede{color:var(--muted);max-width:760px}
.meta{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px;padding:0;list-style:none}.meta li{border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:13px;color:var(--muted)}
.chapter{margin-top:44px}.ch-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:12px;border-bottom:1px solid var(--line);padding-bottom:8px;margin-bottom:16px}
.ch-num{font-weight:800;color:var(--accent)}.ch-head h2{font-size:22px}.ch-time{color:var(--muted);font-size:14px}
.frames{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:20px}
figure{background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.shot{position:relative}.shot img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover}
.tc{position:absolute;left:10px;top:10px;background:rgba(0,0,0,.65);color:#fff;font-size:12px;font-weight:600;border-radius:6px;padding:3px 8px}
.kind{position:absolute;right:10px;top:10px;background:rgba(0,0,0,.65);color:#fff;font-size:11px;letter-spacing:.08em;text-transform:uppercase;border-radius:6px;padding:3px 8px}
figcaption{padding:14px 16px 16px}figcaption h3{font-size:16px;margin-bottom:4px}figcaption p{color:var(--muted);font-size:14px}
.snd{margin-top:8px}.snd b{color:var(--ink);font-weight:600}
.badge{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#fff;background:var(--accent);border-radius:999px;padding:2px 8px;margin-right:6px;vertical-align:2px}
.notes{margin-top:48px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted)}.notes li{margin:6px 0 6px 18px}
"""


def snap(project, times, out):
    env = dict(os.environ)
    cmd = ["npx", "--yes", "hyperframes", "snapshot", "--at", ",".join(f"{t:g}" for t in times), "--no-end", "-o", out, "--timeout", "25000"]
    subprocess.run(cmd, cwd=project, env=env, check=True)
    return sorted(glob.glob(os.path.join(out, "frame-*.png")), key=lambda p: float(p.rsplit("-at-", 1)[1].rstrip("s.png") or 0))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("project"); ap.add_argument("out"); ap.add_argument("--no-snap", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec)); os.makedirs(os.path.join(a.out, "frames"), exist_ok=True)
    frames = [fr for ch in spec["chapters"] for fr in ch["frames"]]
    if not a.no_snap:
        from PIL import Image
        tmp = os.path.join(a.out, "_snaps"); shutil.rmtree(tmp, ignore_errors=True)
        shots = snap(os.path.abspath(a.project), [fr["t"] for fr in frames], os.path.abspath(tmp))
        for i, (fr, p) in enumerate(zip(frames, shots)):
            name = f"frames/f{i + 1:02d}.jpg"; fr["img"] = name
            Image.open(p).convert("RGB").resize((1280, 720), Image.LANCZOS).save(os.path.join(a.out, name), quality=80, optimize=True, progressive=True)
        shutil.rmtree(tmp, ignore_errors=True)
    e = html.escape
    tc = lambda t: f"{int(t // 60)}:{t % 60:04.1f}"
    out = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
           f"<title>{e(spec['title'])} storyboard</title><style>{CSS}</style></head><body><main>",
           f"<div class='eyebrow'>{e(spec.get('eyebrow', 'Storyboard'))}</div><h1>{e(spec['title'])}</h1><p class='lede'>{e(spec.get('lede', ''))}</p>",
           "<ul class='meta'>" + "".join(f"<li>{e(m)}</li>" for m in spec.get("meta", [])) + "</ul>"]
    for ch in spec["chapters"]:
        out.append(f"<section class='chapter'><div class='ch-head'><span class='ch-num'>{e(ch.get('num', ''))}</span><h2>{e(ch['name'])}</h2><span class='ch-time'>{e(ch.get('span', ''))}</span></div><div class='frames'>")
        for fr in ch["frames"]:
            badge = f"<span class='badge'>{e(fr['badge'])}</span>" if fr.get("badge") else ""
            kind = "<span class='kind'>Transition</span>" if fr.get("transition") else ""
            snd = f"<p class='snd'><b>Sound</b> {e(fr['sound'])}</p>" if fr.get("sound") else ""
            out.append(f"<figure><div class='shot'><img src='{fr.get('img', '')}' alt='{e(fr.get('title', ''))}' loading='lazy'><span class='tc'>{tc(fr['t'])}</span>{kind}</div>"
                       f"<figcaption><h3>{badge}{e(fr.get('title', ''))}</h3><p>{e(fr.get('text', ''))}</p>{snd}</figcaption></figure>")
        out.append("</div></section>")
    if spec.get("notes"):
        out.append("<section class='notes'><ul>" + "".join(f"<li>{e(n)}</li>" for n in spec["notes"]) + "</ul></section>")
    out.append("</main></body></html>")
    open(os.path.join(a.out, "index.html"), "w").write("".join(out))
    print("wrote", os.path.join(a.out, "index.html"), len(frames), "frames")


if __name__ == "__main__":
    main()
