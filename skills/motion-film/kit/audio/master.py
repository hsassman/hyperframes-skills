"""Master a film mix: fade with the picture, a transparent peak limiter set from the measured loudness, then two-pass
ffmpeg-normalize to -14 LUFS integrated / -1 dBTP (linear mode), and a final BS.1770 measurement.

    python3 master.py mix_pre.wav mix_master.wav --fade 1.6 [--target -14 --tp -1]
Needs ffmpeg and ffmpeg-normalize (pip install ffmpeg-normalize)."""
import argparse, json, os, re, subprocess, tempfile


def ebu(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = r[r.rindex("Summary:"):]
    return (float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1)), float(re.search(r"LRA:\s+(-?[\d.]+) LU", tail).group(1)),
            float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1)))


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout)


def master(src, dst, fade=1.6, target=-14.0, tp=-1.0):
    tmp = tempfile.mkdtemp()
    faded, lim = os.path.join(tmp, "faded.wav"), os.path.join(tmp, "limited.wav")
    total = duration(src)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"afade=t=out:st={max(0, total - fade)}:d={fade}", "-c:a", "pcm_f32le", faded], check=True)
    I, lra, peak = ebu(faded)
    ceiling = I + (tp - target) - 0.4   # limit only the peaks that would land above tp - 0.4 dB after the loudness gain
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", faded, "-af", f"alimiter=limit={min(1.0, 10 ** (ceiling / 20)):.4f}:attack=3:release=60:level=0:asc=1",
                    "-c:a", "pcm_f32le", lim], check=True)
    subprocess.run(["ffmpeg-normalize", lim, "-o", dst, "-f", "-t", str(target), "-tp", str(tp), "-lrt", "11", "--keep-lra-above-loudness-range-target",
                    "-c:a", "pcm_s24le", "-ar", "48000"], check=True, capture_output=True)
    I2, lra2, tp2 = ebu(dst)
    return {"pre": {"I": I, "LRA": lra, "peak": peak}, "limiter_ceiling_dbfs": round(ceiling, 2), "master": {"I": I2, "LRA": lra2, "true_peak": tp2}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--fade", type=float, default=1.6); ap.add_argument("--target", type=float, default=-14.0); ap.add_argument("--tp", type=float, default=-1.0)
    a = ap.parse_args()
    print(json.dumps(master(a.src, a.dst, a.fade, a.target, a.tp)))
