"""Map a music track's bar grid and energy so picture can be cut to it.

    python3 music_grid.py track.mp3 [--bpm 120] [--beats-per-bar 4] [--offset 2.3975]

Without --bpm the tempo is estimated from onset autocorrelation; without --offset the downbeat phase is the one whose bar
starts carry the most onset energy. Prints one row per bar: start time, energy bar, RMS dB and the downbeat "hit" strength
(onset level vs the 200 ms before). Use it to:
  * put chapter starts on bar lines (every title lands on a downbeat);
  * find phrase starts (strong hits every 4 or 8 bars) for splices and cut-downs;
  * land the payoff (a counter, a logo) on the biggest hit.
Writes grid.json next to the track: {bpm, offset, bar, bars:[{t, db, hit}]}."""
import argparse, json, os, subprocess
import numpy as np

SR = 22050


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def onset_env(x, hop=256):
    n = len(x) // hop; fr = x[: n * hop].reshape(n, hop)
    spec = np.abs(np.fft.rfft(fr * np.hanning(hop), axis=1))
    flux = np.maximum(0, np.diff(np.log1p(spec), axis=0)).sum(1)
    return np.r_[0, flux], hop / SR


def estimate_bpm(o, dt, lo=70, hi=180):
    o = o - o.mean(); ac = np.correlate(o, o, "full")[len(o) - 1:]
    lags = np.arange(len(ac)) * dt; m = (lags >= 60 / hi) & (lags <= 60 / lo)
    return 60 / lags[m][np.argmax(ac[m])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track"); ap.add_argument("--bpm", type=float); ap.add_argument("--beats-per-bar", type=int, default=4)
    ap.add_argument("--offset", type=float)
    a = ap.parse_args()
    x = load(a.track); o, dt = onset_env(x)
    bpm = a.bpm or estimate_bpm(o, dt); beat = 60 / bpm; bar = beat * a.beats_per_bar
    if a.offset is None:
        best, off = -1, 0.0
        for ph in np.arange(0, bar, dt):
            idx = (np.arange(ph, len(x) / SR, bar) / dt).astype(int); idx = idx[idx < len(o)]
            s = o[idx].sum()
            if s > best:
                best, off = s, ph
    else:
        off = a.offset % bar
    rows, top = [], None
    for t in np.arange(off, len(x) / SR - 0.01, bar):
        i0, i1 = int(t * SR), int(min(len(x), (t + bar) * SR))
        d = 20 * np.log10(np.sqrt(np.mean(x[i0:i1] ** 2)) + 1e-9)
        h = 20 * np.log10(np.sqrt(np.mean(x[i0:i0 + int(0.08 * SR)] ** 2)) + 1e-9) - 20 * np.log10(np.sqrt(np.mean(x[max(0, i0 - int(0.2 * SR)):i0] ** 2)) + 1e-9)
        rows.append({"t": round(float(t), 4), "db": round(float(d), 1), "hit": round(float(h), 1)})
    top = max(r["db"] for r in rows)
    print(f"bpm {bpm:.2f}  bar {bar:.4f}s  first downbeat {off:.4f}s")
    for r in rows:
        print(f"{r['t']:8.2f}s {'#' * max(0, int(r['db'] - (top - 24))):24s} {r['db']:6.1f} dB  hit {r['hit']:+5.1f}{'  <' if r['hit'] > 4 else ''}")
    out = os.path.splitext(a.track)[0] + ".grid.json"
    json.dump({"bpm": bpm, "offset": off, "bar": bar, "bars": rows}, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
