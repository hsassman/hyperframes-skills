"""Cut-downs (e.g. 30 s / 15 s) assembled from the hero render — no re-render.

Picture: frame-accurate segments of the hero picture, every cut on a bar line of the cut-down's own music edit.
Music:   the original track re-edited on its bar lines (equal-power crossfades that END on the downbeat).
Effects: the hero's effects stem cut on the same frames, re-levelled against the new music underneath.

Config (JSON):
{
  "hero_picture": "renders/hero_picture.mp4", "track": "music/track.mp3",
  "sfx_stem": "audio/out/sfx_stem.wav", "music_stem": "audio/out/music_stem.wav",
  "fade_color": "0x0F2A33", "out": "audio/out",
  "cuts": {
    "30": {"segs": [[0.4, 4.4], [16.4, 18.4], ...], "music": [[4.4, 26.4], [122.4, 130.4]], "fade_in": 0.15, "fade_out": 0.6},
    "15": {"segs": [[1.4, 4.4], ...], "music": [[115.4, 130.4]], "fade_in": 0.25, "fade_out": 0.5}
  }
}
Rules for choosing segments: start segments at bar lines where no transition is mid-flight; let a segment END with a
transition so the next hard cut lands on its downbeat; put the payoff on the music's strongest phrase start; give the
end card >= 3 s after its last element lands. Total = sum of segment lengths and must equal the music edit length.

    python3 cutdowns.py config.json audio     # cutNN_pre.wav, cutNN_sfx.wav, cutNN_master.wav
    python3 cutdowns.py config.json picture   # cutNN_picture.mp4 (verifies frame count)
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from master import master  # noqa: E402
SR = 48000


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def splice(src, ranges, xf=0.06):
    n_xf = int(xf * SR); out = None
    for a, b in ranges:
        i0, i1 = int(round(a * SR)), int(round(b * SR)); seg = src[i0:i1].copy()
        if out is None:
            out = seg; continue
        pre = src[max(0, i0 - n_xf):i0].copy(); k = len(pre); t = np.linspace(0, 1, k)[:, None]
        out[-k:] = out[-k:] * np.cos(t * np.pi / 2) + pre * np.sin(t * np.pi / 2)
        out = np.vstack([out, seg])
    return out


def local_db(x, w=1.5):
    m = (x ** 2).mean(1); n = int(w * SR); c = np.cumsum(np.r_[0, m])
    idx = np.clip(np.arange(len(m)) - n // 2, 0, max(0, len(m) - n)); s = (c[idx + n] - c[idx]) / n
    return 10 * np.log10(s + 1e-12)


def audio(cfg, key):
    c = cfg["cuts"][key]; total = sum(b - a for a, b in c["segs"]); N = int(round(total * SR))
    mus = splice(decode(cfg["track"]), c["music"])
    mus = mus[:N] if len(mus) >= N else np.vstack([mus, np.zeros((N - len(mus), 2), np.float32)])
    fi = int(c.get("fade_in", 0.15) * SR); mus[:fi] *= np.linspace(0, 1, fi)[:, None]
    hero_sfx, _ = sf.read(cfg["sfx_stem"], dtype="float32"); hero_mus, _ = sf.read(cfg["music_stem"], dtype="float32")
    hero_ref = local_db(hero_mus)
    sfx = splice(hero_sfx, c["segs"], xf=0.012)[:N]
    ht = np.concatenate([np.arange(int(round(a * SR)), int(round(b * SR))) for a, b in c["segs"]])[:N]
    corr = np.clip(local_db(mus) - hero_ref[np.clip(ht, 0, len(hero_ref) - 1)], -8.0, 3.0)
    k = int(0.3 * SR); corr = np.convolve(corr, np.ones(k) / k, "same")
    sfx = sfx * (10 ** (corr / 20))[:, None].astype(np.float32)
    out = cfg.get("out", "."); os.makedirs(out, exist_ok=True)
    pre = os.path.join(out, f"cut{key}_pre.wav"); sf.write(pre, mus + sfx, SR, subtype="FLOAT")
    sf.write(os.path.join(out, f"cut{key}_sfx.wav"), sfx, SR, subtype="FLOAT")
    print(key, json.dumps(master(pre, os.path.join(out, f"cut{key}_master.wav"), c.get("fade_out", 0.6))))


def picture(cfg, key):
    c = cfg["cuts"][key]; total = sum(b - a for a, b in c["segs"]); ins, labels = [], []
    for i, (a, b) in enumerate(c["segs"]):
        ins += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", cfg["hero_picture"]]; labels.append(f"[{i}:v]")
    fo = c.get("fade_out", 0.6)
    fc = f"{''.join(labels)}concat=n={len(labels)}:v=1:a=0,fade=t=out:st={total - fo:.3f}:d={fo}:color={cfg.get('fade_color', 'black')},format=yuv420p[v]"
    out = os.path.join(cfg.get("out", "."), f"cut{key}_picture.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[v]", "-r", str(cfg.get("fps", 30)),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p", out], check=True)
    n = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", out],
                       capture_output=True, text=True).stdout.strip()
    print(key, "picture", out, "frames", n, "expected", round(total * cfg.get("fps", 30)))


if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1])); what = sys.argv[2] if len(sys.argv) > 2 else "audio"
    for key in cfg["cuts"]:
        {"audio": audio, "picture": picture}[what](cfg, key)
