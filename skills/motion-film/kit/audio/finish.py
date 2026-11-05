"""Mux, QA and share-encode finished films.

  python3 finish.py mux picture.mp4 master.wav out.mp4            # picture copied untouched, AAC 320k, +faststart
  python3 finish.py qa out.mp4 [more.mp4 ...]                       # specs, black/frozen scan, loudness, frame count
  python3 finish.py share in.mp4 master.wav out_share.mp4 --mb 29   # 2-pass H.264 sized under a messaging/upload limit
  python3 finish.py sheet in.mp4 sheet.jpg --times 1,3.2,8,...      # contact sheet of stills for visual QA
"""
import argparse, json, os, re, subprocess


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def mux(pic, wav, out):
    run(["ffmpeg", "-v", "error", "-y", "-i", pic, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
         "-ar", "48000", "-movflags", "+faststart", out])
    print(out, round(os.path.getsize(out) / 1e6, 1), "MB")


def qa(paths):
    for p in paths:
        j = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels:format=duration,size",
                            "-of", "json", p]).stdout)
        bd = run(["ffmpeg", "-hide_banner", "-i", p, "-vf", "blackdetect=d=0.12:pix_th=0.06", "-an", "-f", "null", "-"]).stderr
        fz = run(["ffmpeg", "-hide_banner", "-i", p, "-vf", "freezedetect=n=0.0008:d=1.6", "-an", "-f", "null", "-"]).stderr
        lo = run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
        tail = lo[lo.rindex("Summary:"):] if "Summary:" in lo else ""
        loud = " ".join(x.strip() for x in tail.splitlines() if x.strip().startswith(("I:", "LRA:", "Peak:")))
        v = [s for s in j["streams"] if s.get("width")][0]; a = [s for s in j["streams"] if s.get("sample_rate")]
        print(f"{os.path.basename(p)}: {float(j['format']['duration']):.3f}s {v['width']}x{v['height']} {v['r_frame_rate']} {v['codec_name']} "
              f"frames={v.get('nb_frames')} | {(a[0]['codec_name'] + ' ' + a[0]['sample_rate'] + 'Hz') if a else 'no audio'} | "
              f"{int(j['format']['size']) / 1e6:.1f} MB | {loud}")
        print("   black:", [l.split('] ')[-1] for l in bd.splitlines() if 'black_start' in l] or "none",
              "| frozen:", [l.split('] ')[-1] for l in fz.splitlines() if 'freeze_start' in l] or "none")


def share(src, wav, out, mb=29.0, audio_k=192, scale=None):
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).stdout)
    vk = int(mb * 8 * 1024 * 1024 / dur / 1000 * 0.97 - audio_k)
    vf = ["-vf", f"scale={scale}:flags=lanczos"] if scale else []
    common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.5)}k", "-bufsize", f"{vk * 2}k", "-pix_fmt", "yuv420p", "-profile:v", "high"]
    log = out + ".2pass"
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an"] + vf + common + ["-pass", "1", "-passlogfile", log, "-f", "mp4", os.devnull])
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", wav, "-map", "0:v", "-map", "1:a"] + vf + common +
        ["-pass", "2", "-passlogfile", log, "-c:a", "aac", "-b:a", f"{audio_k}k", "-ar", "48000", "-movflags", "+faststart", out])
    for f in os.listdir(os.path.dirname(os.path.abspath(out))):
        if f.startswith(os.path.basename(log)):
            os.remove(os.path.join(os.path.dirname(os.path.abspath(out)), f))
    print(out, round(os.path.getsize(out) / 1e6, 1), "MB at", vk, "kbps video")


def sheet(src, out, times, cols=4, w=640):
    from PIL import Image, ImageDraw
    h = w * 9 // 16; rows = (len(times) + cols - 1) // cols
    sh = Image.new("RGB", (cols * w, rows * (h + 24)), "black"); d = ImageDraw.Draw(sh)
    tmp = out + ".frame.jpg"
    for i, t in enumerate(times):
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf", f"scale={w}:{h}", tmp])
        x, y = (i % cols) * w, (i // cols) * (h + 24); sh.paste(Image.open(tmp), (x, y + 24)); d.text((x + 6, y + 5), f"{t:.2f}s", fill="white")
    os.remove(tmp); sh.save(out, quality=85); print(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("op", choices=["mux", "qa", "share", "sheet"]); ap.add_argument("paths", nargs="+")
    ap.add_argument("--mb", type=float, default=29.0); ap.add_argument("--scale"); ap.add_argument("--times", default="")
    a = ap.parse_args()
    if a.op == "mux":
        mux(*a.paths[:3])
    elif a.op == "qa":
        qa(a.paths)
    elif a.op == "share":
        share(a.paths[0], a.paths[1], a.paths[2], a.mb, scale=a.scale)
    else:
        sheet(a.paths[0], a.paths[1], [float(t) for t in a.times.split(",") if t])
