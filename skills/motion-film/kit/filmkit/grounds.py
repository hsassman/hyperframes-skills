"""filmkit.grounds — pre-rendered chapter grounds (gradient + soft colour glows + optional paper tooth).

Rendered to images (2112x1188, 10% oversize so they can drift) instead of stacking CSS gradients and blurred blobs:
HyperFrames lint flags heavy overlay elements, and images render faster and identically everywhere.

    from filmkit.grounds import plate
    plate("assets/gr0.jpg", linear=(135, [(0, "#FFF4E6"), (.5, "#FBE3C8"), (1, "#F6C79A")]),
          glows=[(1100, -200, 1100, "#E8743B", .36), (-300, 600, 900, "#2BA3B8", .2)], paper=.3)
"""
import math
import numpy as np
from PIL import Image, ImageFilter

W, H = 2112, 1188


def _hex(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def _ramp(t, stops):
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1); k = ((t - p0) / max(1e-6, p1 - p0))[..., None]
        out = np.where(m[..., None], _hex(c0) * (1 - k) + _hex(c1) * k, out)
    return out


def plate(path, linear=None, radial=None, glows=(), paper=0.0, seed=5, quality=93):
    """linear=(angle_deg, stops) or radial=(cx, cy, stops) with stops [(pos 0..1, '#hex'), ...];
    glows=[(x, y, diameter, '#hex', alpha)] in 1920x1080 frame coordinates; paper = 0..1 strength of a paper-tooth texture."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if linear:
        a = math.radians(linear[0]); sx, sy = math.sin(a), -math.cos(a)
        t = ((xx - W / 2) * sx + (yy - H / 2) * sy) / (abs(W * sx) + abs(H * sy)) + 0.5
        img = _ramp(np.clip(t, 0, 1), linear[1])
    else:
        cx, cy, stops = radial
        t = np.sqrt(((xx - cx * W) / (W * 0.72)) ** 2 + ((yy - cy * H) / (H * 0.85)) ** 2)
        img = _ramp(np.clip(t, 0, 1), stops)
    ox, oy = (W - 1920) / 2, (H - 1080) / 2
    for (x, y, r, c, al) in glows:
        cxp, cyp = x + r / 2 + ox, y + r / 2 + oy
        d = np.sqrt((xx - cxp) ** 2 + (yy - cyp) ** 2) / (r * 0.48)
        k = (al * np.clip(1 - d, 0, 1) ** 1.2)[..., None]
        img = img * (1 - k) + _hex(c) * k
    if paper:
        rng = np.random.default_rng(seed)
        n = Image.fromarray(np.clip(128 + rng.normal(0, 60, (H // 2, W // 2)), 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2)).resize((W, H))
        tooth = (np.asarray(n, np.float32) / 255.0 - 0.5) * 0.12
        img = img * (1 + tooth[..., None] * paper * 2)
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(path, quality=quality)
    return path
