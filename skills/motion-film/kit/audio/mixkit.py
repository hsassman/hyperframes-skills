"""mixkit — place real recorded sound effects on exact picture events, levelled against the music playing at that moment.

    from mixkit import Mix
    mx = Mix("music_edit.wav", total=71.6, libs=["sfx/"])          # libs: folders holding your licensed recordings
    mx.place("whoosh_soft.mp3", 0, "whoosh", peak_at=10.3, dur=2.0, fade_out=0.5, note="band wipe")
    mx.place("paper_slide.mp3", 2.45, "paper", db=-3, note="title lands")
    mx.ticks("clock.mp3", [47.5, 47.6, ...], note="counter")
    mx.dip_before([10.4, 30.4, 60.4])                                 # short music breaths before the big hits
    mx.render("out/")                                                 # music_stem.wav, sfx_stem.wav, mix_pre.wav, cues.json

Levels: every role has a target (dB of the effect's active RMS against the music's RMS within +-0.75 s of the cue), floored
at the film's average music level - 10 dB so effects in a quiet intro stay small. Each cue also has a sample-peak ceiling so
transient-heavy sounds can't spike the master. Start from ROLE/CAP below and tune per film by measuring (see report()).

Segments: pick="onset" (from the first transient), "loudest" (busiest stretch of dur), or src=seconds. If a fixed src lands
in a pause, the cue moves to the next unused busy stretch of the same recording (so repeats never play the identical take).
"""
import json, os, subprocess
import numpy as np
import soundfile as sf

SR = 48000
ROLE = {"whoosh": -7, "swish": -10, "marker": -13, "paper": -10, "pop": -8, "click": -14, "chime": -9, "box": -5, "tape": -7,
        "amb": -15, "riser": -9, "truck": -13, "pencil": -13, "door": -6, "rattle": -7, "ice": -10, "flour": -9, "tick": -15,
        "wind": -13, "handling": -15, "impact": -6, "ui": -12}
CAP = {"door": -4.0, "whoosh": -5.0, "tape": -5.0, "box": -6.0, "flour": -6.0, "riser": -6.0, "rattle": -7.0, "impact": -4.0,
       "tick": -16.0, "pop": -9.0, "amb": -14.0, "wind": -10.0, "ice": -10.0}


def decode(path, hp=None, lp=None, sr=SR):
    af = ",".join(x for x in [f"highpass=f={hp}" if hp else "", f"lowpass=f={lp}" if lp else ""] if x)
    cmd = ["ffmpeg", "-v", "error", "-i", path] + (["-af", af] if af else []) + ["-f", "f32le", "-ac", "2", "-ar", str(sr), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def env(x, win=0.01):
    m = np.abs(x).mean(1); w = max(1, int(win * SR))
    return np.convolve(m, np.ones(w) / w, "same")


class Mix:
    def __init__(self, music, total, libs=(), roles=None, caps=None, floor_db=-10.0):
        self.total, self.N, self.libs = total, int(total * SR), list(libs)
        m = decode(music)[: self.N]
        self.music = m if len(m) >= self.N else np.vstack([m, np.zeros((self.N - len(m), 2), np.float32)])
        self.MRMS = rms_db(self.music)
        self.bus = np.zeros((self.N + 2 * SR, 2), np.float32)
        self.cues, self.cache, self.used = [], {}, {}
        self.roles = {**ROLE, **(roles or {})}; self.caps = {**CAP, **(caps or {})}
        self.floor = floor_db
        self.gain = np.ones(self.N, np.float32)

    # ---------------------------------------------------------------- helpers
    def path(self, name):
        if os.path.isabs(name) or os.path.exists(name):
            return name
        for d in self.libs:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
        raise FileNotFoundError(name)

    def load(self, name, hp=None, lp=None):
        k = (name, hp, lp)
        if k not in self.cache:
            self.cache[k] = decode(self.path(name), hp, lp)
        return self.cache[k].copy()

    def ref_db(self, t0, t1):
        a, b = int(max(0.0, t0 - 0.75) * SR), int(min(self.total, t1 + 0.75) * SR)
        return max(rms_db(self.music[a:b]) if b > a else self.MRMS, self.MRMS + self.floor)

    def busy_windows(self, name, hp, lp, n, maxk=8):
        x = self.load(name, hp, lp); m = (x ** 2).mean(1); c = np.cumsum(np.r_[0, m])
        if len(x) <= n:
            return [0]
        w = c[n:] - c[:-n]; hop = max(1, int(0.02 * SR)); idx = np.arange(0, len(w), hop); sc = w[idx]; out = []
        for i in np.argsort(-sc):
            st = int(idx[i])
            if all(abs(st - o) >= n for o in out):
                out.append(st)
            if len(out) >= maxk:
                break
        return out

    def _add(self, seg, t):
        i0 = int(round(t * SR))
        if i0 < 0:
            seg = seg[-i0:]; i0 = 0
        i1 = min(len(self.bus), i0 + len(seg))
        if i1 > i0:
            self.bus[i0:i1] += seg[: i1 - i0]

    # ---------------------------------------------------------------- cues
    def place(self, name, t, role, dur=None, pick="onset", src=None, peak_at=None, fade_in=0.008, fade_out=0.08,
              hp=None, lp=None, pan=0.0, db=0.0, cap=None, note=""):
        """t = film time of the segment start, or with peak_at = film time where the segment's loudest 20 ms lands."""
        x = self.load(name, hp, lp)
        if src is not None:
            s0 = int(src * SR)
        elif pick == "onset":
            e = env(x); s0 = max(0, int(np.argmax(e > e.max() * 10 ** (-30 / 20))) - int(0.012 * SR))
        else:
            n = int((dur or 2.0) * SR); s0 = self.busy_windows(name, hp, lp, n, 1)[0] if len(x) > n else 0
        seg = x[s0: s0 + int((dur or (len(x) - s0) / SR) * SR)].copy()
        if len(seg) < 32:
            return
        if src is not None and (np.mean(env(seg, 0.02) > 10 ** (-42 / 20)) < 0.45 or rms_db(seg) < -40):
            wins = self.busy_windows(name, hp, lp, len(seg)); k = self.used.get(name, 0) % len(wins); self.used[name] = k + 1
            seg = x[wins[k]: wins[k] + len(seg)].copy()
        act = seg[np.abs(seg).mean(1) > 10 ** (-50 / 20)]
        cur = rms_db(act if len(act) > 100 else seg)
        if peak_at is not None:
            t = peak_at - np.argmax(env(seg, 0.02)) / SR
        g = 10 ** ((self.ref_db(t, t + len(seg) / SR) + self.roles[role] + db - cur) / 20)
        c = self.caps.get(role, -9.0) if cap is None else cap
        g = min(g, 10 ** (c / 20) / (np.abs(seg).max() + 1e-9))
        seg *= g
        fi, fo = min(int(fade_in * SR), len(seg) // 2), min(int(fade_out * SR), len(seg) // 2)
        if fi:
            seg[:fi] *= np.linspace(0, 1, fi)[:, None]
        if fo:
            seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
        if pan:
            seg[:, 0] *= min(1.0, 1 - pan); seg[:, 1] *= min(1.0, 1 + pan)
        self._add(seg, t)
        self.cues.append({"t": round(float(t), 3), "end": round(float(t + len(seg) / SR), 3), "file": name, "role": role, "note": note})

    def ticks(self, name, times, role="tick", db=0.0, pan=0.0, note=""):
        """One short transient lifted from a real recording, repeated on given times with slight level variation
        (counters, clocks, typing)."""
        x = self.load(name); e = env(x, 0.002); pk = int(np.argmax(e[: int(1.5 * SR)]))
        tk = x[max(0, pk - int(0.004 * SR)): pk + int(0.066 * SR)].copy()
        tk[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))[:, None]
        rng = np.random.default_rng(7)
        for t in times:
            seg = tk * 10 ** (rng.uniform(-2.5, 0.5) / 20)
            g = 10 ** ((self.ref_db(t, t + 0.07) + self.roles[role] + db - rms_db(seg[: int(0.03 * SR)])) / 20)
            g = min(g, 10 ** (self.caps.get(role, -9.0) / 20) / (np.abs(seg).max() + 1e-9))
            seg = seg * g
            if pan:
                seg[:, 0] *= min(1.0, 1 - pan); seg[:, 1] *= min(1.0, 1 + pan)
            self._add(seg, t)
        self.cues.append({"t": round(times[0], 3), "end": round(times[-1] + 0.07, 3), "file": name, "role": role, "note": f"{note} ({len(times)} ticks)"})

    def dip_before(self, hits, depth_db=-4.0, lead=0.5):
        """Music takes a short breath into each hit and snaps back on the downbeat."""
        lo = 10 ** (depth_db / 20)
        for hit in hits:
            a, b, c = int((hit - lead) * SR), int((hit - 0.06) * SR), int((hit - 0.01) * SR)
            self.gain[a:b] = np.minimum(self.gain[a:b], np.linspace(1, lo, b - a)); self.gain[b:c] = lo
            d = c + int(0.03 * SR); self.gain[c:d] = np.linspace(lo, 1, d - c)

    # ---------------------------------------------------------------- output
    def render(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        mus = self.music * self.gain[:, None]; stem = self.bus[: self.N].copy()
        sf.write(os.path.join(out_dir, "music_stem.wav"), mus, SR, subtype="FLOAT")
        sf.write(os.path.join(out_dir, "sfx_stem.wav"), stem, SR, subtype="FLOAT")
        sf.write(os.path.join(out_dir, "mix_pre.wav"), mus + stem, SR, subtype="FLOAT")
        with open(os.path.join(out_dir, "cues.json"), "w") as fh:
            json.dump({"music_rms_db": round(float(self.MRMS), 2), "cues": sorted(self.cues, key=lambda c: c["t"])}, fh, indent=1)
        return os.path.join(out_dir, "mix_pre.wav")

    def report(self, quiet=-15.0, hot=0.0):
        """Per cue: loudest 50 ms of the effect vs the music around it. Flags inaudible (< quiet) and dominant (> hot) cues."""
        mus = self.music * self.gain[:, None]; s = self.bus[: self.N]; w = int(0.05 * SR); rows = []
        for c in sorted(self.cues, key=lambda c: c["t"]):
            a = int(c["t"] * SR); b = min(len(s), int(min(c["end"], c["t"] + 0.6) * SR))
            if b - a < w:
                continue
            seg = s[a:b]; p50 = max(rms_db(seg[i:i + w]) for i in range(0, len(seg) - w, w // 2))
            r = p50 - rms_db(mus[a:b]); flag = "QUIET" if r < quiet else "HOT" if r > hot else ""
            rows.append(f"{c['t']:7.2f}  {c['role']:7s} {c['note'][:34]:34s} {r:+6.1f} dB {flag}")
        return "\n".join(rows)
