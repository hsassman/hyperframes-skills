"""filmkit.compose — build a HyperFrames composition (index.html) from Python.

Why a generator: a film is hundreds of timed tweens. Writing them through small helpers keeps every element on the same
timeline grid, makes re-timing a whole chapter a one-number change, and lets the sound mix read the same event times.

Model
-----
* One GSAP timeline (`tl`, registered as window.__timelines['main']); every tween has an absolute start time in seconds.
* Timed *clips* (`class="clip"` + data-start/data-duration) are top-level children of #root: grounds, chapter containers,
  videos, canvases, overlays. Videos must stay top level (HyperFrames rule) and are always muted.
* Each chapter collects untimed markup in named *layers* (`film.L(key)`); `film.container(...)` wraps a layer in a clip.
  Typical: "b2" = back layer (under videos), "f2" = front layer (over videos).
* Edge boil: SVG feTurbulence filters whose seed steps at 10 fps; apply with filter:url(#boil) (all drawn elements do).
* Three.js layers render from timeline time via the hf-seek event (see kit/node/src/film3d.js); register them with
  film.init3d("FILM3D.particles('cv',{...})").

All coordinates are 1920x1080 px. Times are seconds. Colours come from the Theme.
"""
import json, math, os
from dataclasses import dataclass, field


@dataclass
class Theme:
    bg: str = "#0F2A33"        # deepest brand colour: root background, map fog, fade-out
    ink: str = "#1F2A30"       # outlines and reading text on light grounds
    paper: str = "#FAF6F0"     # light neutral: frames, stickers, text on dark grounds
    accent: str = "#E8743B"    # display accent: arrows, chips, counters (never small body text)
    accent2: str = "#2BA3B8"   # second display colour
    display: str = "Poppins"   # headline font family
    body: str = "Inter"        # body/label font family
    hand: str = "Caveat"       # handwritten accent font family (short notes only)
    font_faces: list = field(default_factory=list)   # [(family, weight, "assets/fonts/x.woff2"), ...]


def f(v):
    return f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


# ------------------------------------------------------------------ geometry
def smooth(pts, closed=False, tension=0.5):
    n = len(pts)
    get = (lambda i: pts[i % n]) if closed else (lambda i: pts[max(0, min(n - 1, i))])
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = get(i - 1), get(i), get(i + 1), get(i + 2)
        t = tension / 3
        c1 = (p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t)
        c2 = (p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + (" Z" if closed else "")


def loop_path(cx, cy, rx, ry, turns=1.12, wob=0.045, s=1, rot=-0.35):
    pts = []
    for i in range(91):
        t = i / 90 * turns * 2 * math.pi
        w = 1 + wob * math.sin(t * 2.3 + s) + wob * 0.6 * math.sin(t * 5.1 + s * 2)
        d = 1 + 0.06 * (i / 90)
        pts.append((cx + rx * w * d * math.cos(t + rot), cy + ry * w * d * math.sin(t + rot)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def arrow_path(x0, y0, x1, y1, bend=0.22, head=30):
    mx, my, dx, dy = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    a = math.atan2(y1 - cy, x1 - cx)
    a1 = (x1 - head * math.cos(a - .45), y1 - head * math.sin(a - .45)); a2 = (x1 - head * math.cos(a + .45), y1 - head * math.sin(a + .45))
    return f"M{x0:.1f},{y0:.1f} Q{cx:.1f},{cy:.1f} {x1:.1f},{y1:.1f}", f"M{a1[0]:.1f},{a1[1]:.1f} L{x1:.1f},{y1:.1f} L{a2[0]:.1f},{a2[1]:.1f}"


def brace_path(x0, x1, y, h):
    w = x1 - x0; xm = (x0 + x1) / 2
    pts = [(x0, y), (x0 + 14, y - h * 0.72), (x0 + w * 0.22, y - h * 0.82), (xm - 18, y - h * 0.86), (xm, y - h * 1.55),
           (xm + 18, y - h * 0.86), (x1 - w * 0.22, y - h * 0.82), (x1 - 14, y - h * 0.72), (x1, y)]
    return smooth(pts, tension=0.6)


REV = {"up": "inset(100% 0% 0% 0% round 24px)", "left": "inset(0% 100% 0% 0% round 24px)", "right": "inset(0% 0% 0% 100% round 24px)",
       "iris": "inset(50% 50% 50% 50% round 24px)", "down": "inset(0% 0% 100% 0% round 24px)"}
SHOWN = "inset(0% 0% 0% 0% round 24px)"


class Film:
    def __init__(self, total, theme=None, scripts=None, width=1920, height=1080, seed=11):
        self.total, self.th, self.W, self.Hpx = total, theme or Theme(), width, height
        self.H, self.JS, self.INIT3D, self.LAYERS, self.events = [], [], [], {}, []
        self.scripts = scripts or ["assets/gsap.min.js", "assets/MorphSVGPlugin.min.js"]
        self._seed, self._n = [seed], {"pline": 0}
        self.T("gsap.registerPlugin(MorphSVGPlugin);")
        self.T("const tl = gsap.timeline({ paused: true });")

    # -------------------------------------------------------------- plumbing
    def T(self, s):
        self.JS.append(s)

    def L(self, key):
        return self.LAYERS.setdefault(key, [])

    def event(self, t, kind, note=""):
        """Record a picture event (a reveal, a slam, a draw-on). The sound pass reads these to place cues on the frame."""
        self.events.append({"t": round(t, 3), "kind": kind, "note": note})

    def rnd(self):
        self._seed[0] = (self._seed[0] * 1103515245 + 12345) % 2147483648
        return self._seed[0] / 2147483648

    def init3d(self, js):
        self.INIT3D.append(js)

    # -------------------------------------------------------------- clips
    def ground(self, gid, start, dur, img, word=None, word_col="rgba(255,255,255,.2)", word_y=600, z=1, bg=None, extra=""):
        """Chapter ground: an oversized pre-rendered plate (filmkit.grounds) drifting slowly + optional giant outline word."""
        wd = f'<div class="giant" id="{gid}_w" style="top:{word_y}px;-webkit-text-stroke:4px {word_col}">{word}</div>' if word else ""
        src = img if "." in img else f"{img}.jpg"
        self.H.append(f'<div id="{gid}" class="clip" data-start="{f(start)}" data-duration="{f(dur)}" style="z-index:{z};overflow:hidden;background:{bg or self.th.bg}">'
                      f'<img id="{gid}_i" src="assets/{src}" alt="" style="position:absolute;left:-96px;top:-54px;width:2112px;height:1188px">{wd}{extra}</div>')
        dx, dy = (self.rnd() - .5) * 90, (self.rnd() - .5) * 50
        self.T(f"tl.fromTo('#{gid}_i',{{x:0,y:0,scale:1}},{{x:{dx:.0f},y:{dy:.0f},scale:1.045,duration:{f(dur)},ease:'sine.inOut'}},{f(start)});")
        if word:
            self.T(f"tl.fromTo('#{gid}_w',{{x:90}},{{x:-150,duration:{f(dur)},ease:'none'}},{f(start)});")

    def container(self, cid, key, start, dur, z):
        self.H.append(f'<div id="{cid}" class="clip" data-start="{f(start)}" data-duration="{f(dur)}" style="z-index:{z};pointer-events:none">{"".join(self.LAYERS.get(key, []))}</div>')

    def canvas3d(self, cid, start, dur, z):
        self.H.append(f'<div id="{cid}_c" class="clip" data-start="{f(start)}" data-duration="{f(dur)}" style="z-index:{z};pointer-events:none">'
                      f'<canvas id="{cid}" width="1920" height="1080" style="position:absolute;inset:0;width:1920px;height:1080px"></canvas></div>')

    def raw_clip(self, cid, start, dur, z, inner, style=""):
        self.H.append(f'<div id="{cid}" class="clip" data-start="{f(start)}" data-duration="{f(dur)}" style="z-index:{z};pointer-events:none;{style}">{inner}</div>')

    # -------------------------------------------------------------- media windows
    def reveal(self, targets, at, kind, dur=0.9):
        if kind is None:
            return
        if kind == "instant":
            self.T(f"tl.set({targets},{{clipPath:'{SHOWN}'}},{f(at)});"); return
        self.T(f"tl.fromTo({targets},{{clipPath:'{REV[kind]}'}},{{clipPath:'{SHOWN}',duration:{dur},ease:'expo.out'}},{f(at)});")
        self.event(at, "reveal", kind)

    def win_img(self, key, wid, x, y, w, h, src, at, kb=(1.08, 1.0), kbdur=8, pos="50% 50%", rv="up", tag=None, tagpos="bl"):
        """Framed photo window with a reveal and a slow Ken Burns push."""
        self.L(key).append(f'<div class="win" id="{wid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><div class="wi" id="{wid}_k"><img src="assets/{src}" alt="" style="object-position:{pos}"></div></div>')
        self.reveal(f"'#{wid}'", at, rv)
        self.T(f"tl.fromTo('#{wid}_k',{{scale:{kb[0]}}},{{scale:{kb[1]},duration:{kbdur},ease:'sine.out'}},{f(at)});")
        if tag:
            self.tagbox(key, wid + "_t", x, y, w, h, tag, at + 0.5, tagpos)

    def win_vid(self, key, front, wid, x, y, w, h, src, start, dur, mstart, at, z=20, pos="50% 50%", rv="up", tag=None, tagpos="bl"):
        """Framed video window. The <video> is a top-level muted clip; its white frame lives in the chapter's back layer."""
        self.L(key).append(f'<div class="vframe" id="{wid}_f" style="left:{x - 7}px;top:{y - 7}px;width:{w + 14}px;height:{h + 14}px"></div>')
        self.H.append(f'<video id="{wid}" class="clip vwin" src="assets/{src}" muted playsinline data-start="{f(start)}" data-duration="{f(dur)}" data-media-start="{f(mstart)}" '
                      f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;z-index:{z};object-position:{pos}"></video>')
        self.reveal(f"['#{wid}_f','#{wid}']", at, rv)
        if tag:
            self.tagbox(front, wid + "_t", x, y, w, h, tag, at + 0.5, tagpos)

    def full_video(self, vid, src, start, dur, mstart=0, z=5):
        self.H.append(f'<video id="{vid}" class="clip" src="assets/{src}" muted playsinline data-start="{f(start)}" data-duration="{f(dur)}" data-media-start="{f(mstart)}" '
                      f'style="z-index:{z};width:1920px;height:1080px;object-fit:cover"></video>')

    def tagbox(self, key, tid, x, y, w, h, text, at, pos="bl"):
        tx, ty = (x + 20, y + h - 58) if pos == "bl" else (x + 20, y + 20) if pos == "tl" else (x + w - 20, y + h - 58)
        anchor = "transform:translateX(-100%)" if pos == "br" else ""
        self.L(key).append(f'<div class="tagwrap" style="left:{tx}px;top:{ty}px;{anchor}"><div class="tagc" id="{tid}">{text}</div></div>')
        self.T(f"tl.fromTo('#{tid}',{{opacity:0,x:-16}},{{opacity:1,x:0,duration:0.5,ease:'power3.out'}},{f(at)});")

    def polaroid(self, key, pid, x, y, w, h, src, at, rot, caption, pos="50% 50%", kb=(1.1, 1.0), kbdur=7):
        self.L(key).append(f'<div class="pol" id="{pid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><div class="pin"><img id="{pid}_i" src="assets/{src}" alt="" style="object-position:{pos}"></div>'
                           f'<div class="pcap">{caption}</div><div class="tape" style="left:{w / 2 - 75:.0f}px;top:-20px"></div></div>')
        self.T(f"tl.fromTo('#{pid}',{{opacity:0,y:70,rotation:{rot - 7}}},{{opacity:1,y:0,rotation:{rot},duration:0.75,ease:'back.out(1.5)'}},{f(at)});")
        self.T(f"tl.fromTo('#{pid}_i',{{scale:{kb[0]}}},{{scale:{kb[1]},duration:{kbdur},ease:'sine.out'}},{f(at)});")
        self.event(at, "drop", "polaroid")

    # -------------------------------------------------------------- type
    def title(self, key, tid, x, y, num, label, word, sub, at, col=None, sub_col=None, chip_bg=None, label_col=None, style="rise", size=150, subw=700):
        """Chapter title: chip (number + label), headline word (rise | letters | blur) and a sub line that rises word by word."""
        th = self.th; col = col or th.paper; sub_col = sub_col or col; label_col = label_col or col; chip_bg = chip_bg or th.accent
        chip = (f'<div class="chip" id="{tid}_c" style="left:{x}px;top:{y}px"><span class="cn" style="background:{chip_bg}">{num}</span>'
                f'<span class="cl" style="color:{label_col}">{label}</span></div>') if num else ""
        if style == "rise":
            head = f'<div class="mask" style="left:{x - 6}px;top:{y + 42}px"><div class="step" id="{tid}_w" style="color:{col};font-size:{size}px">{word}</div></div>'
        elif style == "letters":
            head = f'<div class="step" id="{tid}_w" style="left:{x}px;top:{y + 48}px;color:{col};font-size:{size}px;position:absolute">' + "".join(f'<span class="lt">{c}</span>' for c in word) + "</div>"
        else:
            head = f'<div class="step" id="{tid}_w" style="left:{x}px;top:{y + 48}px;color:{col};font-size:{size}px;position:absolute">' + " ".join(f'<span class="wb">{w}</span>' for w in word.split(" ")) + "</div>"
        subh = (f'<div class="sub" id="{tid}_s" style="left:{x + 4}px;top:{y + 48 + size * 1.12:.0f}px;color:{sub_col};width:{subw}px">'
                + " ".join(f'<span class="sw"><span class="swi">{w}</span></span>' for w in sub.split(" ")) + "</div>") if sub else ""
        self.L(key).append(chip + head + subh)
        if num:
            self.T(f"tl.fromTo('#{tid}_c',{{opacity:0,x:-24}},{{opacity:1,x:0,duration:0.5,ease:'power3.out'}},{f(at)});")
        if style == "rise":
            self.T(f"tl.fromTo('#{tid}_w',{{yPercent:118}},{{yPercent:0,duration:0.8,ease:'power4.out'}},{f(at + 0.05)});")
        elif style == "letters":
            self.T(f"tl.fromTo('#{tid}_w .lt',{{opacity:0.15,filter:'blur(6px)'}},{{opacity:1,filter:'blur(0px)',duration:0.18,stagger:0.045,ease:'power2.out'}},{f(at + 0.05)});")
        else:
            self.T(f"tl.fromTo('#{tid}_w .wb',{{opacity:0,filter:'blur(10px)'}},{{opacity:1,filter:'blur(0px)',duration:0.16,stagger:0.07,ease:'power2.out'}},{f(at + 0.05)});")
        if sub:
            self.T(f"tl.fromTo('#{tid}_s .swi',{{yPercent:120}},{{yPercent:0,duration:0.6,ease:'power3.out',stagger:0.035}},{f(at + 0.35)});")
        self.event(at + 0.05, "title", word)

    def counter(self, key, sid, x, y, to, label, at, dur=1.4, frm=0, suffix="", col=None, label_col=None, decimals=0, sep=","):
        """Big stat that counts up (power2.out) — land it on a musical downbeat."""
        col = col or self.th.paper; label_col = label_col or col
        self.L(key).append(f'<div class="stat" id="{sid}" style="left:{x}px;top:{y}px;opacity:0"><div class="v" style="color:{col}"><span id="{sid}_n">{frm}</span>{suffix}</div>'
                           f'<div class="l" style="color:{label_col}">{label}</div></div>')
        self.T(f"tl.fromTo('#{sid}',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5,ease:'power3.out'}},{f(at)});")
        self.T(f"(function(){{const o={{v:{frm}}},el=document.getElementById('{sid}_n');tl.fromTo(o,{{v:{frm}}},{{v:{to},duration:{dur},ease:'power2.out',"
               f"onUpdate:function(){{el.textContent=o.v.toFixed({decimals}).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,'{sep}');}}}},{f(at)});}})();")
        self.event(at, "count", f"{frm}->{to}"); self.event(at + dur * 0.7, "count_land", str(to))

    # -------------------------------------------------------------- drawn annotation (edge-boiled SVG)
    def svg_wrap(self, key, sid, inner, boil="boil"):
        self.L(key).append(f'<svg id="{sid}" class="ov" width="1920" height="1080" viewBox="0 0 1920 1080" style="filter:url(#{boil})">{inner}</svg>')

    def draw(self, pid, at, dur, ease="power2.inOut"):
        self.T(f"tl.fromTo('#{pid}',{{attr:{{'stroke-dashoffset':1}}}},{{attr:{{'stroke-dashoffset':0}},duration:{f(dur)},ease:'{ease}'}},{f(at)});")

    @staticmethod
    def spath(pid, d, col, w, extra=""):
        return (f'<path id="{pid}" d="{d}" pathLength="1" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" '
                f'stroke-linejoin="round" stroke-dasharray="1 1" stroke-dashoffset="1" {extra}/>')

    def arrow(self, key, aid, x0, y0, x1, y1, at, col=None, width=7, bend=0.22, head=30):
        b, hd = arrow_path(x0, y0, x1, y1, bend, head)
        self.svg_wrap(key, aid, self.spath(aid + "_a", b, col or self.th.accent, width) + self.spath(aid + "_h", hd, col or self.th.accent, width))
        self.draw(aid + "_a", at, 0.55); self.draw(aid + "_h", at + 0.5, 0.2)
        self.event(at, "draw", "arrow")

    def loop(self, key, lid, cx, cy, rx, ry, at, col=None, width=7, s=1, dur=0.8):
        """Hand-drawn loop around a detail. Use sparingly — one per film reads as emphasis, one per scene reads as a tic."""
        self.svg_wrap(key, lid, self.spath(lid + "_p", loop_path(cx, cy, rx, ry, s=s), col or self.th.accent, width))
        self.draw(lid + "_p", at, dur); self.event(at, "draw", "loop")

    def brace(self, key, bid, x0, x1, y, h, at, col=None, width=6):
        self.svg_wrap(key, bid, self.spath(bid + "_p", brace_path(x0, x1, y, h), col or self.th.accent, width))
        self.draw(bid + "_p", at, 0.6); self.event(at, "draw", "brace")

    def underline(self, key, uid, x0, x1, y, at, col=None, width=7, dur=0.5):
        d = smooth([(x0, y), ((x0 + x1) / 2, y + 6), (x1, y - 2)], tension=0.5)
        self.svg_wrap(key, uid, self.spath(uid + "_p", d, col or self.th.accent, width))
        self.draw(uid + "_p", at, dur); self.event(at, "draw", "underline")

    def note(self, key, nid, x, y, text, at, col=None, size=60, rot=-3, sticker=False):
        """Handwritten note (hand font) or a taped paper sticker."""
        col = col or self.th.ink
        if sticker:
            self.L(key).append(f'<div class="stk" id="{nid}" style="left:{x}px;top:{y}px"><span style="font-size:{size}px;color:{col}">{text}</span><i class="stkt"></i></div>')
            self.T(f"tl.fromTo('#{nid}',{{opacity:0,scale:0.85,rotation:{rot - 6}}},{{opacity:1,scale:1,rotation:{rot},duration:0.55,ease:'back.out(1.8)'}},{f(at)});")
            self.event(at, "sticker", text)
        else:
            self.L(key).append(f'<div class="hand" id="{nid}" style="left:{x}px;top:{y}px;font-size:{size}px;color:{col}">{text}</div>')
            self.T(f"tl.fromTo('#{nid}',{{opacity:0,y:12,rotation:{rot}}},{{opacity:1,y:0,rotation:{rot},duration:0.5,ease:'power3.out'}},{f(at)});")
            self.event(at, "note", text)

    def process_line(self, key, pts, at, dur, col=None, width=8, dashed=False):
        """A line that threads through a chapter and leaves frame toward the next step. Solid by default (dashed lines read busy)."""
        self._n["pline"] += 1; pid = f"pl{self._n['pline']}"
        d = smooth(pts)
        dash = 'stroke-dasharray="3 19"' if dashed else ""
        inner = (f'<defs><mask id="{pid}_m" maskUnits="userSpaceOnUse" x="-200" y="-200" width="2320" height="1480">'
                 f'<path id="{pid}_mp" d="{d}" pathLength="1" stroke="#fff" stroke-width="{width + 22}" fill="none" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1"/></mask></defs>'
                 f'<path id="{pid}" d="{d}" stroke="{col or self.th.accent}" stroke-width="{width}" fill="none" stroke-linecap="round" {dash} mask="url(#{pid}_m)"/>')
        self.svg_wrap(key, pid + "_s", inner)
        self.draw(pid + "_mp", at, dur); self.event(at, "draw", "process line")

    def illo(self, key, data, iid, x, y, scale, at, speed=1.0, recolor=None, wmul=1.0):
        """Hero illustration from kit/node illos JSON: draws part by part (outline -> fills pop in behind -> details). Returns end time."""
        w, h = data["w"], data["h"]
        groups, order, cursor, pending = {}, [], at, []
        wf = (0.62 + 0.38 / scale) * wmul
        for p in sorted(data["parts"], key=lambda p: p["order"]):
            pid = f"{iid}_{p['id']}"
            col = (recolor or {}).get(p["color"], p["color"])
            g = p.get("group") or "_"
            if g not in groups:
                groups[g] = []; order.append(g)
            if p["kind"] == "fill":
                groups[g].append(f'<path id="{pid}" d="{p["d"]}" fill="{col}" style="opacity:0" transform="translate({p["dx"]} {p["dy"]})"/>')
                pending.append((pid, p.get("opacity", 1)))
            else:
                groups[g].append(self.spath(pid, p["d"], col, f"{p['width'] * wf:.2f}"))
                dd = p["dur"] / speed
                self.draw(pid, cursor, dd, "power1.inOut")
                for fid, op in pending:
                    self.T(f"tl.fromTo('#{fid}',{{opacity:0}},{{opacity:{op},duration:0.3,ease:'power1.out'}},{f(cursor + dd * 0.55)});")
                pending = []
                cursor += dd * 0.62
        for fid, op in pending:
            self.T(f"tl.fromTo('#{fid}',{{opacity:0}},{{opacity:{op},duration:0.3}},{f(cursor)});")
        body = "".join("".join(groups[g]) if g == "_" else f'<g id="{iid}_g_{g}">{"".join(groups[g])}</g>' for g in order)
        self.L(key).append(f'<svg id="{iid}" class="illo" viewBox="-20 -20 {w + 40} {h + 40}" style="left:{x - 20 * scale:.0f}px;top:{y - 20 * scale:.0f}px;'
                           f'width:{(w + 40) * scale:.0f}px;height:{(h + 40) * scale:.0f}px;filter:url(#boil)">{body}</svg>')
        self.event(at, "draw_start", iid); self.event(cursor, "draw_end", iid)
        return cursor

    # -------------------------------------------------------------- transitions (each is caused by something on screen)
    def band_wipe(self, tid, at, color=None, z=150, dur_in=0.45, dur_out=0.5, angle=-8):
        """A wide colour band sweeps across and off — covers the cut at `at + dur_in`."""
        self.raw_clip(tid, at, dur_in + dur_out + 0.1, z, f'<div id="{tid}_b" style="position:absolute;left:0;top:-300px;width:2600px;height:1680px;background:{color or self.th.bg};transform:rotate({angle}deg)"></div>')
        self.T(f"tl.fromTo('#{tid}_b',{{x:-2700}},{{x:-340,duration:{dur_in},ease:'power3.in'}},{f(at)});")
        self.T(f"tl.to('#{tid}_b',{{x:2400,duration:{dur_out},ease:'power3.out'}},{f(at + dur_in + 0.05)});")
        self.event(at + dur_in, "wipe", "band")

    def whip(self, out_ids, in_ids, at, dist=2100, dur_out=0.32, dur_in=0.42):
        """Whip pan: outgoing elements fly left with blur, incoming ones arrive from the right (cut lands at `at + dur_out`)."""
        o = ",".join(f"'#{i}'" for i in out_ids); n = ",".join(f"'#{i}'" for i in in_ids)
        self.T(f"tl.to([{o}],{{x:-{dist},filter:'blur(18px)',duration:{dur_out},ease:'power3.in'}},{f(at)});")
        self.T(f"tl.fromTo([{n}],{{x:{dist},filter:'blur(18px)'}},{{x:0,filter:'blur(0px)',duration:{dur_in},ease:'power3.out'}},{f(at + dur_out)});")
        self.event(at + dur_out, "whip")

    def texture_cover(self, tid, img, at, hold, z=160, settle_opacity=0.92):
        """A full-frame texture (e.g. frost, smoke, paper) grows in from beyond the edges and settles; keep scale >= 1.04 so
        the image edge never shows."""
        self.raw_clip(tid, at, hold, z, f'<img id="{tid}_i" src="assets/{img}" alt="" style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
        self.T(f"tl.fromTo('#{tid}_i',{{opacity:0,scale:1.5}},{{opacity:1,scale:1.04,duration:0.6,ease:'power2.out',transformOrigin:'50% 50%'}},{f(at + 0.03)});")
        self.T(f"tl.to('#{tid}_i',{{opacity:{settle_opacity},scale:1.13,duration:{f(max(0.5, hold - 0.7))},ease:'sine.out'}},{f(at + 0.65)});")
        self.event(at, "texture_in", img)

    def shutter(self, tid, img, at, z=178, up_after=0.18):
        """A panel (roller door, curtain, page) slams down to cover the frame, bounces, then rolls up on the next scene."""
        self.raw_clip(tid, at, 1.4, z, f'<div id="{tid}_i" style="position:absolute;left:0;top:0;width:1920px;height:1120px;background:url(assets/{img}) center/cover">'
                      f'<div style="position:absolute;left:0;top:100%;width:100%;height:110px;background:linear-gradient(rgba(6,14,20,.55),rgba(6,14,20,0))"></div></div>')
        self.T(f"tl.fromTo('#{tid}_i',{{y:-1140}},{{y:-28,duration:0.4,ease:'power2.in'}},{f(at + 0.06)});")
        self.T(f"tl.to('#{tid}_i',{{y:0,duration:0.12,ease:'power1.out'}},{f(at + 0.46)});")
        self.T(f"tl.to('#{tid}_i',{{y:-1190,duration:0.66,ease:'power2.inOut'}},{f(at + 0.58 + up_after)});")
        self.event(at + 0.46, "slam"); self.event(at + 0.58 + up_after, "roll_up")

    def cloud_pass(self, tid, img_a, img_b, at, z=176):
        """Camera rises through two cloud layers (tilt up), white flash at the top, clouds clear upwards."""
        self.raw_clip(tid, at, 2.1, z,
                      f'<img id="{tid}_b" src="assets/{img_b}" alt="" style="position:absolute;left:-240px;top:0;width:2400px;height:1350px">'
                      f'<img id="{tid}_a" src="assets/{img_a}" alt="" style="position:absolute;left:-160px;top:0;width:2240px;height:1260px">'
                      f'<div id="{tid}_w" style="position:absolute;inset:0;background:#fff;opacity:0"></div>')
        self.T(f"tl.fromTo('#{tid}_b',{{y:1400}},{{y:40,duration:0.8,ease:'power2.in'}},{f(at + 0.12)});")
        self.T(f"tl.to('#{tid}_b',{{y:-1600,duration:1.05,ease:'power2.out'}},{f(at + 0.92)});")
        self.T(f"tl.fromTo('#{tid}_a',{{y:1150}},{{y:-80,duration:0.75,ease:'power2.in'}},{f(at + 0.02)});")
        self.T(f"tl.to('#{tid}_a',{{y:-1450,duration:1.0,ease:'power2.out'}},{f(at + 0.77)});")
        self.T(f"tl.fromTo('#{tid}_w',{{opacity:0}},{{opacity:0.85,duration:0.23,ease:'power1.in'}},{f(at + 0.57)});")
        self.T(f"tl.to('#{tid}_w',{{opacity:0,duration:0.25}},{f(at + 0.8)});")
        self.event(at + 0.5, "rise")

    def burst(self, tid, img, at, x=960, y=540, z=97, follow=False):
        """A burst image (powder, splash, confetti) grows from a point to cover the frame, then blows past. With follow=True
        the element is positioned every frame by FILM3D.map's `follow` option (e.g. bursting out of a map pin)."""
        pos = "" if follow else f"left:{x}px;top:{y}px;"
        self.raw_clip(tid, at - 0.12, 1.4, z, f'<div id="{tid}_p" style="position:absolute;{pos}width:0;height:0">'
                      f'<img id="{tid}_i" src="assets/{img}" alt="" style="position:absolute;left:-1150px;top:-650px;width:2300px;height:1300px;opacity:0"></div>')
        self.T(f"tl.fromTo('#{tid}_i',{{opacity:0,scale:0.18}},{{opacity:1,scale:1.15,duration:0.6,ease:'power2.in'}},{f(at)});")
        self.T(f"tl.to('#{tid}_i',{{scale:2.2,opacity:0,duration:0.6,ease:'power1.out'}},{f(at + 0.6)});")
        self.event(at + 0.55, "burst")
        return f"{tid}_p"

    def fade_out(self, at, dur=1.2, color=None):
        self.raw_clip("fadeout_c", at, self.total - at, 300, f'<div id="fadeout" style="position:absolute;inset:0;background:{color or self.th.bg};opacity:0"></div>')
        self.T(f"tl.fromTo('#fadeout',{{opacity:0}},{{opacity:1,duration:{dur},ease:'power1.in'}},{f(at)});")

    # -------------------------------------------------------------- output
    def css(self):
        th = self.th
        faces = "".join(f"@font-face{{font-family:'{fam}';font-weight:{wt};src:url({src})}}" for fam, wt, src in th.font_faces)
        return faces + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{th.bg};font-family:'{th.display}',sans-serif;color:{th.paper}}}
.clip{{position:absolute;inset:0}}
.giant{{position:absolute;left:0;white-space:nowrap;font-family:'{th.display}';font-weight:800;font-size:420px;letter-spacing:-14px;line-height:1;color:transparent;text-transform:uppercase}}
.win{{position:absolute;border-radius:24px;overflow:hidden;background:{th.bg};box-shadow:0 34px 70px rgba(0,0,0,.38),0 0 0 7px rgba(255,255,255,.96)}}
.win .wi{{position:absolute;inset:0;transform-origin:50% 50%}} .win img{{width:100%;height:100%;object-fit:cover;display:block}}
.vframe{{position:absolute;border-radius:30px;background:rgba(255,255,255,.96);box-shadow:0 34px 70px rgba(0,0,0,.38)}}
.vwin{{position:absolute;inset:auto;border-radius:24px;object-fit:cover;background:{th.bg}}}
.pol{{position:absolute;background:#fffdf8;border-radius:6px;box-shadow:0 28px 54px rgba(0,0,0,.36)}}
.pol .pin{{position:absolute;left:16px;top:16px;right:16px;bottom:66px;overflow:hidden;border-radius:2px}} .pol img{{width:100%;height:100%;object-fit:cover;transform-origin:50% 50%}}
.pcap{{position:absolute;left:22px;bottom:18px;font-family:'{th.body}';font-weight:500;font-size:22px;letter-spacing:3px;text-transform:uppercase;color:{th.ink}}}
.tape{{position:absolute;width:150px;height:40px;background:linear-gradient(90deg,rgba(244,226,190,.88),rgba(250,240,215,.78));box-shadow:0 2px 6px rgba(0,0,0,.12);transform:rotate(-4deg)}}
.tagwrap{{position:absolute}}
.tagc{{font-family:'{th.body}';font-weight:500;font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#fff;background:rgba(0,0,0,.55);border-radius:999px;padding:8px 18px;white-space:nowrap}}
.chip{{position:absolute;display:flex;align-items:center;gap:16px;font-family:'{th.body}',sans-serif}}
.cn{{font-family:'{th.display}';font-weight:700;font-size:26px;color:#fff;border-radius:999px;padding:6px 18px;letter-spacing:1px}}
.cl{{font-size:24px;font-weight:500;letter-spacing:5px;text-transform:uppercase}}
.mask{{position:absolute;overflow:hidden;padding:0 8px 14px}}
.step{{font-weight:800;letter-spacing:-5px;line-height:1.04;white-space:nowrap}}
.wb,.lt{{display:inline-block}}
.sub{{position:absolute;font-family:'{th.body}',sans-serif;font-size:40px;font-weight:400;line-height:1.32}}
.sw{{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:4px}} .swi{{display:inline-block}}
.hand{{position:absolute;font-family:'{th.hand}';font-weight:700;white-space:nowrap;line-height:1}}
.stk{{position:absolute;background:#FFFDF6;border-radius:8px;padding:6px 22px 10px;box-shadow:0 14px 30px rgba(0,0,0,.30);white-space:nowrap}}
.stk span{{font-family:'{th.hand}';font-weight:700;line-height:1}}
.stkt{{position:absolute;left:50%;top:-16px;width:96px;height:30px;margin-left:-48px;background:rgba(244,226,190,.85);transform:rotate(3deg)}}
.ov{{position:absolute;inset:0;overflow:visible}} .illo{{position:absolute;overflow:visible}}
.stat{{position:absolute;font-family:'{th.display}'}} .stat .v{{font-size:150px;font-weight:800;letter-spacing:-5px;line-height:1}}
.stat .l{{margin-top:10px;font-family:'{th.body}';font-size:28px;font-weight:500;letter-spacing:4px;text-transform:uppercase}}
.city{{position:absolute;transform:translate(-50%,-100%);font-family:'{th.body}';font-size:22px;font-weight:500;color:{th.paper};white-space:nowrap;text-shadow:0 2px 8px rgba(0,0,0,.8);opacity:0}}
#grain{{position:absolute;inset:-200px;background:url(assets/grain.png);opacity:.06;mix-blend-mode:overlay;pointer-events:none}}
#vig{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 62%,rgba(0,0,0,.26) 100%);pointer-events:none}}
"""

    def write(self, out_path, audio=None, grain=True, extra_css=""):
        """Write index.html (+ events.json for the sound pass). audio = 'assets/mix.wav' to embed the soundtrack."""
        T = self.total
        self.T(f"(function(){{const b={{t:0}}; const fs=document.querySelectorAll('.turb'); tl.fromTo(b,{{t:0}},{{t:{T},duration:{T},ease:'none',onUpdate:function(){{const s=1+Math.floor(b.t*10)%7; for(const q of fs) q.setAttribute('seed',s);}}}},0);}})();")
        if grain:
            self.H.append(f'<div id="fx" class="clip" data-start="0" data-duration="{T}" style="z-index:200;pointer-events:none"><div id="grain"></div><div id="vig"></div></div>')
            self.T(f"tl.fromTo('#grain',{{x:0,y:0}},{{x:-150,y:-110,duration:{T},ease:'steps({int(T * 12)})'}},0);")
            ensure_grain(os.path.join(os.path.dirname(os.path.abspath(out_path)), "assets", "grain.png"))
        self.T("window.__timelines = window.__timelines || {}; window.__timelines['main'] = tl;")
        filters = ('<svg width="0" height="0" style="position:absolute"><defs>'
                   '<filter id="boil" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence class="turb" type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="1" result="n"/>'
                   '<feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/></filter>'
                   '<filter id="boilS" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence class="turb" type="fractalNoise" baseFrequency="0.05" numOctaves="1" seed="3" result="n"/>'
                   '<feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G"/></filter></defs></svg>')
        aud = f'<audio id="music" class="clip" data-start="0" data-duration="{T}" src="{audio}"></audio>' if audio else ""
        scripts = "".join(f'<script src="{s}"></script>' for s in self.scripts)
        html = (f'<!doctype html>\n<html lang="en" data-resolution="landscape">\n<head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">\n'
                f'{scripts}\n<style>{self.css()}{extra_css}</style></head>\n<body>\n'
                f'<div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1920" data-height="1080">\n{filters}\n'
                + "\n".join(self.H) + f"\n{aud}\n</div>\n<script>\n" + "\n".join(self.INIT3D) + "\n" + "\n".join(self.JS) + "\n</script>\n</body></html>")
        with open(out_path, "w") as fh:
            fh.write(html)
        with open(os.path.join(os.path.dirname(os.path.abspath(out_path)), "events.json"), "w") as fh:
            json.dump(sorted(self.events, key=lambda e: e["t"]), fh, indent=1)
        return len(html)


def ensure_grain(path, size=1024, seed=3):
    """Film grain tile (mid-grey noise) used by #grain; generated once."""
    if os.path.exists(path):
        return
    import numpy as np
    from PIL import Image
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rng = np.random.default_rng(seed)
    n = np.clip(128 + rng.normal(0, 38, (size, size)), 0, 255).astype("uint8")
    Image.fromarray(n, "L").convert("RGB").save(path)
