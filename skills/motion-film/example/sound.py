"""Sound pass for the demo film. In a real film: source licensed music + real recordings (see references/sound.md),
write every source into sources.json as you download, then place cues on the picture events below.

    python3 sound.py --demo     # synthesises placeholder music/effects so the pipeline runs with no downloads
    python3 sound.py            # uses music/track.wav + sfx/ (your licensed files)

Outputs audio/out/{music_stem,sfx_stem,mix_pre}.wav, cues.json, mix_master.wav (-14 LUFS / -1 dBTP)."""
import json, os, sys
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kit", "audio"))
from mixkit import Mix, SR  # noqa: E402
from master import master  # noqa: E402

TOTAL = 20.0
OUT = os.path.join(HERE, "audio", "out")
MUSIC, SFX = os.path.join(HERE, "music", "track.wav"), os.path.join(HERE, "sfx")


def synth_demo():
    """120 BPM placeholder: soft pad + kick on every downbeat (bars every 2 s), plus a few synthetic effects."""
    os.makedirs(os.path.dirname(MUSIC), exist_ok=True); os.makedirs(SFX, exist_ok=True)
    rng = np.random.default_rng(1); n = int(48 * SR); t = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * f * t) for f in (110, 164.8, 220, 277.2)) * 0.05 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 8))
    kick = np.zeros(n)
    for b in np.arange(0, 48, 0.5):
        i = int(b * SR); k = np.arange(int(0.25 * SR)) / SR
        kick[i:i + len(k)] += np.sin(2 * np.pi * (50 + 80 * np.exp(-k * 30)) * k) * np.exp(-k * 14) * (0.5 if b % 2 == 0 else 0.18)
    sf.write(MUSIC, np.stack([pad + kick] * 2, 1).astype(np.float32), SR)
    def noise_sweep(d, f0, f1):
        x = rng.normal(0, 1, int(d * SR)); e = np.sin(np.linspace(0, np.pi, len(x))) ** 2
        from numpy.fft import rfft, irfft
        X = rfft(x); fr = np.linspace(0, SR / 2, len(X)); X *= np.exp(-((fr - (f0 + f1) / 2) / ((f1 - f0) / 2 + 1)) ** 2); return irfft(X, len(x)) * e
    sf.write(f"{SFX}/whoosh.wav", np.stack([noise_sweep(1.6, 300, 3000)] * 2, 1).astype(np.float32) * 4, SR)
    k = np.arange(int(0.04 * SR)) / SR
    sf.write(f"{SFX}/click.wav", np.stack([np.sin(2 * np.pi * 2400 * k) * np.exp(-k * 120)] * 2, 1).astype(np.float32), SR)
    k = np.arange(int(0.6 * SR)) / SR
    sf.write(f"{SFX}/thump.wav", np.stack([np.sin(2 * np.pi * (60 + 60 * np.exp(-k * 20)) * k) * np.exp(-k * 7)] * 2, 1).astype(np.float32), SR)
    sf.write(f"{SFX}/scribble.wav", np.stack([noise_sweep(1.2, 2000, 6000) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 9 * np.arange(int(1.2 * SR)) / SR)))] * 2, 1).astype(np.float32), SR)


if "--demo" in sys.argv:
    synth_demo()

ev = json.load(open(os.path.join(HERE, "events.json")))
mx = Mix(MUSIC, TOTAL, libs=[SFX])
# 1) cues straight from picture events (draw-ons, stickers, titles, wipes, panels, textures, bursts, counters)
for e in ev:
    k = e["kind"]
    if k == "draw_start":
        mx.place("scribble.wav", e["t"], "pencil", dur=1.2, fade_out=0.3, note=f"illustration {e['note']} draws")
    elif k in ("sticker", "note"):
        mx.place("click.wav", e["t"], "paper", note=e["note"])
    elif k == "title":
        mx.place("click.wav", e["t"], "click", db=-3, note=f"title {e['note']}")
    elif k in ("wipe", "rise", "burst", "whip"):
        mx.place("whoosh.wav", 0, "whoosh", peak_at=e["t"], note=k)
    elif k == "panel_down":
        mx.place("thump.wav", e["t"], "impact", note="panel lands")
    elif k == "panel_up":
        mx.place("whoosh.wav", e["t"], "whoosh", dur=0.7, fade_out=0.3, note="panel lifts")
    elif k in ("texture_in", "texture_out"):
        mx.place("whoosh.wav", 0, "whoosh", peak_at=e["t"] + 0.3, db=-4, note=f"{k} {e['note']}")
    elif k == "count":
        a, b = (int(v) for v in e["note"].split("->")); n = min(24, b - a)
        mx.ticks("click.wav", [e["t"] + 1.4 * (1 - (1 - i / n) ** 0.5) for i in range(n)], note="counter")
# 2) music breathes into the big downbeats
mx.dip_before([6.0, 12.0, 16.0])
pre = mx.render(OUT)
print(mx.report())
print(json.dumps(master(pre, os.path.join(OUT, "mix_master.wav"), fade=1.0)))
